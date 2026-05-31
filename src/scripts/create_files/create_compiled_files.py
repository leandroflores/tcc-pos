
from pathlib import Path

import json
import os

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

ECONOMIC_2021_FOLDER_PATH: str = "data/process/economic/2021"
ECONOMIC_2022_FOLDER_PATH: str = "data/process/economic/2022"
ECONOMIC_2023_FOLDER_PATH: str = "data/process/economic/2023"
SCHOOL_FOLDER_PATH: str = "data/process/school_by_uf"

OUTPUT_FOLDER_PATH: str = os.path.join("data", "process", "compiled")

def read_records( 
        folder_path: str,
        state_abbr: str,
    ) -> dict:
    
    records: dict = {}

    folder_path: Path = Path(folder_path)
    file_path: Path = Path(os.path.join(folder_path, f"{state_abbr}.json"))

    if not file_path.exists():
        return records
    
    with open(file_path, "r", encoding="utf-8") as file:
        records = json.load(file)

    return records


def create_compiled_data(
        economic_2021_data: dict,
        economic_2022_data: dict,
        economic_2023_data: dict,
        school_data: dict,
) -> dict:
    compiled_data: dict = {}
    EMPTY_VALUE: dict = {}
    for key, value in school_data.items():
        compiled_data[key] = {
            "school": value,
            "economic": {
                "2021": economic_2021_data.get(key, EMPTY_VALUE),
                "2022": economic_2022_data.get(key, EMPTY_VALUE),
                "2023": economic_2023_data.get(key, EMPTY_VALUE),
            }
        }
    return compiled_data

def save_state_file(
        compiled_data: dict,
        state_abbr: str, 
        output_folder: str = OUTPUT_FOLDER_PATH,
    ) -> None:
    
    output_folder: Path = Path(output_folder)
    output_folder.parent.mkdir(parents=True, exist_ok=True)
    output_file_path: Path = Path(os.path.join(output_folder, f"{state_abbr}.json"))

    with open(output_file_path, "w", encoding="utf-8") as file:
        json.dump(
            compiled_data,
            file,
            ensure_ascii=False,
            indent=4,
        )

def create_compiled_data(
        state_abbr: str,
        economic_2021_folder_path: str = ECONOMIC_2021_FOLDER_PATH,
        economic_2022_folder_path: str = ECONOMIC_2022_FOLDER_PATH,
        economic_2023_folder_path: str = ECONOMIC_2023_FOLDER_PATH,
        school_folder_path: str = SCHOOL_FOLDER_PATH,
) -> dict:
    
    economic_2021_data: dict = read_records(
        folder_path=economic_2021_folder_path,
        state_abbr=state_abbr,
    )

    economic_2022_data: dict = read_records(
        folder_path=economic_2022_folder_path,
        state_abbr=state_abbr,
    )

    economic_2023_data: dict = read_records(
        folder_path=economic_2023_folder_path,
        state_abbr=state_abbr,
    )

    school_data: dict = read_records(
        folder_path=school_folder_path,
        state_abbr=state_abbr,
    )

    compiled_data: dict = create_compiled_data(
        economic_2021_data=economic_2021_data,
        economic_2022_data=economic_2022_data,
        economic_2023_data=economic_2023_data,
        school_data=school_data,
    )

    return compiled_data

def create_compiled_files(
        economic_2021_folder_path: str = ECONOMIC_2021_FOLDER_PATH,
        economic_2022_folder_path: str = ECONOMIC_2022_FOLDER_PATH,
        economic_2023_folder_path: str = ECONOMIC_2023_FOLDER_PATH,
        school_folder_path: str = SCHOOL_FOLDER_PATH,
        output_folder_path: str = OUTPUT_FOLDER_PATH,
) -> None:
    for state in BRAZIL_STATES:

        print(f"Creating {state["state_abbr"]} file ...")

        state_abbr: str = state["state_abbr"]

        compiled_data: dict = create_compiled_data(
            state_abbr=state_abbr,
            economic_2021_folder_path=economic_2021_folder_path,
            economic_2022_folder_path=economic_2022_folder_path,
            economic_2023_folder_path=economic_2023_folder_path,
            school_folder_path=school_folder_path,
        )

        save_state_file(
            compiled_data=compiled_data,
            state_abbr=state_abbr,
            output_folder=output_folder_path,
        )

        print("#" * 50)
        print(state_abbr)
        print(len(compiled_data))
        print("#" * 50)



create_compiled_files(
    economic_2021_folder_path=ECONOMIC_2021_FOLDER_PATH,
    economic_2022_folder_path=ECONOMIC_2022_FOLDER_PATH,
    economic_2023_folder_path=ECONOMIC_2023_FOLDER_PATH,
    school_folder_path=SCHOOL_FOLDER_PATH,
    output_folder_path=OUTPUT_FOLDER_PATH,
)