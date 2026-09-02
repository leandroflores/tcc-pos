
from pathlib import Path

import json
import os
import pandas as pd
import re
import unicodedata


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


INPUT_FOLDER_PATH: str = os.path.join("data", "process", "complete")
OUTPUT_FOLDER_PATH: str = os.path.join("data", "process", "csv_complete_data")
SCHOOL_RECORDS_KEY: str = "schoolar"


def import_data(file_path: Path) -> dict:
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def convert_to_float(value) -> float | None:
    if not value:
        return None

    text: str = str(value).strip()

    if text == "" or text.lower() in ["none", "nan", "null"]:
        return None

    try:
        text: str = text.replace(",", ".")
        return float(text)
    except ValueError:
        return None


def normalize_text(value) -> str:
    if not value:
        return ""
    return str(value).strip().lower()

def slugify(value: str | None) -> str:
    
    if not value:
        return "sem_informacao"

    text = str(value).strip().lower()

    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))

    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text)
    text = text.strip("_")

    return text or "sem_informacao"

def extract_municipality_basic_data(
    municipality_code: str,
    municipality_data: dict,
) -> dict:
    return {
        "region_code": municipality_data.get("region_code"),
        "region_name": municipality_data.get("region_name"),
        "state_code": municipality_data.get("state_code"),
        "state_abbr": municipality_data.get("state_abbr"),
        "state_name": municipality_data.get("state_name"),
        "city_code": municipality_data.get("city_code") or municipality_code,
        "city_name": municipality_data.get("city_name"),
    }

def normalize_school_record(
    record: dict,
) -> dict:
    
    return {
        "school_year": record.get("ano"),
        "school_state_code": record.get("id_uf"),
        "school_state_abbr": record.get("sigla_uf"),
        "school_city_code": record.get("id_municipio"),
        "school_city_name": record.get("nome_municipio"),
        "school_network": record.get("rede"),
        "education_level": record.get("ensino"),
        "school_grades": record.get("anos_escolares"),
        "approval_rate": convert_to_float(record.get("taxa_aprovacao")),
        "performance_indicator": convert_to_float(record.get("indicador_rendimento")),
        "saeb_math_score": convert_to_float(record.get("nota_saeb_matematica")),
        "saeb_portuguese_score": convert_to_float(
            record.get("nota_saeb_lingua_portuguesa")
        ),
        "saeb_standardized_average_score": convert_to_float(
            record.get("nota_saeb_media_padronizada")
        ),
        "ideb": convert_to_float(record.get("ideb")),
        "ideb_projection": convert_to_float(record.get("projecao")),
    }

def create_school_record_key(record: dict) -> str:
    network: str = slugify(record.get("rede"))
    education_level: str = slugify(record.get("ensino"))
    school_grades: str = slugify(record.get("anos_escolares"))

    return f"{network}_{education_level}_{school_grades}"

def create_wide_rows_from_state_data(state_data: dict) -> tuple[list[dict], list[dict]]:
    rows: list[dict] = []
    duplicated_records: list[dict] = []

    metrics = {
        "approval_rate": "taxa_aprovacao",
        "performance_indicator": "indicador_rendimento",
        "saeb_math_score": "nota_saeb_matematica",
        "saeb_portuguese_score": "nota_saeb_lingua_portuguesa",
        "saeb_standardized_average_score": "nota_saeb_media_padronizada",
        "ideb": "ideb",
        "ideb_projection": "projecao",
    }

    for municipality_code, municipality_data in state_data.items():
        basic_data: dict = extract_municipality_basic_data(
            municipality_code=municipality_code,
            municipality_data=municipality_data,
        )

        economic_data: dict = extract_economic_data(municipality_data)

        row = {
            **basic_data,
            **economic_data,
            "total_school_records": 0,
            "has_any_school_record": False,
        }

        school_records: list[dict] = municipality_data.get("schoolar", [])

        row["total_school_records"] = len(school_records)
        row["has_any_school_record"] = len(school_records) > 0

        used_keys: set[str] = set()

        for record in school_records:
            key: str = create_school_record_key(record)

            if key in used_keys:
                duplicated_records.append(
                    {
                        "city_code": row["city_code"],
                        "city_name": row["city_name"],
                        "state_abbr": row["state_abbr"],
                        "duplicated_school_record_key": key,
                    }
                )
                continue

            used_keys.add(key)

            for output_metric, source_field in metrics.items():
                column_name = f"{output_metric}_{key}"
                row[column_name] = convert_to_float(record.get(source_field))

        rows.append(row)

    return rows, duplicated_records

def extract_economic_data(municipality_data: dict) -> dict:
    economic_data: dict = municipality_data.get("economic", {})

    if not isinstance(economic_data, dict):
        economic_data: dict = {}

    economic_2021: dict = economic_data.get("2021", {})
    economic_2022: dict = economic_data.get("2022", {})
    economic_2023: dict = economic_data.get("2023", {})

    if not isinstance(economic_2021, dict):
        economic_2021 = {}

    if not isinstance(economic_2022, dict):
        economic_2022 = {}

    if not isinstance(economic_2023, dict):
        economic_2023 = {}

    return {
        
        "gdp_2023_current_prices_thousand_reais": convert_to_float(
            economic_2023.get("gdp")
        ),
        "gdp_per_capita_2023_current_reais": convert_to_float(
            economic_2023.get("gdp_per_capita")
        ),

        
        "gdp_2022_current_prices_thousand_reais": convert_to_float(
            economic_2022.get("gdp")
        ),
        "gdp_per_capita_2022_current_reais": convert_to_float(
            economic_2022.get("gdp_per_capita")
        ),

        
        "gdp_2021_current_prices_thousand_reais": convert_to_float(
            economic_2021.get("gdp_current_prices")
        ),
        "gdp_per_capita_2021_current_reais": convert_to_float(
            economic_2021.get("gdp_per_capita_current")
        ),
        "gross_value_added_agriculture_2021_current_prices_thousand_reais": convert_to_float(
            economic_2021.get("gross_value_added_agriculture_current_prices")
        ),
        "gross_value_added_industry_2021_current_prices_thousand_reais": convert_to_float(
            economic_2021.get("gross_value_added_industry_current_prices")
        ),
        "gross_value_added_services_2021_current_prices_thousand_reais": convert_to_float(
            economic_2021.get("gross_value_added_services_current_prices")
        ),
        "gross_value_added_public_administration_2021_current_prices_thousand_reais": convert_to_float(
            economic_2021.get("gross_value_added_public_administration_current_prices")
        ),
        "gross_value_added_total_2021_current_prices_thousand_reais": convert_to_float(
            economic_2021.get("gross_value_added_total_current_prices")
        ),
        "taxes_less_subsidies_2021_current_prices_thousand_reais": convert_to_float(
            economic_2021.get("taxes_less_subsidies_on_products_current_prices")
        ),
        "main_economic_activity_2021": economic_2021.get(
            "main_economic_activity_by_gross_value_added"
        ),
        "second_main_economic_activity_2021": economic_2021.get(
            "second_main_economic_activity_by_gross_value_added"
        ),
        "third_main_economic_activity_2021": economic_2021.get(
            "third_main_economic_activity_by_gross_value_added"
        ),
    }

def convert_json_to_complete_csv_file(
    state_abbr: str,
    input_folder_path: Path = INPUT_FOLDER_PATH,
    output_folder_path: Path = OUTPUT_FOLDER_PATH,
) -> dict:

    json_file_path: Path = Path(input_folder_path, f"{state_abbr}.json")

    state_data: dict = import_data(json_file_path)

    print("0" * 50)
    print(state_data)
    print("0" * 50)

    
    # state_output_folder = output_folder_path / state_abbr
    # state_output_folder.mkdir(parents=True, exist_ok=True)

    
    wide_rows, duplicated_records = create_wide_rows_from_state_data(state_data)
    wide_dataframe = pd.DataFrame(wide_rows)

    wide_csv_path = Path(output_folder_path, f"{state_abbr}_municipal_summary_wide.csv")

    wide_dataframe.to_csv(
        wide_csv_path,
        index=False,
        sep=";",
        encoding="utf-8-sig",
    )

    # CSV 3: possíveis duplicidades internas
    duplicated_csv_path = Path(output_folder_path, f"{state_abbr}_duplicated_school_records.csv")

    duplicated_dataframe = pd.DataFrame(duplicated_records)

    duplicated_dataframe.to_csv(
        duplicated_csv_path,
        index=False,
        sep=";",
        encoding="utf-8-sig",
    )

    total_municipalities = len(wide_dataframe)
    municipalities_with_school_records = int(
        wide_dataframe["has_any_school_record"].sum()
    )
    municipalities_without_school_records = (
        total_municipalities - municipalities_with_school_records
    )

    print(f"UF processada: {state_abbr}")
    print(f"Municípios: {total_municipalities}")
    print(f"Municípios com dados escolares: {municipalities_with_school_records}")
    print(f"Municípios sem dados escolares: {municipalities_without_school_records}")
    print(f"CSV amplo: {wide_csv_path}")
    print("-" * 80)

    return {
        "state_abbr": state_abbr,
        "total_municipalities": total_municipalities,
        "municipalities_with_school_records": municipalities_with_school_records,
        "municipalities_without_school_records": municipalities_without_school_records,
        "wide_csv_path": str(wide_csv_path),
        "duplicated_records": len(duplicated_records),
        "duplicated_csv_path": str(duplicated_csv_path),
    }

print("0" * 50)
print(BRAZIL_STATES)
print("0" * 50)

for state in BRAZIL_STATES:
    state_abbr: str = state.get("state_abbr")
    convert_json_to_complete_csv_file(state_abbr=state_abbr)
