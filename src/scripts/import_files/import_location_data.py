
from pathlib import Path

import json

INPUT_FILE_PATH: str = "data/process/location.json"

def import_location_data(file_input_path: Path) -> dict:
    
    with open(file_input_path, "r", encoding="utf-8") as file:
        location_data = json.load(file)

    return location_data


def main() -> None:
    
    print("Searching location data JSON file ... ")

    file_input_path: Path = Path(INPUT_FILE_PATH)

    if not file_input_path.exists():
        raise ValueError(f"Import file {INPUT_FILE_PATH} not found.")
    
    print("JSON file exists... ")
    print("")
    print("Importing location data ... ")

    location_data: dict = import_location_data(
        file_input_path=file_input_path,
    )

    print("Location data imported... ")
    print("")
    print(location_data)

    return location_data    

main()
