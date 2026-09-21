
from pathlib import Path
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


import numpy as np
import pandas as pd


DATA_PATH = Path(
    "data/process/csv_complete_data/PR.csv"
)

OUTPUT_DIR = Path("outputs/modeling")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "ideb_random_forest_test_predictions.csv"
)

TARGET_COLUMN = (
    "ideb_publica_medio_todos_1_4"
)

RANDOM_STATE = 42

TEST_SIZE = 0.25


EDUCATIONAL_COLUMNS = [
    "ideb_publica_medio_todos_1_4",
    "saeb_math_score_publica_medio_todos_1_4",
    "saeb_portuguese_score_publica_medio_todos_1_4",
    "approval_rate_publica_medio_todos_1_4",
    "performance_indicator_publica_medio_todos_1_4",
    "saeb_standardized_average_score_publica_medio_todos_1_4",
]


df = pd.read_csv(
    DATA_PATH,
    sep=";",
    encoding="utf-8-sig",
    dtype={"city_code": "string"},
    low_memory=False,
)

print(f"Municípios na base original: {len(df)}")


def convert_numeric(series: pd.Series) -> pd.Series:
    values = series.astype("string").str.strip()

    has_comma = values.str.contains(
        ",",
        regex=False,
        na=False,
    )

    values.loc[has_comma] = (
        values.loc[has_comma]
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )

    return pd.to_numeric(
        values,
        errors="coerce",
    )


required_educational = [
    "city_code",
    *EDUCATIONAL_COLUMNS,
]

missing = [
    column
    for column in required_educational
    if column not in df.columns
]

if missing:
    raise ValueError(
        f"Colunas ausentes: {missing}"
    )

for column in EDUCATIONAL_COLUMNS:
    df[column] = convert_numeric(df[column])


df_valid = df.dropna(
    subset=EDUCATIONAL_COLUMNS
).copy()

print(
    "Municípios com indicadores educacionais válidos:",
    len(df_valid),
)

if len(df_valid) != 387:
    raise ValueError(
        "A amostra não corresponde aos 387 municípios "
        "utilizados no TCC. Confira os dados e o filtro."
    )

if df_valid["city_code"].duplicated().any():
    raise ValueError(
        "Foram encontrados códigos municipais duplicados."
    )


GDP_COLUMNS = [
    "gdp_2023_current_prices_thousand_reais",
    "gdp_per_capita_2023_current_reais",
]

SECTOR_ALIASES = {
    "agriculture": [
        "gva_agriculture_2021_current_prices_thousand_reais",
        "gross_value_added_agriculture_2021_current_prices_thousand_reais",
    ],
    "industry": [
        "gva_industry_2021_current_prices_thousand_reais",
        "gross_value_added_industry_2021_current_prices_thousand_reais",
    ],
    "services": [
        "gva_services_2021_current_prices_thousand_reais",
        "gross_value_added_services_2021_current_prices_thousand_reais",
    ],
    "public_administration": [
        "gva_public_administration_2021_current_prices_thousand_reais",
        "gross_value_added_public_administration_2021_current_prices_thousand_reais",
    ],
}

sector_columns = []

for sector, alternatives in SECTOR_ALIASES.items():
    found = next(
        (
            column
            for column in alternatives
            if column in df_valid.columns
        ),
        None,
    )

    if found is None:
        raise ValueError(
            f"Não encontrei a coluna do VAB de {sector}.\n"
            f"Alternativas procuradas: {alternatives}\n"
            "Confira df.columns.tolist() e ajuste "
            "SECTOR_ALIASES."
        )

    sector_columns.append(found)


CATEGORY_CANDIDATES = [
    "main_economic_activity_2021",
    "primary_economic_activity_2021",
    "predominant_economic_activity_2021",
    "main_economic_activity",
    "primary_economic_activity",
]

category_column = next(
    (
        column
        for column in CATEGORY_CANDIDATES
        if column in df_valid.columns
    ),
    None,
)

if category_column is None:
    print("\nColunas relacionadas a atividade econômica:")

    candidates = [
        column
        for column in df_valid.columns
        if (
            "activity" in column.lower()
            or "atividade" in column.lower()
            or "sector" in column.lower()
            or "setor" in column.lower()
        )
    ]

    print(candidates)

    raise ValueError(
        "A coluna categórica de atividade econômica "
        "não foi identificada. Ajuste "
        "CATEGORY_CANDIDATES com o nome exato "
        "utilizado no script original do TCC."
    )


NUMERIC_COLUMNS = (
    GDP_COLUMNS
    + sector_columns
)

CATEGORICAL_COLUMNS = [
    category_column
]

print("\nVariáveis numéricas:")
print(NUMERIC_COLUMNS)

print("\nVariável categórica:")
print(CATEGORICAL_COLUMNS)


for column in NUMERIC_COLUMNS:
    df_valid[column] = convert_numeric(
        df_valid[column]
    )

df_valid = df_valid.set_index(
    "city_code",
    verify_integrity=True,
)

X = df_valid[
    NUMERIC_COLUMNS
    + CATEGORICAL_COLUMNS
].copy()

y = df_valid[TARGET_COLUMN].copy()


X_train, X_test, y_train, y_test = (
    train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
    )
)

print("\nDivisão da amostra:")
print(f"Treinamento: {len(X_train)} municípios")
print(f"Teste: {len(X_test)} municípios")

if len(X_train) != 290 or len(X_test) != 97:
    raise ValueError(
        "A divisão não corresponde à descrita no TCC."
    )


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
            SimpleImputer(
                strategy="most_frequent"
            ),
        ),
        (
            "encoder",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
        ),
    ]
)

preprocessor = ColumnTransformer(
    transformers=[
        (
            "numeric",
            numeric_transformer,
            NUMERIC_COLUMNS,
        ),
        (
            "categorical",
            categorical_transformer,
            CATEGORICAL_COLUMNS,
        ),
    ]
)


model = Pipeline(
    steps=[
        (
            "preprocessing",
            preprocessor,
        ),
        (
            "regressor",
            RandomForestRegressor(
                n_estimators=300,
                max_depth=6,
                min_samples_leaf=5,
                random_state=RANDOM_STATE,
                n_jobs=-1,
            ),
        ),
    ]
)

model.fit(
    X_train,
    y_train,
)


y_pred = model.predict(
    X_test
)

predictions = pd.DataFrame({
    "city_code": X_test.index.astype(str),
    "ideb_observado": y_test.to_numpy(),
    "ideb_estimado": y_pred,
})

predictions["erro"] = (
    predictions["ideb_estimado"]
    - predictions["ideb_observado"]
)

predictions["erro_absoluto"] = (
    predictions["erro"].abs()
)


mae = mean_absolute_error(
    y_test,
    y_pred,
)

rmse = np.sqrt(
    mean_squared_error(
        y_test,
        y_pred,
    )
)

r2 = r2_score(
    y_test,
    y_pred,
)

print("\nResultados da floresta aleatória — IDEB")
print("-" * 45)

print(f"MAE: {mae:.3f}")
print(f"RMSE: {rmse:.3f}")
print(f"R²: {r2:.3f}")


expected_metrics = {
    "MAE": (mae, 0.236),
    "RMSE": (rmse, 0.306),
    "R²": (r2, 0.035),
}

for name, (obtained, expected) in expected_metrics.items():
    if round(obtained, 3) != expected:
        print(
            f"ATENÇÃO: {name} = {obtained:.3f} "
            f"difere da Tabela 6 ({expected:.3f})."
        )


predictions.to_csv(
    OUTPUT_FILE,
    sep=";",
    decimal=",",
    index=False,
    encoding="utf-8-sig",
)

print(
    "\nArquivo gerado com sucesso:"
)

print(
    OUTPUT_FILE.resolve()
)

print(
    "\nPrimeiras observações:"
)

print(
    predictions.head()
)
