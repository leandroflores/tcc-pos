
from pathlib import Path

import json
import pandas as pd


INPUT_FILE_PATH: str = "data/raw/dtb_2024/RELATORIO_DTB_BRASIL_2024_MUNICIPIOS.xls"
OUTPUT_FILE_PATH: str = "data/process/location.json"

REGION_BY_STATE = {
    "11": {"region_code": "1", "region_name": "Norte"},
    "12": {"region_code": "1", "region_name": "Norte"},
    "13": {"region_code": "1", "region_name": "Norte"},
    "14": {"region_code": "1", "region_name": "Norte"},
    "15": {"region_code": "1", "region_name": "Norte"},
    "16": {"region_code": "1", "region_name": "Norte"},
    "17": {"region_code": "1", "region_name": "Norte"},

    "21": {"region_code": "2", "region_name": "Nordeste"},
    "22": {"region_code": "2", "region_name": "Nordeste"},
    "23": {"region_code": "2", "region_name": "Nordeste"},
    "24": {"region_code": "2", "region_name": "Nordeste"},
    "25": {"region_code": "2", "region_name": "Nordeste"},
    "26": {"region_code": "2", "region_name": "Nordeste"},
    "27": {"region_code": "2", "region_name": "Nordeste"},
    "28": {"region_code": "2", "region_name": "Nordeste"},
    "29": {"region_code": "2", "region_name": "Nordeste"},

    "31": {"region_code": "3", "region_name": "Sudeste"},
    "32": {"region_code": "3", "region_name": "Sudeste"},
    "33": {"region_code": "3", "region_name": "Sudeste"},
    "35": {"region_code": "3", "region_name": "Sudeste"},

    "41": {"region_code": "4", "region_name": "Sul"},
    "42": {"region_code": "4", "region_name": "Sul"},
    "43": {"region_code": "4", "region_name": "Sul"},

    "50": {"region_code": "5", "region_name": "Centro-Oeste"},
    "51": {"region_code": "5", "region_name": "Centro-Oeste"},
    "52": {"region_code": "5", "region_name": "Centro-Oeste"},
    "53": {"region_code": "5", "region_name": "Centro-Oeste"},
}

def load_location(file_path: Path) -> pd.DataFrame:

    header_index = get_header_index(file_path)

    location_data: pd.DataFrame = pd.read_excel(
        file_path,
        header=header_index,
        dtype=str,
        engine="xlrd",
    )

    location_data.columns = location_data.columns.astype(str).str.strip()

    return location_data

def get_header_index(file_path: Path) -> int:

    preview: pd.DataFrame = pd.read_excel(
        file_path,
        header=None,
        dtype=str,
        nrows=30,
        engine="xlrd",
    )

    for index, line in preview.iterrows():
        values = line.astype(str).str.strip().tolist()

        if (
            "Código Município Completo" in values
            and "Nome_Município" in values
            and "UF" in values
            and "Nome_UF" in values
        ):
            return index

    raise ValueError(
        "Header with UF, Nome_UF, Código Município Completo, and Nome_Município not found."
    )

def filter_location(location_dataframe: pd.DataFrame) -> pd.DataFrame:

    columns: list[str] = [
        "UF",
        "Nome_UF",
        "Código Município Completo",
        "Nome_Município",
    ]
    for column in columns:
        if column not in location_dataframe.columns:
            raise ValueError(f"Column {column} not found")

    
    return location_dataframe[columns].copy()

def normalize_location(location_dataframe: pd.DataFrame) -> pd.DataFrame:
    
    location_dataframe: pd.DataFrame = location_dataframe.rename(
        columns={
            "UF": "state_code",
            "Nome_UF": "state_name",
            "Código Município Completo": "city_code",
            "Nome_Município": "city_name",
        }
    )

    location_dataframe["state_code"] = (
        location_dataframe["state_code"]
        .astype(str)
        .str.replace(".0", "", regex=False)
        .str.strip()
        .str.zfill(2)
    )

    location_dataframe["city_code"] = (
        location_dataframe["city_code"]
        .astype(str)
        .str.replace(".0", "", regex=False)
        .str.strip()
        .str.zfill(7)
    )

    location_dataframe["state_name"] = location_dataframe["state_name"].astype(str).str.strip()
    location_dataframe["city_name"] = location_dataframe["city_name"].astype(str).str.strip()

    location_dataframe = location_dataframe.dropna(subset=["city_code"])
    location_dataframe = location_dataframe.drop_duplicates(subset=["city_code"])

    return location_dataframe

def create_location_data(location_dataframe: pd.DataFrame) -> dict:
    location_data: dict = {}

    for _, line in location_dataframe.iterrows():
        state_code = line["state_code"]
        region_data = REGION_BY_STATE.get(
            state_code,
            {
                "region_code": None,
                "region_name": None,
            }
        )

        city_code = line["city_code"]

        location_data[city_code] = {
            "city_code": city_code,
            "city_name": line["city_name"],
            "state_code": state_code,
            "state_name": line["state_name"],
            "region_code": region_data["region_code"],
            "region_name": region_data["region_name"],
        }

    return location_data

def save_location_data(location_data: dict, output_file_path: Path) -> None:

    output_file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file_path, "w", encoding="utf-8") as file:
        json.dump(
            location_data,
            file,
            ensure_ascii=False,
            indent=4,
        )


def main() -> None:
    
    print("Loading location data ... ")

    location_dataframe: pd.DataFrame = load_location(
        file_path=Path(INPUT_FILE_PATH),
    )

    print("Location data loaded... ")
    print("")
    print("Filtering location data ... ")

    location_dataframe: pd.DataFrame = filter_location(
        location_dataframe=location_dataframe,
    )

    print("Location data filtered... ")
    print("")
    print("Normalinzing location data ... ")

    location_dataframe: pd.DataFrame = normalize_location(
        location_dataframe=location_dataframe,
    )

    print("Location data normalized... ")
    print("")
    print("Creating location data ... ")

    location_data: dict = create_location_data(
        location_dataframe=location_dataframe,
    )

    print("Location data created... ")
    print("")
    print("Saving location data ... ")

    save_location_data(
        location_data=location_data,
        output_file_path=Path(OUTPUT_FILE_PATH),
    )

    print("Location data saved... ")

main()
