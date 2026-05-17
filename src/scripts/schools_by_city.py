
import pandas as pd


def load_location_data() -> pd.DataFrame:
    FILE_PATH: str = "data/raw/dtb_2024/RELATORIO_DTB_BRASIL_2024_MUNICIPIOS.xls"

    location_data: pd.DataFrame = pd.read_excel(
        file_path=FILE_PATH,
        encoding="latin1",
        low_memory=False,
    )

    return location_data


def load_data(file_path: str) -> pd.DataFrame:
    

    dataframe: pd.DataFrame = pd.read_csv(
        file_path,
        sep=";",
        encoding="latin1",
        low_memory=False
    )

    return dataframe

def main() -> None:
    
    FILE_PATH: str = "data/raw/microdados_saeb_2023/DADOS/TS_ESCOLA.csv"

    data: pd.DataFrame = load_data(
        file_path=FILE_PATH,
    )

    print("-" * 50)
    print(data)
    print("-" * 50)

    location_data: pd.DataFrame = load_location_data()
    print("+" * 50)
    print(location_data)
    print("+" * 50)

main()
