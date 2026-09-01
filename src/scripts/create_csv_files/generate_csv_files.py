
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


INPUT_FOLDER_PATH: str = os.path.join("data", "process", "complete")
OUTPUT_FOLDER_PATH: str = os.path.join("data", "process", "csv_complete")

TARGET_YEAR: str = "2023"
TARGET_NETWORK: str = "publica"
TARGET_EDUCATION_LEVEL: str = "medio"
TARGET_SCHOOL_GRADES: str = "todos (1-4)"

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

def find_educational_record(educational_records: list[dict]) -> dict | None:
    for record in educational_records:
        if (
            normalize_text(record.get("ano")) == TARGET_YEAR
            and normalize_text(record.get("rede")) == TARGET_NETWORK
            and normalize_text(record.get("ensino")) == TARGET_EDUCATION_LEVEL
            and normalize_text(record.get("anos_escolares")) == TARGET_SCHOOL_GRADES
        ):
            return record
    return None

def create_row_from_municipality(
    municipality_code: str,
    municipality_data: dict,
) -> dict:
    educational_records: list[dict] = municipality_data.get("schoolar", [])
    
    educational_record: dict | None = find_educational_record(educational_records)

    economic_data: dict = municipality_data.get("economic", {})

    if not isinstance(economic_data, dict):
        economic_data = {}

    economic_2023 = economic_data.get("2023", {})
    economic_2022 = economic_data.get("2022", {})
    economic_2021 = economic_data.get("2021", {})

    if not isinstance(economic_2023, dict):
        economic_2023 = {}

    if not isinstance(economic_2022, dict):
        economic_2022 = {}

    if not isinstance(economic_2021, dict):
        economic_2021 = {}

    row = {
        "region_code": municipality_data.get("region_code"),
        "region_name": municipality_data.get("region_name"),
        "state_code": municipality_data.get("state_code"),
        "state_abbr": municipality_data.get("state_abbr"),
        "state_name": municipality_data.get("state_name"),
        "city_code": municipality_data.get("city_code") or municipality_code,
        "city_name": municipality_data.get("city_name"),

        "has_educational_record": educational_record is not None,
        "school_year": None,
        "school_network": None,
        "education_level": None,
        "school_grades": None,

        "approval_rate": None,
        "performance_indicator": None,
        "saeb_math_score": None,
        "saeb_portuguese_score": None,
        "saeb_standardized_average_score": None,
        "ideb": None,
        "ideb_projection": None,

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

    if educational_record is not None:
        row.update(
            {
                "school_year": educational_record.get("ano"),
                "school_network": educational_record.get("rede"),
                "education_level": educational_record.get("ensino"),
                "school_grades": educational_record.get("anos_escolares"),
                "approval_rate": convert_to_float(
                    educational_record.get("taxa_aprovacao")
                ),
                "performance_indicator": convert_to_float(
                    educational_record.get("indicador_rendimento")
                ),
                "saeb_math_score": convert_to_float(
                    educational_record.get("nota_saeb_matematica")
                ),
                "saeb_portuguese_score": convert_to_float(
                    educational_record.get("nota_saeb_lingua_portuguesa")
                ),
                "saeb_standardized_average_score": convert_to_float(
                    educational_record.get("nota_saeb_media_padronizada")
                ),
                "ideb": convert_to_float(
                    educational_record.get("ideb")
                ),
                "ideb_projection": convert_to_float(
                    educational_record.get("projecao")
                ),
            }
        )

    return row

def convert_state_json_to_csv(
    state_abbr: str,
    input_folder_path: Path = Path(INPUT_FOLDER_PATH),
    output_folder_path: Path = Path(OUTPUT_FOLDER_PATH),
) -> dict:

    json_file_path: Path = Path(input_folder_path, f"{state_abbr}.json")

    state_data: dict = import_data(json_file_path)

    rows: list[dict] = []

    for municipality_code, municipality_data in state_data.items():
        row = create_row_from_municipality(
            municipality_code=municipality_code,
            municipality_data=municipality_data,
        )

        rows.append(row)

    dataframe = pd.DataFrame(rows)

    output_file_path: Path = Path(output_folder_path, f"{state_abbr}.csv")

    output_folder_path.mkdir(parents=True, exist_ok=True)

    dataframe.to_csv(
        output_file_path,
        index=False,
        sep=";",
        encoding="utf-8-sig",
    )

    total_municipalities = len(dataframe)
    municipalities_with_educational_record = int(dataframe["has_educational_record"].sum())
    municipalities_without_educational_record = (
        total_municipalities - municipalities_with_educational_record
    )

    print(f"CSV gerado: {output_file_path}")
    print(f"UF: {state_abbr}")
    print(f"Municípios: {total_municipalities}")
    print(f"Com registro educacional do recorte: {municipalities_with_educational_record}")
    print(f"Sem registro educacional do recorte: {municipalities_without_educational_record}")
    print("-" * 60)

    return {
        "state_abbr": state_abbr,
        "csv_file": str(output_file_path),
        "total_municipalities": total_municipalities,
        "municipalities_with_educational_record": municipalities_with_educational_record,
        "municipalities_without_educational_record": municipalities_without_educational_record,
    }


print("0" * 50)
print(BRAZIL_STATES)
print("0" * 50)

for state in BRAZIL_STATES:
    state_abbr: str = state.get("state_abbr")
    convert_state_json_to_csv(state_abbr=state_abbr)
