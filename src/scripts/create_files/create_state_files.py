
from pathlib import Path

import json
import pandas as pd

from src.scripts.import_files import import_location_data

FILE_PATH: str = "data/raw/microdados_saeb_2023/DADOS/TS_ESCOLA.csv"
INPUT_FILE_PATH: str = "data/raw/dtb_2024/RELATORIO_DTB_BRASIL_2024_MUNICIPIOS.xls"
OUTPUT_FILE_PATH: str = "data/process/states"



def load_school_data(file_path: str = FILE_PATH) -> pd.DataFrame:
    
    dataframe: pd.DataFrame = pd.read_csv(
        file_path,
        sep=";",
        encoding="latin1",
        low_memory=False
    )

    return dataframe

def filter_school_data(dataframe: pd.DataFrame) -> pd.DataFrame:
    SCHOOL_COLUNMS: list[str] = [
        "ID_REGIAO",
        "ID_UF",
        "ID_MUNICIPIO",
        "ID_ESCOLA",
        "IN_PUBLICA",
        "ID_LOCALIZACAO",
        "NU_MATRICULADOS_CENSO_EM",
        "NU_PRESENTES_EM",
        "MEDIA_EM_LP",
        "MEDIA_EM_MT",
    ]
    for column in SCHOOL_COLUNMS:
        if column not in dataframe.columns:
            raise ValueError(f"Column {column} not found")
        
    return dataframe[SCHOOL_COLUNMS].copy()

def normalize_school_data(dataframe: pd.DataFrame) -> pd.DataFrame:
    dataframe: pd.DataFrame = dataframe.copy()
    if "ID_UF" not in dataframe.columns:
        raise ValueError("Column 'ID_UF' not found.")

    if "ID_MUNICIPIO" not in dataframe.columns:
        raise ValueError("Column 'ID_MUNICIPIO' not found.")
    
    dataframe: pd.DataFrame = dataframe.rename(
        columns={
            "ID_REGIAO": "region_code",
            "ID_UF": "state_code",
            "ID_MUNICIPIO": "city_code",
            "ID_ESCOLA": "school_code",
            "IN_PUBLICA": "public_school",
            "ID_LOCALIZACAO": "location_code",
            "NU_MATRICULADOS_CENSO_EM": "number_of_students",
            "NU_PRESENTES_EM": "number_of_present_students",
            "MEDIA_EM_LP": "portuguese_average",
            "MEDIA_EM_MT": "math_average",
        }
    )
    dataframe["state_code"] = dataframe["state_code"].astype(str).str.replace(".0", "", regex=False).str.zfill(2)
    dataframe["city_code"] = (
        dataframe["city_code"]
        .astype(str)
        .str.replace(".0", "", regex=False)
        .str.zfill(7)
    )

    return dataframe

def get_location_data() -> dict:
    LOCATION_FILE_PATH: str = "data/process/location.json"

    return import_location_data.import_location_data(
        file_path=LOCATION_FILE_PATH,
    )

def create_state_school_data(
        input_file_path: str = INPUT_FILE_PATH,
) -> None:
    
    try:
        print("Loading location data ... ")

        school_dataframe: pd.DataFrame = load_school_data(
            file_path=input_file_path,
        )

        print("Location data loaded... ")
        print("")
        print("Filtering location data ... ")

        school_dataframe: pd.DataFrame = filter_school_data(
            dataframe=school_dataframe,
        )

        print("Location data filtered... ")
        print("")
        print("Normalinzing location data ... ")

        school_dataframe: pd.DataFrame = normalize_school_data(
            dataframe=school_dataframe,
        )

        print("Location data normalized... ")
        print("")
        print("Creating location data ... ")

        location_data: dict = get_location_data()

        print("Location data created... ")
        print("")
        print(location_data)
        print("Saving location data ... ")

        
        return True
    
    except Exception:
    
        return False

create_state_school_data()
