
from pathlib import Path
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    mean_absolute_error, 
    mean_squared_error, 
    r2_score,
)
from sklearn.model_selection import (
    KFold, 
    cross_val_score, 
    train_test_split,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeRegressor

import numpy as np
import os
import pandas as pd



CSV_FOLDER_PATH: Path = Path("data", "process", "csv_complete_data")

EDUCATIONAL_FILTER = [
    "ideb_publica_medio_todos_1_4",
    "saeb_math_score_publica_medio_todos_1_4",
    "saeb_portuguese_score_publica_medio_todos_1_4",
    "approval_rate_publica_medio_todos_1_4",
    "performance_indicator_publica_medio_todos_1_4",
    "saeb_standardized_average_score_publica_medio_todos_1_4",
]

TARGETS = {
    "IDEB": "ideb_publica_medio_todos_1_4",
    "SAEB Matemática": "saeb_math_score_publica_medio_todos_1_4",
    "SAEB Língua Portuguesa": "saeb_portuguese_score_publica_medio_todos_1_4",
}

NUMERIC_FEATURES = [
    "gdp_2023_current_prices_thousand_reais",
    "gdp_per_capita_2023_current_reais",
    "gross_value_added_agriculture_2021_current_prices_thousand_reais",
    "gross_value_added_industry_2021_current_prices_thousand_reais",
    "gross_value_added_services_2021_current_prices_thousand_reais",
    "gross_value_added_public_administration_2021_current_prices_thousand_reais",
]
CATEGORICAL_FEATURES = ["main_economic_activity_2021"]

def convert_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(
        series.astype("string").str.strip().str.replace(",", ".", regex=False),
        errors="coerce",
    )

def create_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("numeric", SimpleImputer(strategy="median"), NUMERIC_FEATURES),
            (
                "categorical",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                CATEGORICAL_FEATURES,
            ),
        ]
    )


def create_models() -> dict:
    return {
        "Árvore de decisão": DecisionTreeRegressor(
            max_depth=4, min_samples_leaf=10, random_state=42
        ),
        "Floresta aleatória": RandomForestRegressor(
            n_estimators=300,
            max_depth=6,
            min_samples_leaf=5,
            random_state=42,
            n_jobs=-1,
        ),
    }


def main() -> None:

    CSV_PATH: str = os.path.join(CSV_FOLDER_PATH, "PR.csv")
    data = pd.read_csv(CSV_PATH, sep=";", encoding="utf-8-sig", dtype={"city_code": "string"})
    required = ["city_code", "city_name", *EDUCATIONAL_FILTER, *NUMERIC_FEATURES, *CATEGORICAL_FEATURES]
    missing = [col for col in required if col not in data.columns]
    if missing:
        raise ValueError(
            "O arquivo deve estar em formato amplo (uma linha por município). "
            f"Colunas ausentes: {missing}"
        )
    if data["city_code"].duplicated().any():
        raise ValueError("Há municípios duplicados no CSV de origem.")

    for column in dict.fromkeys([*EDUCATIONAL_FILTER, *NUMERIC_FEATURES]):
        data[column] = convert_numeric(data[column])

    valid = data.dropna(subset=EDUCATIONAL_FILTER).copy()
    economic_missing = valid[NUMERIC_FEATURES + CATEGORICAL_FEATURES].isna().sum()
    if economic_missing.any():
        raise ValueError(f"Há variáveis econômicas ausentes na amostra:\n{economic_missing}")
    if len(valid) != 387:
        print(f"ATENÇÃO: sua versão do arquivo tem {len(valid)} municípios válidos, não 387.")
    print(f"Municípios no CSV: {len(data)} | Válidos: {len(valid)}")

    print("1" * 50)

    X = valid[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    train_idx, test_idx = train_test_split(
        np.arange(len(valid)), test_size=0.25, random_state=42
    )
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    print(f"Treino: {len(X_train)} | Teste: {len(X_test)}")
    cv = KFold(n_splits=5, shuffle=True, random_state=42)
    metrics_rows = []
    prediction_rows = []
    importance_rows = []

    for outcome, target_column in TARGETS.items():
        y = valid[target_column]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        baseline = DummyRegressor(strategy="mean")
        baseline.fit(X_train, y_train)
        baseline_pred = baseline.predict(X_test)
        print(f"\n{outcome} — referência da média: MAE={mean_absolute_error(y_test, baseline_pred):.3f}; R²={r2_score(y_test, baseline_pred):.3f}")

        for name, regressor in create_models().items():
            pipeline = Pipeline(
                steps=[("preprocessor", create_preprocessor()), ("regressor", regressor)]
            )
            pipeline.fit(X_train, y_train)
            predictions = pipeline.predict(X_test)
            fold_scores = cross_val_score(
                pipeline, X, y, cv=cv, scoring="r2", n_jobs=1
            )
            metrics_rows.append(
                {
                    "Variável-alvo": outcome,
                    "Modelo": name,
                    "n": len(valid),
                    "Treino": len(y_train),
                    "Teste": len(y_test),
                    "MAE": mean_absolute_error(y_test, predictions),
                    "RMSE": np.sqrt(mean_squared_error(y_test, predictions)),
                    "R²": r2_score(y_test, predictions),
                    "R² CV (média 5 folds)": fold_scores.mean(),
                }
            )
            for idx, predicted in zip(test_idx, predictions):
                prediction_rows.append(
                    {
                        "Município": valid.iloc[idx]["city_name"],
                        "Código IBGE": valid.iloc[idx]["city_code"],
                        "Variável-alvo": outcome,
                        "Modelo": name,
                        "Real": float(y.iloc[idx]),
                        "Estimado": float(predicted),
                        "Erro absoluto": abs(float(y.iloc[idx]) - float(predicted)),
                    }
                )

            feature_names = pipeline.named_steps["preprocessor"].get_feature_names_out()
            for feature, importance in zip(
                feature_names, pipeline.named_steps["regressor"].feature_importances_
            ):
                importance_rows.append(
                    {
                        "Variável-alvo": outcome,
                        "Modelo": name,
                        "Variável": feature,
                        "Importância": float(importance),
                    }
                )

    metrics = pd.DataFrame(metrics_rows)
    print("0" * 40)
    print("\nTABELA 5 — RESULTADOS (valores não arredondados nos arquivos)")
    print(metrics.round(3).to_string(index=False))

main()