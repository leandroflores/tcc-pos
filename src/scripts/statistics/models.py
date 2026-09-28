from pathlib import Path

import numpy as np
import pandas as pd

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


# ============================================================
# CONFIGURAÇÕES GERAIS
# ============================================================

RANDOM_STATE = 42
TEST_SIZE = 0.25
N_SPLITS_CV = 5
EXPECTED_MUNICIPALITIES = 387

CSV_PATH = Path(
    "data",
    "process",
    "csv_complete_data",
    "PR.csv",
)

OUTPUT_DIR = Path("outputs", "modeling")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# VARIÁVEIS EDUCACIONAIS
# ============================================================

# Os seis indicadores precisam estar válidos para que o município
# faça parte da amostra analítica utilizada no TCC.
EDUCATIONAL_FILTER = [
    "ideb_publica_medio_todos_1_4",
    "saeb_math_score_publica_medio_todos_1_4",
    "saeb_portuguese_score_publica_medio_todos_1_4",
    "approval_rate_publica_medio_todos_1_4",
    "performance_indicator_publica_medio_todos_1_4",
    "saeb_standardized_average_score_publica_medio_todos_1_4",
]


# Variáveis dependentes dos modelos.
TARGETS = {
    "IDEB": "ideb_publica_medio_todos_1_4",
    "SAEB Matemática": "saeb_math_score_publica_medio_todos_1_4",
    "SAEB Língua Portuguesa": (
        "saeb_portuguese_score_publica_medio_todos_1_4"
    ),
}


# ============================================================
# VARIÁVEIS ECONÔMICAS EXPLICATIVAS
# ============================================================

NUMERIC_FEATURES = [
    "gdp_2023_current_prices_thousand_reais",
    "gdp_per_capita_2023_current_reais",
    "gross_value_added_agriculture_2021_current_prices_thousand_reais",
    "gross_value_added_industry_2021_current_prices_thousand_reais",
    "gross_value_added_services_2021_current_prices_thousand_reais",
    "gross_value_added_public_administration_2021_current_prices_thousand_reais",
]

CATEGORICAL_FEATURES = [
    "main_economic_activity_2021",
]


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def convert_numeric(series: pd.Series) -> pd.Series:
    """
    Converte uma coluna para formato numérico.

    Trata tanto números no formato:
        1234.56

    quanto:
        1234,56
    """

    values = series.astype("string").str.strip()

    has_comma = values.str.contains(
        ",",
        regex=False,
        na=False,
    )

    # Quando há vírgula, assume formato brasileiro.
    # Ex.: 1.234,56 -> 1234.56
    values.loc[has_comma] = (
        values.loc[has_comma]
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )

    return pd.to_numeric(
        values,
        errors="coerce",
    )


def create_preprocessor() -> ColumnTransformer:
    """
    Cria o pipeline de pré-processamento.

    Variáveis numéricas:
        - imputação pela mediana, caso necessário.

    Variável categórica:
        - imputação pela categoria mais frequente;
        - codificação one-hot.
    """

    numeric_transformer = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="median"),
            ),
        ]
    )

    categorical_transformer = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="most_frequent"),
            ),
            (
                "onehot",
                OneHotEncoder(
                    handle_unknown="ignore",
                ),
            ),
        ]
    )

    return ColumnTransformer(
        transformers=[
            (
                "numeric",
                numeric_transformer,
                NUMERIC_FEATURES,
            ),
            (
                "categorical",
                categorical_transformer,
                CATEGORICAL_FEATURES,
            ),
        ]
    )


def create_models() -> dict:
    """
    Cria novas instâncias dos dois algoritmos utilizados no TCC.
    """

    return {
        "Árvore de decisão": DecisionTreeRegressor(
            max_depth=4,
            min_samples_leaf=10,
            random_state=RANDOM_STATE,
        ),
        "Floresta aleatória": RandomForestRegressor(
            n_estimators=300,
            max_depth=6,
            min_samples_leaf=5,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
    }


# ============================================================
# EXECUÇÃO PRINCIPAL
# ============================================================

def main() -> None:

    # --------------------------------------------------------
    # 1. LEITURA DOS DADOS
    # --------------------------------------------------------

    data = pd.read_csv(
        CSV_PATH,
        sep=";",
        encoding="utf-8-sig",
        dtype={"city_code": "string"},
        low_memory=False,
    )

    print("=" * 70)
    print("MODELAGEM DOS INDICADORES EDUCACIONAIS")
    print("=" * 70)

    print(f"\nArquivo: {CSV_PATH}")
    print(f"Municípios no CSV original: {len(data)}")


    # --------------------------------------------------------
    # 2. VALIDAÇÃO DAS COLUNAS
    # --------------------------------------------------------

    required_columns = [
        "city_code",
        "city_name",
        *EDUCATIONAL_FILTER,
        *NUMERIC_FEATURES,
        *CATEGORICAL_FEATURES,
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            "O arquivo deve estar em formato amplo "
            "(uma linha por município).\n"
            f"Colunas ausentes: {missing_columns}"
        )

    if data["city_code"].duplicated().any():
        raise ValueError(
            "Foram encontrados códigos municipais duplicados."
        )


    # --------------------------------------------------------
    # 3. CONVERSÃO DAS VARIÁVEIS NUMÉRICAS
    # --------------------------------------------------------

    numeric_columns_to_convert = list(
        dict.fromkeys(
            [
                *EDUCATIONAL_FILTER,
                *NUMERIC_FEATURES,
            ]
        )
    )

    for column in numeric_columns_to_convert:
        data[column] = convert_numeric(
            data[column]
        )


    # --------------------------------------------------------
    # 4. DEFINIÇÃO DA AMOSTRA ANALÍTICA
    # --------------------------------------------------------

    # Um município somente entra na análise quando possui
    # valores válidos nos seis indicadores educacionais.
    valid = data.dropna(
        subset=EDUCATIONAL_FILTER
    ).copy()

    print(
        f"Municípios com os seis indicadores "
        f"educacionais válidos: {len(valid)}"
    )

    if len(valid) != EXPECTED_MUNICIPALITIES:
        raise ValueError(
            f"A amostra contém {len(valid)} municípios, "
            f"mas o TCC utiliza {EXPECTED_MUNICIPALITIES}."
        )


    # --------------------------------------------------------
    # 5. VERIFICAÇÃO DAS VARIÁVEIS ECONÔMICAS
    # --------------------------------------------------------

    economic_missing = valid[
        NUMERIC_FEATURES + CATEGORICAL_FEATURES
    ].isna().sum()

    print("\nValores econômicos ausentes:")
    print(economic_missing.to_string())

    # No conjunto utilizado no TCC espera-se que não haja
    # valores econômicos ausentes.
    if economic_missing.any():
        raise ValueError(
            "\nForam encontrados valores econômicos "
            "ausentes na amostra analítica.\n"
            f"{economic_missing}"
        )


    # --------------------------------------------------------
    # 6. MATRIZ DE VARIÁVEIS EXPLICATIVAS
    # --------------------------------------------------------

    X = valid[
        NUMERIC_FEATURES
        + CATEGORICAL_FEATURES
    ].copy()


    # --------------------------------------------------------
    # 7. DIVISÃO ÚNICA TREINAMENTO / TESTE
    # --------------------------------------------------------

    # Utilizamos os índices para garantir exatamente os mesmos
    # municípios nos conjuntos de treinamento e teste para
    # IDEB, Matemática e Língua Portuguesa.
    train_idx, test_idx = train_test_split(
        np.arange(len(valid)),
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
    )

    X_train = X.iloc[train_idx]
    X_test = X.iloc[test_idx]

    print("\nDivisão da amostra:")
    print(f"Treinamento: {len(X_train)} municípios")
    print(f"Teste:       {len(X_test)} municípios")

    if len(X_train) != 290 or len(X_test) != 97:
        raise ValueError(
            "A divisão não corresponde aos "
            "290 municípios de treinamento e "
            "97 municípios de teste descritos no TCC."
        )


    # --------------------------------------------------------
    # 8. CONFIGURAÇÃO DA VALIDAÇÃO CRUZADA
    # --------------------------------------------------------

    # ATENÇÃO:
    # A validação cruzada será executada somente nos
    # 290 municípios do conjunto de treinamento.
    #
    # Os 97 municípios de teste não participam da CV.
    cv = KFold(
        n_splits=N_SPLITS_CV,
        shuffle=True,
        random_state=RANDOM_STATE,
    )


    # Estruturas para salvar resultados.
    metrics_rows = []
    prediction_rows = []
    importance_rows = []
    cv_rows = []


    # --------------------------------------------------------
    # 9. MODELAGEM DE CADA VARIÁVEL-ALVO
    # --------------------------------------------------------

    for outcome, target_column in TARGETS.items():

        print("\n" + "=" * 70)
        print(f"VARIÁVEL-ALVO: {outcome}")
        print("=" * 70)

        y = valid[target_column]

        y_train = y.iloc[train_idx]
        y_test = y.iloc[test_idx]


        # ----------------------------------------------------
        # 9.1 BASELINE — MÉDIA DO TREINAMENTO
        # ----------------------------------------------------

        baseline = DummyRegressor(
            strategy="mean"
        )

        baseline.fit(
            np.zeros((len(y_train), 1)),
            y_train,
        )

        baseline_pred = baseline.predict(
            np.zeros((len(y_test), 1))
        )

        baseline_mae = mean_absolute_error(
            y_test,
            baseline_pred,
        )

        baseline_r2 = r2_score(
            y_test,
            baseline_pred,
        )

        print(
            "\nReferência pela média do treinamento:"
        )
        print(f"MAE: {baseline_mae:.3f}")
        print(f"R²:  {baseline_r2:.3f}")


        # ----------------------------------------------------
        # 9.2 ÁRVORE E FLORESTA ALEATÓRIA
        # ----------------------------------------------------

        for model_name, regressor in create_models().items():

            print(
                f"\n--- {model_name} ---"
            )

            pipeline = Pipeline(
                steps=[
                    (
                        "preprocessor",
                        create_preprocessor(),
                    ),
                    (
                        "regressor",
                        regressor,
                    ),
                ]
            )


            # ------------------------------------------------
            # 9.2.1 VALIDAÇÃO CRUZADA — SOMENTE TREINAMENTO
            # ------------------------------------------------

            fold_scores = cross_val_score(
                estimator=pipeline,
                X=X_train,
                y=y_train,
                cv=cv,
                scoring="r2",
                n_jobs=1,
            )

            cv_mean = fold_scores.mean()
            cv_std = fold_scores.std(ddof=1)

            print(
                "R² CV por partição:",
                np.round(fold_scores, 3),
            )
            print(
                f"R² CV médio: {cv_mean:.3f}"
            )
            print(
                f"R² CV desvio-padrão: {cv_std:.3f}"
            )

            for fold_number, fold_score in enumerate(
                fold_scores,
                start=1,
            ):
                cv_rows.append(
                    {
                        "Variável-alvo": outcome,
                        "Modelo": model_name,
                        "Partição": fold_number,
                        "R²": float(fold_score),
                    }
                )


            # ------------------------------------------------
            # 9.2.2 AJUSTE FINAL NOS 290 MUNICÍPIOS
            # ------------------------------------------------

            pipeline.fit(
                X_train,
                y_train,
            )


            # ------------------------------------------------
            # 9.2.3 AVALIAÇÃO FINAL NOS 97 MUNICÍPIOS
            # ------------------------------------------------

            predictions = pipeline.predict(
                X_test
            )

            mae = mean_absolute_error(
                y_test,
                predictions,
            )

            rmse = np.sqrt(
                mean_squared_error(
                    y_test,
                    predictions,
                )
            )

            r2 = r2_score(
                y_test,
                predictions,
            )

            print("\nAvaliação final — conjunto de teste:")
            print(f"MAE:  {mae:.3f}")
            print(f"RMSE: {rmse:.3f}")
            print(f"R²:   {r2:.3f}")


            # ------------------------------------------------
            # 9.2.4 MÉTRICAS CONSOLIDADAS
            # ------------------------------------------------

            metrics_rows.append(
                {
                    "Variável-alvo": outcome,
                    "Modelo": model_name,
                    "n": len(valid),
                    "Treino": len(y_train),
                    "Teste": len(y_test),
                    "MAE": mae,
                    "RMSE": rmse,
                    "R² teste": r2,
                    "R² CV médio": cv_mean,
                    "R² CV desvio-padrão": cv_std,
                }
            )


            # ------------------------------------------------
            # 9.2.5 PREVISÕES DOS 97 MUNICÍPIOS
            # ------------------------------------------------

            for idx, predicted in zip(
                test_idx,
                predictions,
            ):
                observed = float(
                    y.iloc[idx]
                )

                predicted = float(
                    predicted
                )

                prediction_rows.append(
                    {
                        "Município": valid.iloc[idx][
                            "city_name"
                        ],
                        "Código IBGE": valid.iloc[idx][
                            "city_code"
                        ],
                        "Variável-alvo": outcome,
                        "Modelo": model_name,
                        "Real": observed,
                        "Estimado": predicted,
                        "Erro": predicted - observed,
                        "Erro absoluto": abs(
                            predicted - observed
                        ),
                    }
                )


            # ------------------------------------------------
            # 9.2.6 IMPORTÂNCIA DAS VARIÁVEIS
            # ------------------------------------------------

            feature_names = (
                pipeline
                .named_steps["preprocessor"]
                .get_feature_names_out()
            )

            feature_importances = (
                pipeline
                .named_steps["regressor"]
                .feature_importances_
            )

            for feature, importance in zip(
                feature_names,
                feature_importances,
            ):
                importance_rows.append(
                    {
                        "Variável-alvo": outcome,
                        "Modelo": model_name,
                        "Variável": feature,
                        "Importância": float(importance),
                    }
                )


    # ========================================================
    # 10. CONSOLIDAÇÃO DOS RESULTADOS
    # ========================================================

    metrics = pd.DataFrame(
        metrics_rows
    )

    predictions_df = pd.DataFrame(
        prediction_rows
    )

    importance_df = pd.DataFrame(
        importance_rows
    )

    cv_df = pd.DataFrame(
        cv_rows
    )


    # ========================================================
    # 11. EXIBIÇÃO DA TABELA 6
    # ========================================================

    print("\n" + "=" * 90)
    print("TABELA 6 — RESULTADOS DOS MODELOS")
    print("=" * 90)

    print(
        metrics.round(3).to_string(
            index=False
        )
    )


    # ========================================================
    # 12. SALVAMENTO DOS RESULTADOS
    # ========================================================

    metrics.to_csv(
        OUTPUT_DIR / "model_metrics.csv",
        sep=";",
        decimal=",",
        index=False,
        encoding="utf-8-sig",
    )

    predictions_df.to_csv(
        OUTPUT_DIR / "model_predictions.csv",
        sep=";",
        decimal=",",
        index=False,
        encoding="utf-8-sig",
    )

    importance_df.to_csv(
        OUTPUT_DIR / "model_feature_importances.csv",
        sep=";",
        decimal=",",
        index=False,
        encoding="utf-8-sig",
    )

    cv_df.to_csv(
        OUTPUT_DIR / "model_cross_validation.csv",
        sep=";",
        decimal=",",
        index=False,
        encoding="utf-8-sig",
    )


    print("\nArquivos gerados:")

    print(
        OUTPUT_DIR / "model_metrics.csv"
    )
    print(
        OUTPUT_DIR / "model_predictions.csv"
    )
    print(
        OUTPUT_DIR / "model_feature_importances.csv"
    )
    print(
        OUTPUT_DIR / "model_cross_validation.csv"
    )


if __name__ == "__main__":
    main()