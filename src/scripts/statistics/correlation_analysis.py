
from pathlib import Path

import pandas as pd

CSV_FOLDER_PATH: Path = Path("data", "process", "csv_complete_data")

ECONOMIC_COLUMNS = {

    "PIB municipal 2023":
        "gdp_2023_current_prices_thousand_reais",

    "PIB per capita 2023":
        "gdp_per_capita_2023_current_reais",

    "VAB agropecuária 2021":
        "gross_value_added_agriculture_2021_current_prices_thousand_reais",

    "VAB indústria 2021":
        "gross_value_added_industry_2021_current_prices_thousand_reais",

    "VAB serviços 2021":
        "gross_value_added_services_2021_current_prices_thousand_reais",

    "VAB administração pública 2021":
        "gross_value_added_public_administration_2021_current_prices_thousand_reais",

}

EDUCATIONAL_ANALYSIS_COLUMNS = {

    "IDEB":
        "ideb_publica_medio_todos_1_4",

    "SAEB Matemática":
        "saeb_math_score_publica_medio_todos_1_4",

    "SAEB Língua Portuguesa":
        "saeb_portuguese_score_publica_medio_todos_1_4",

}

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

def convert_numeric_columns(
    dataframe: pd.DataFrame,
    columns: list[str],
) -> pd.DataFrame:

    dataframe = dataframe.copy()

    for column in columns:

        dataframe[column] = pd.to_numeric(
            dataframe[column]
            .astype("string")
            .str.strip()
            .str.replace(",", ".", regex=False),
            errors="coerce",
        )

    return dataframe


def format_brazilian_number(
    value: float,
    decimal_places: int = 2,
) -> str:

    formatted_value = f"{value:,.{decimal_places}f}"

    return (
        formatted_value
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


print("0" * 50)

state_data = load_data("PR")
state_data: pd.DataFrame = load_data("PR")

print()
print("CARACTERIZAÇÃO DA BASE")
print("-" * 80)

print(
    f"Municípios na base original: {len(state_data)}"
)

required_columns = [
    "city_code",
    "city_name",
    *EDUCATIONAL_COLUMNS.values(),
    *ECONOMIC_COLUMNS.values(),
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

columns_to_convert = [
    *EDUCATIONAL_COLUMNS.values(),
    *ECONOMIC_COLUMNS.values(),
]

state_data = convert_numeric_columns(
    state_data,
    columns_to_convert,
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


print(
    f"Municípios na base: {total_municipalities}"
)

print(
    f"Municípios com dados educacionais válidos: "
    f"{valid_municipalities}"
)

print(
    f"Municípios excluídos: {excluded_municipalities}"
)

excluded_data = state_data.loc[
    ~state_data.index.isin(state_valid_data.index),
    [
        "city_code",
        "city_name",
    ],
].copy()


print()
print("MUNICÍPIOS SEM DADOS EDUCACIONAIS VÁLIDOS")
print("-" * 80)

print(
    excluded_data.to_string(index=False)
)

economic_missing = state_valid_data[
    list(ECONOMIC_COLUMNS.values())
].isna().sum()

print()
print("VALORES ECONÔMICOS AUSENTES")
print("-" * 80)

print(economic_missing)

if economic_missing.any():

    raise ValueError(
        "Existem municípios com dados educacionais válidos, "
        "mas com indicadores econômicos ausentes. "
        "Verifique a base antes de continuar."
    )


economic_column_names = list(
    ECONOMIC_COLUMNS.values()
)

educational_column_names = list(
    EDUCATIONAL_ANALYSIS_COLUMNS.values()
)

correlation_results: list = []

for economic_name, economic_column in ECONOMIC_COLUMNS.items():

    statistics = {
        "Variável econômica": economic_name,
    }

    for educational_name, educational_column in (
        EDUCATIONAL_ANALYSIS_COLUMNS.items()
    ):

        correlation = state_valid_data[
            economic_column
        ].corr(
            state_valid_data[educational_column],
            method="pearson",
        )

        statistics[educational_name] = correlation

    correlation_results.append(statistics)

table: pd.DataFrame = pd.DataFrame(
    correlation_results
)
formatted_table: pd.DataFrame = table.copy()

for column in EDUCATIONAL_ANALYSIS_COLUMNS.keys():

    formatted_table[column] = [
        format_brazilian_number(
            value,
            decimal_places=3,
        )
        for value in table[column]
    ]



print()
print("TABELA 4 - CORRELAÇÃO DE PEARSON")
print("-" * 100)

print(
    formatted_table.to_string(index=False)
)