
import pandas as pd



def load_data(file_path: str) -> pd.DataFrame:
    

    dataframe: pd.DataFrame = pd.read_csv(
        file_path,
        sep=";",
        encoding="latin1",
        low_memory=False
    )

    return dataframe

def main() -> None:
    
    FILE_PATH: str = "../data/raw/microdados_saeb_2023/DADOS/TS_ESCOLA.csv"

    data: pd.DataFrame = load_data(
        file_path=FILE_PATH,
    )

    print("-" * 50)
    print(data)
    print("-" * 50)

main()
