

from pathlib import Path

import json
import os
import pandas as pd

BRAZIL_STATES: list[dict] = [
    {"state_abbr": "AC", "state_code": "12", "state_name": "Acre"},
    {"state_abbr": "AL", "state_code": "27", "state_name": "Alagoas"},
    {"state_abbr": "AP", "state_code": "16", "state_name": "Amapá"},
    {"state_abbr": "AM", "state_code": "13", "state_name": "Amazonas"},
    {"state_abbr": "BA", "state_code": "29", "state_name": "Bahia"},
    {"state_abbr": "CE", "state_code": "23", "state_name": "Ceará"},
    {"state_abbr": "DF", "state_code": "53", "state_name": "Distrito Federal"},
    {"state_abbr": "ES", "state_code": "32", "state_name": "Espírito Santo"},
    {"state_abbr": "GO", "state_code": "52", "state_name": "Goiás"},
    {"state_abbr": "MA", "state_code": "21", "state_name": "Maranhão"},
    {"state_abbr": "MT", "state_code": "51", "state_name": "Mato Grosso"},
    {"state_abbr": "MS", "state_code": "50", "state_name": "Mato Grosso do Sul"},
    {"state_abbr": "MG", "state_code": "31", "state_name": "Minas Gerais"},
    {"state_abbr": "PA", "state_code": "15", "state_name": "Pará"},
    {"state_abbr": "PB", "state_code": "25", "state_name": "Paraíba"},
    {"state_abbr": "PR", "state_code": "41", "state_name": "Paraná"},
    {"state_abbr": "PE", "state_code": "26", "state_name": "Pernambuco"},
    {"state_abbr": "PI", "state_code": "22", "state_name": "Piauí"},
    {"state_abbr": "RJ", "state_code": "33", "state_name": "Rio de Janeiro"},
    {"state_abbr": "RN", "state_code": "24", "state_name": "Rio Grande do Norte"},
    {"state_abbr": "RS", "state_code": "43", "state_name": "Rio Grande do Sul"},
    {"state_abbr": "RO", "state_code": "11", "state_name": "Rondônia"},
    {"state_abbr": "RR", "state_code": "14", "state_name": "Roraima"},
    {"state_abbr": "SC", "state_code": "42", "state_name": "Santa Catarina"},
    {"state_abbr": "SP", "state_code": "35", "state_name": "São Paulo"},
    {"state_abbr": "SE", "state_code": "28", "state_name": "Sergipe"},
    {"state_abbr": "TO", "state_code": "17", "state_name": "Tocantins"},
]

COLUMN_MAPPING: dict = {
    "Ano": "year",

    "Código da Grande Região": "region_code",
    "Nome da Grande Região": "region_name",

    "Código da Unidade da Federação": "state_code",
    "Sigla da Unidade da Federação": "state_abbr",
    "Nome da Unidade da Federação": "state_name",

    "Código do Município": "city_code",
    "Nome do Município": "city_name",

    "Região Metropolitana": "metropolitan_region",
    "Código da Mesorregião": "mesoregion_code",
    "Nome da Mesorregião": "mesoregion_name",
    "Código da Microrregião": "microregion_code",
    "Nome da Microrregião": "microregion_name",
}

NUMERIC_COLUMNS: list[str] = [
    "gross_value_added_agriculture_current_prices",
    "gross_value_added_industry_current_prices",
    "gross_value_added_services_current_prices",
    "gross_value_added_public_administration_current_prices",
    "gross_value_added_total_current_prices",
    "taxes_less_subsidies_on_products_current_prices",
    "gdp_current_prices",
    "gdp_per_capita_current_prices",
]

ECONOMIC_FILE_PATH: str = os.path.join("data", "raw", "economico", "PIB dos Municípios - base de dados 2010-2023.xlsx")

REFERENCE_YEAR: str = "2023"
OUTPUT_FOLDER_PATH: str = os.path.join("data", "process", "economic", REFERENCE_YEAR)


def load_economic_data(
        economic_file_path: str = ECONOMIC_FILE_PATH,
        year: str = REFERENCE_YEAR,
) -> pd.DataFrame:
    dataframe = pd.read_excel(
        economic_file_path,
        engine="openpyxl",
        dtype=str,
    )
    dataframe: pd.DataFrame = dataframe.rename(
        columns=COLUMN_MAPPING,
    )

    economic_data: pd.DataFrame = (
        dataframe[dataframe["year"].astype(str).str.strip() == year].copy()
    )

    print(f"{economic_data.shape[0]} lines x {economic_data.shape[1]} columns")

    return economic_data

def clean_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    dataframe = dataframe.copy()

    dataframe.columns = (
        dataframe.columns
        .astype(str)
        .str.replace("\n", " ", regex=False)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    return dataframe

def normalize_code_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    dataframe: pd.DataFrame = dataframe.copy()

    if "year" in dataframe.columns:
        dataframe["year"] = (
            dataframe["year"]
            .astype(str)
            .str.strip()
            .str.replace(r"\.0$", "", regex=True)
        )

    if "region_code" in dataframe.columns:
        dataframe["region_code"] = (
            dataframe["region_code"]
            .astype(str)
            .str.strip()
            .str.replace(r"\.0$", "", regex=True)
        )

    if "state_code" in dataframe.columns:
        dataframe["state_code"] = (
            dataframe["state_code"]
            .astype(str)
            .str.strip()
            .str.replace(r"\.0$", "", regex=True)
            .str.zfill(2)
        )

    if "city_code" in dataframe.columns:
        dataframe["city_code"] = (
            dataframe["city_code"]
            .astype(str)
            .str.strip()
            .str.replace(r"\.0$", "", regex=True)
            .str.zfill(7)
        )

    return dataframe



def filter_economic_data_by_state(
        economic_dataframe: pd.DataFrame,
        state_abbr: str,
) -> pd.DataFrame:
    
    economic_data_by_state: pd.DataFrame = (
        economic_dataframe[
            economic_dataframe["state_abbr"].astype(str).str.strip() == state_abbr
        ].copy()
    )

    return economic_data_by_state

def convert_brazilian_number(value) -> float | None:
    
    if pd.isna(value):
        return None

    text = str(value).strip()
    if text in ["", "-", "nan", "NaN", "None"]:
        return None

    try:
        if "," in text:
            text = text.replace(".", "").replace(",", ".")

        return float(text)
    except ValueError:
        return None

def convert_numeric_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    dataframe = dataframe.copy()

    for column in NUMERIC_COLUMNS:
        if column not in dataframe.columns:
            continue

        dataframe[column] = dataframe[column].apply(
            convert_brazilian_number
        )

    return dataframe

def create_economic_data_by_state(
        dataframe: pd.DataFrame,
) -> dict:
    dataframe: pd.DataFrame = dataframe.copy()

    economic_data: dict = {}
    for _, row in dataframe.iterrows():
        city_code: str = row["city_code"]
        economic_data[city_code] = {
            "year": row.get("year"),
            "region_code": row.get("region_code"),
            "region_name": row.get("region_name"),
            "state_code": row.get("state_code"),
            "state_abbr": row.get("state_abbr"),
            "state_name": row.get("state_name"),
            "city_code": row.get("city_code"),
            "city_name": row.get("city_name"),

            
            # "gross_value_added_agriculture_current_prices": row.get(
            #     "Valor Agricultura"
            # ),
            # "gross_value_added_industry_current_prices": row.get(
            #     "Valor Industria"
            # ),
            # "gross_value_added_services_current_prices": row.get(
            #     "Valor Serviços"
            # ),
            # "gross_value_added_public_administration_current_prices": row.get(
            #     "Valor Administração"
            # ),
            # "gross_value_added_total_current_prices": row.get(
            #     "Valor bruto total"
            # ),
            # "taxes_less_subsidies_on_products_current_prices": row.get(
            #     "Impostos Liquidos"
            # ),
            "gdp": row.get(
                "Produto Interno Bruto"
            ),
            "gdp_per_capita": row.get(
                "Produto Interno Bruto per capita"
            ),

            # "main_economic_activity_by_gross_value_added": row.get(
            #     "Atividade 1"
            # ),
            # "second_main_economic_activity_by_gross_value_added": row.get(
            #     "Atividade 2"
            # ),
            # "third_main_economic_activity_by_gross_value_added": row.get(
            #     "Atividade 3"
            # ),
        }

    return economic_data

def save_state_file(
        economic_data: dict,
        state_abbr: str, 
        output_folder: str = OUTPUT_FOLDER_PATH,
    ) -> None:
    
    output_folder: Path = Path(output_folder)
    output_folder.parent.mkdir(parents=True, exist_ok=True)
    output_file_path: Path = Path(os.path.join(output_folder, f"{state_abbr}.json"))

    with open(output_file_path, "w", encoding="utf-8") as file:
        json.dump(
            economic_data,
            file,
            ensure_ascii=False,
            indent=4,
        )

    print(f"Saving JSON file: {output_folder}")




def import_economic_data(
        economic_file_path=ECONOMIC_FILE_PATH,
        year=REFERENCE_YEAR,
) -> None:
    
    economic_dataframe: pd.DataFrame = load_economic_data(
        economic_file_path=economic_file_path,
        year=year,
    )
    
    for state in BRAZIL_STATES:

        print(f"Creating {state["state_abbr"]} file ...")

        state_abbr: str = state["state_abbr"]

        economic_dataframe_by_state: pd.DataFrame = filter_economic_data_by_state(
            economic_dataframe=economic_dataframe,
            state_abbr=state_abbr,
        )

        economic_dataframe_by_state: pd.DataFrame = normalize_code_columns(
            dataframe=economic_dataframe_by_state,
        )

        # economic_dataframe: pd.DataFrame = convert_numeric_columns(
        #    dataframe=economic_dataframe,
        #)
        
        economic_data: dict = create_economic_data_by_state(
            dataframe=economic_dataframe_by_state,
        )

        save_state_file(
            economic_data=economic_data,
            state_abbr=state_abbr,
            output_folder=OUTPUT_FOLDER_PATH,
        )


import_economic_data(
    economic_file_path=ECONOMIC_FILE_PATH,
    year=REFERENCE_YEAR,
)