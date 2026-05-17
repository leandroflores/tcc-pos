
from pathlib import Path

import json

INPUT_FILE_PATH: str = "data/process/location.json"

def read_location_data(input_file_path: Path) -> dict:
    
    with open(input_file_path, "r", encoding="utf-8") as file:
        location_data = json.load(file)

    return location_data


def import_location_data(
        file_path: str = INPUT_FILE_PATH,
) -> dict:
    
    file_input_path: Path = Path(file_path)

    if not file_input_path.exists():
        raise FileNotFoundError(f"Import file {file_path} not found.")

    location_data: dict = read_location_data(
        input_file_path=file_input_path,
    )

    return location_data    

import_location_data()
