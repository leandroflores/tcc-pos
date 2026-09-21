
from pathlib import Path

import os
import pandas as pd

CSV_FOLDER_PATH: Path = Path("data", "process", "csv_complete_data")

EDUCATIONAL_COLUMNS = {

    "IDEB":
        "ideb_publica_medio_todos_1_4",

    "SAEB Matemática":
        "saeb_math_score_publica_medio_todos_1_4",

    "SAEB Língua Portuguesa":
        "saeb_portuguese_score_publica_medio_todos_1_4",

    "Taxa de aprovação (%)":
        "approval_rate_publica_medio_todos_1_4",

    "Indicador de rendimento":
        "performance_indicator_publica_medio_todos_1_4",

    "Nota média padronizada do SAEB":
        "saeb_standardized_average_score_publica_medio_todos_1_4",

}


THREE_DECIMAL_INDICATORS = {
    "Indicador de rendimento",
}

def load_data(
    state_abbr: str = "PR",
    folder_path: Path = CSV_FOLDER_PATH,
) -> pd.DataFrame:

    file_path: Path = folder_path / f"{state_abbr}.csv"
    dataframe = pd.read_csv(
        file_path,
        sep=";",
        encoding="utf-8-sig",
        dtype={
            "city_code": "string",
        },
    )

    return dataframe



print("0" * 50)

state_data = load_data("PR")
print(state_data)
print(state_data.columns)

print(f"Municípios na base original: {len(state_data)}")

required_columns = [
    "city_code",
    "city_name",
    *EDUCATIONAL_COLUMNS.values(),
]

missing_columns = [
    column
    for column in required_columns
    if column not in state_data.columns
]

if missing_columns:
    raise ValueError(
        f"Colunas não encontradas: {missing_columns}"
    )

for column in EDUCATIONAL_COLUMNS.values():

    state_data[column] = pd.to_numeric(
        state_data[column]
        .astype("string")
        .str.strip()
        .str.replace(",", ".", regex=False),
        errors="coerce",
    )

state_valid_data: pd.DataFrame = state_data.dropna(
    subset=list(EDUCATIONAL_COLUMNS.values())
).copy()

if state_valid_data["city_code"].duplicated().any():

    duplicated = state_valid_data.loc[
        state_valid_data["city_code"].duplicated(),
        ["city_code", "city_name"],
    ]

    raise ValueError(
        f"Municípios duplicados encontrados:\n{duplicated}"
    )

total_municipalities: int = len(state_data)
valid_municipalities: int = len(state_valid_data)
excluded_municipalities: int = (
    total_municipalities - valid_municipalities
)


print()
print("CARACTERIZAÇÃO DA BASE")
print("-" * 50)

print(
    f"Municípios na base: {total_municipalities}"
)

print(
    f"Municípios válidos: {valid_municipalities}"
)

print(
    f"Municípios sem dados completos: "
    f"{excluded_municipalities}"
)

results: list = []

for indicator_name, column in EDUCATIONAL_COLUMNS.items():

    values = state_valid_data[column]

    statistics = {

        "Indicador": indicator_name,

        "n": values.count(),

        "Média": values.mean(),

        "Mediana": values.median(),

        "Desvio-padrão": values.std(ddof=1),

        "Mínimo": values.min(),

        "Máximo": values.max(),

    }

    results.append(statistics)

table: pd.DataFrame = pd.DataFrame(results)
formatted_table: pd.DataFrame = table.copy()

print("1" * 50)

numeric_columns: list[str] = [
    "Média",
    "Mediana",
    "Desvio-padrão",
    "Mínimo",
    "Máximo",
]
for column in numeric_columns:

    formatted_table[column] = [
        (
            f"{value:.3f}".replace(".", ",")
            if indicator == "Indicador de rendimento"
            else f"{value:.2f}".replace(".", ",")
        )
        for indicator, value in zip(
            table["Indicador"],
            table[column],
        )
    ]



print()
print("TABELA 2 - ESTATÍSTICA DESCRITIVA")
print("-" * 80)

print(
    formatted_table.to_string(index=False)
)
