
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
FOLDER_PATH: str = os.path.join("data", "process", "uf")
LOCATION_FILE_PATH: str = os.path.join("data", "process", "location.json")

def read_location_data(location_file_path: Path) -> dict:
    
    with open(location_file_path, "r", encoding="utf-8") as file:
        location_data = json.load(file)

    return location_data


def import_location_data(
        file_path: str = LOCATION_FILE_PATH,
) -> dict:
    
    file_location_path: Path = Path(file_path)

    if not file_location_path.exists():
        raise FileNotFoundError(f"Import file {file_path} not found.")

    location_data: dict = read_location_data(
        location_file_path=file_location_path,
    )

    return location_data    

def filter_state_records(
        location_data: dict,
        state_abbr: str,
        state_code: str,
) -> dict:
    state_records: list[dict] = []
    for _, record in location_data.items():
        if record["state_code"] == state_code:
            state_records.append(
                {
                    "city_code": record.get("city_code", None),
                    "city_name": record.get("city_name", None),
                    "region_code": record.get("region_code", None),
                    "region_name": record.get("region_name", None),
                    "state_abbr": state_abbr,
                    "state_code": record.get("state_code", None),
                    "state_name": record.get("state_name", None),
                }
            )
    return state_records

def create_state_file(
        state_abbr: str,
        state_data: dict, 
        folder_path: str = FOLDER_PATH,
) -> None:
    
    file_path: str = os.path.join(folder_path, f"{state_abbr}.json")
    state_file_path: Path = Path(file_path)

    state_file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(state_file_path, "w", encoding="utf-8") as file:
        json.dump(
            state_data,
            file,
            ensure_ascii=False,
            indent=4,
        )


def create_state_files(
        folder_path: str = FOLDER_PATH,
        location_file_path: str = LOCATION_FILE_PATH,
) -> None:
    
    location_data: dict = import_location_data(
        file_path=location_file_path,
    )

    print("0" * 50)
    print(location_data)
    print("0" * 50)

    for state in BRAZIL_STATES:
        print(f"Creating {state} file ...")

        state_data: dict = filter_state_records(
            location_data=location_data,
            state_abbr=state["state_abbr"],
            state_code=state["state_code"],
        )

        print("1" * 50)
        print(state_data)
        print("1" * 50)

        create_state_file(
            state_abbr=state["state_abbr"],
            state_data=state_data,
            folder_path=folder_path,
        )

create_state_files(
    folder_path=FOLDER_PATH,
    location_file_path=LOCATION_FILE_PATH,
)
