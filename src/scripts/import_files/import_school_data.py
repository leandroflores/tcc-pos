

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

OUTPUT_FOLDER_PATH: str = os.path.join("data", "process", "school_by_uf")
SCHOOL_FILE_PATH: str = os.path.join("data", "raw", "microdados_saeb_2023", "DADOS", "TS_ESCOLA.csv")


def load_school_data(
        school_file_path: str = SCHOOL_FILE_PATH
) -> pd.DataFrame:
    dataframe = pd.read_csv(
        school_file_path,
        sep=";",
        encoding="latin1",
        low_memory=False,
    )

    print(f"Base carregada: {dataframe.shape[0]} linhas x {dataframe.shape[1]} colunas")

    return dataframe

def normalize_location_codes(
        dataframe: pd.DataFrame,
) -> pd.DataFrame:
    
    dataframe = dataframe.copy()

    dataframe["ID_UF"] = (
        dataframe["ID_UF"]
        .astype(str)
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
        .str.zfill(2)
    )

    dataframe["ID_MUNICIPIO"] = (
        dataframe["ID_MUNICIPIO"]
        .astype(str)
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
        .str.zfill(7)
    )

    return dataframe

def convert_numeric_columns(
        dataframe: pd.DataFrame,
) -> pd.DataFrame:
    NUMERIC_COLUMNS: list[str] = [
        "NU_PRESENTES_EM",
        "MEDIA_EM_LP",
        "MEDIA_EM_MT",
    ]
    
    dataframe: pd.DataFrame = dataframe.copy()
    for column in NUMERIC_COLUMNS:
        if column not in dataframe.columns:
            raise ValueError(f"Column {column} does not exists on dataframe.")

        dataframe[column] = (
            dataframe[column]
            .astype(str)
            .str.strip()
            .str.replace(",", ".", regex=False)
        )

        dataframe[column] = pd.to_numeric(
            dataframe[column],
            errors="coerce",
        )

    return dataframe

def weighted_average(
        values: pd.Series, 
        weights: pd.Series,
) -> float | None:
    valid_data: pd.DataFrame = pd.DataFrame(
        {
            "value": values,
            "weight": weights,
        }
    ).dropna()

    valid_data: pd.DataFrame = valid_data[valid_data["weight"] > 0]

    if valid_data.empty:
        return None

    return (
        valid_data["value"] * valid_data["weight"]
    ).sum() / valid_data["weight"].sum()

def create_school_data_by_location(
        school_dataframe: pd.DataFrame,
) -> pd.DataFrame:
    columns: list[str] = [
        "ID_UF",
        "ID_MUNICIPIO",
        "ID_ESCOLA",
        "NU_PRESENTES_EM",
        "MEDIA_EM_LP",
        "MEDIA_EM_MT",
    ]

    for column in columns:
        if column not in school_dataframe.columns:
            raise ValueError(f"Column {column} does not exists.")

        
    school_dataframe: pd.DataFrame = school_dataframe[columns].copy()
    school_dataframe = school_dataframe[
        school_dataframe["MEDIA_EM_LP"].notna()
        | school_dataframe["MEDIA_EM_MT"].notna()
    ].copy()

    school_data_by_location: pd.DataFrame = (
        school_dataframe
        .groupby(["ID_UF", "ID_MUNICIPIO"])
        .apply(
            lambda group: pd.Series(
                {
                    "qtd_escolas": group["ID_ESCOLA"].nunique(),
                    "total_presentes_em": group["NU_PRESENTES_EM"].sum(),
                    "media_lp_simples": group["MEDIA_EM_LP"].mean(),
                    "media_mt_simples": group["MEDIA_EM_MT"].mean(),
                    "media_lp_ponderada": weighted_average(
                        group["MEDIA_EM_LP"],
                        group["NU_PRESENTES_EM"],
                    ),
                    "media_mt_ponderada": weighted_average(
                        group["MEDIA_EM_MT"],
                        group["NU_PRESENTES_EM"],
                    ),
                }
            ),
            include_groups=False,
        )
        .reset_index()
    )

    school_data_by_location: pd.DataFrame = school_data_by_location.sort_values(
        ["ID_UF", "ID_MUNICIPIO"]
    )

    return school_data_by_location

def create_school_data_by_state(
    school_dataframe: pd.DataFrame,
    state_code: str,
) -> dict:
    
    dataframe: pd.DataFrame = school_dataframe.copy()
    dataframe: pd.DataFrame = dataframe[dataframe["ID_UF"] == state_code].copy()

    school_data_by_state = {}
    for _, row in dataframe.iterrows():
        city_code: str = row["ID_MUNICIPIO"]

        school_data_by_state[city_code] = {
            "city_code": city_code,
            "state_code": row["ID_UF"],
            "number_of_schools": int(row["qtd_escolas"]) if pd.notna(row["qtd_escolas"]) else None,
            "number_of_students": float(row["total_presentes_em"]) if pd.notna(row["total_presentes_em"]) else None,
            "simple_portuguese_average": float(row["media_lp_simples"]) if pd.notna(row["media_lp_simples"]) else None,
            "simple_math_average": float(row["media_mt_simples"]) if pd.notna(row["media_mt_simples"]) else None,
            "weighted_portuguese_average": float(row["media_lp_ponderada"]) if pd.notna(row["media_lp_ponderada"]) else None,
            "weighted_math_average": float(row["media_mt_ponderada"]) if pd.notna(row["media_mt_ponderada"]) else None,
        }

    return school_data_by_state

def save_state_file(
        school_data: dict,
        state_attr: str, 
        output_folder: str = OUTPUT_FOLDER_PATH,
    ) -> None:
    
    output_folder: Path = Path(output_folder)
    output_folder.parent.mkdir(parents=True, exist_ok=True)
    output_file_path: Path = Path(os.path.join(output_folder, f"{state_attr}.json"))

    with open(output_file_path, "w", encoding="utf-8") as file:
        json.dump(
            school_data,
            file,
            ensure_ascii=False,
            indent=4,
        )

    print(f"Saving JSON file: {output_folder}")

def import_school_data(
        school_file_path=SCHOOL_FILE_PATH,
) -> None:
    
    school_data: pd.DataFrame = load_school_data(
        school_file_path=school_file_path,
    )

    school_data: pd.DataFrame = normalize_location_codes(
        dataframe=school_data,
    )
    print("1" * 50)
    print(f"{school_data.shape[0]} lines x {school_data.shape[1]} columns")
    print("1" * 50)

    school_data: pd.DataFrame = convert_numeric_columns(
        dataframe=school_data,
    )
    print("2" * 50)
    print(f"{school_data.shape[0]} lines x {school_data.shape[1]} columns")
    print("2" * 50)

    school_data_by_location: pd.DataFrame = create_school_data_by_location(
        school_dataframe=school_data,
    )
    print("3" * 50)
    print(type(school_data_by_location))
    print(school_data_by_location)
    print(f"{school_data_by_location.shape[0]} lines x {school_data_by_location.shape[1]} columns")
    print("3" * 50)

    for state in BRAZIL_STATES:
        print(f"Creating {state} file ...")

        state_abbr: str = state["state_abbr"]
        state_code: str = state["state_code"]

        school_data: dict = create_school_data_by_state(
            school_dataframe=school_data_by_location,
            state_code=state_code,
        )

        save_state_file(
            school_data=school_data,
            state_attr=state_abbr,
            output_folder=OUTPUT_FOLDER_PATH,
        )


import_school_data(
    school_file_path=SCHOOL_FILE_PATH,
)