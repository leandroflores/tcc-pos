
import basedosdados as bd
import json
import os

from pathlib import Path

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

PROJECT_ID = "tcc-pos-498101"
OUTPUT_FOLDER_PATH: str = os.path.join("data", "process", "schoolar_complete")

for state in BRAZIL_STATES:

    state_abbr: str = state["state_abbr"]
    state_code: str = state["state_code"]

    file_path: str = os.path.join(OUTPUT_FOLDER_PATH, f"{state_abbr}.json")
    output_file_path: Path = Path(file_path)

    query = f"""
    SELECT
    ideb.ano,
    SUBSTR(CAST(ideb.id_municipio AS STRING), 1, 2) AS id_uf,
    municipio.sigla_uf,
    ideb.id_municipio,
    municipio.nome AS nome_municipio,
    ideb.rede,
    ideb.ensino,
    ideb.anos_escolares,
    ideb.taxa_aprovacao,
    ideb.indicador_rendimento,
    ideb.nota_saeb_matematica,
    ideb.nota_saeb_lingua_portuguesa,
    ideb.nota_saeb_media_padronizada,
    ideb.ideb,
    ideb.projecao
    FROM `basedosdados.br_inep_ideb.municipio` AS ideb
    LEFT JOIN `basedosdados.br_bd_diretorios_brasil.municipio` AS municipio
    ON ideb.id_municipio = municipio.id_municipio
    WHERE ideb.ano = 2023
    AND ideb.id_municipio IS NOT NULL
    AND SUBSTR(CAST(ideb.id_municipio AS STRING), 1, 2) = "{state_code}"
    """

    df = bd.read_sql(
        query,
        billing_project_id=PROJECT_ID
    )

    print(df)

    df["ano"] = df["ano"].astype(str)
    df["id_uf"] = df["id_uf"].astype(str).str.zfill(2)
    df["id_municipio"] = df["id_municipio"].astype(str).str.zfill(7)

    df = df.where(df.notna(), "None")

    records = df.to_dict(orient="records")

    with open(output_file_path, "w", encoding="utf-8") as file:
        json.dump(records, file, ensure_ascii=False, indent=4)

    print(f"Arquivo salvo em: {output_file_path}")

