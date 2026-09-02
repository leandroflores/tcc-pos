
from pathlib import Path

import os
import pandas as pd

CSV_FOLDER_PATH: Path = Path("data", "process", "csv_complete_data")

def load_data(
    state_abbr: str,
    folder_path: Path = CSV_FOLDER_PATH,
) -> pd.DataFrame:

    file_path: Path = folder_path / f"{state_abbr}.csv"
    dataframe = pd.read_csv(
        file_path,
        sep=";",
        encoding="utf-8-sig"
    )

    return dataframe

def prepare_analysis_dataframe(
    dataframe: pd.DataFrame,
    target_column: str,
) -> pd.DataFrame:

    dataframe: pd.DataFrame = dataframe.copy()

    dataframe[target_column] = pd.to_numeric(
        dataframe[target_column],
        errors="coerce"
    )

    analysis_dataframe: pd.DataFrame = dataframe.dropna(
        subset=[target_column]
    ).copy()

    print(f"Total de municípios no arquivo: {len(dataframe)}")
    print(f"Municípios com IDEB Ensino Médio público: {len(analysis_dataframe)}")

    return analysis_dataframe

print("0" * 50)

state_data = load_data("PR")
print(state_data)
print(state_data.columns)



ideb_columns: list[str] = [
    "ideb_publica_medio_todos_1_4",
    "ideb_estadual_medio_todos_1_4",
    "ideb_federal_medio_todos_1_4",

    "ideb_municipal_fundamental_finais_6_9",
    "ideb_estadual_fundamental_finais_6_9",
    "ideb_publica_fundamental_finais_6_9",
    "ideb_federal_fundamental_finais_6_9",

    "ideb_municipal_fundamental_iniciais_1_5",
    "ideb_publica_fundamental_iniciais_1_5",
    "ideb_estadual_fundamental_iniciais_1_5",
    
]

# analysis_dataframe = prepare_analysis_dataframe(state_data, "ideb_publica_medio_todos_1_4")

for column in ideb_columns:
    analysis_dataframe = prepare_analysis_dataframe(state_data, column)
    
    print("-" * 50)
    print(column)
    print("-" * 50)
    print(analysis_dataframe)
    print("-" * 50)

