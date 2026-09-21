
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


DATA_PATH = Path("data/process/csv_complete_data/PR.csv")

OUTPUT_DIR = Path("outputs/figures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = OUTPUT_DIR / "figura_3_distribuicao_ideb_pr_2023.png"

IDEB_COLUMN = "ideb_publica_medio_todos_1_4"

EDUCATIONAL_COLUMNS = [
    "ideb_publica_medio_todos_1_4",
    "saeb_math_score_publica_medio_todos_1_4",
    "saeb_portuguese_score_publica_medio_todos_1_4",
    "approval_rate_publica_medio_todos_1_4",
    "performance_indicator_publica_medio_todos_1_4",
    "saeb_standardized_average_score_publica_medio_todos_1_4",
]


df = pd.read_csv(
    DATA_PATH,
    sep=";",
    encoding="utf-8-sig",
    dtype={"city_code": "string"},
    low_memory=False,
)

missing_columns = [
    column
    for column in EDUCATIONAL_COLUMNS
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Colunas não encontradas no arquivo: {missing_columns}"
    )


def convert_numeric(series: pd.Series) -> pd.Series:

    values = series.astype("string").str.strip()
    has_comma = values.str.contains(",", regex=False, na=False)

    values.loc[has_comma] = (
        values.loc[has_comma]
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )

    return pd.to_numeric(values, errors="coerce")


for column in EDUCATIONAL_COLUMNS:
    df[column] = convert_numeric(df[column])


df_valid = df.dropna(
    subset=EDUCATIONAL_COLUMNS
).copy()

if df_valid["city_code"].duplicated().any():
    duplicates = df_valid.loc[
        df_valid["city_code"].duplicated(keep=False),
        "city_code",
    ].tolist()

    raise ValueError(
        "Foram encontrados municípios duplicados: "
        f"{duplicates}"
    )

ideb = df_valid[IDEB_COLUMN]


n = len(ideb)

mean = ideb.mean()
median = ideb.median()
std = ideb.std(ddof=1)

minimum = ideb.min()
maximum = ideb.max()

print("\nDistribuição do IDEB — Paraná, 2023")
print("-" * 45)
print(f"Municípios na base consolidada: {len(df)}")
print(f"Municípios válidos: {n}")
print(f"Média: {mean:.2f}")
print(f"Mediana: {median:.2f}")
print(f"Desvio-padrão: {std:.2f}")
print(f"Mínimo: {minimum:.2f}")
print(f"Máximo: {maximum:.2f}")

if n != 387:
    raise ValueError(
        f"Esperavam-se 387 municípios válidos, mas foram "
        f"encontrados {n}. Confira o filtro e a base utilizada."
    )


bin_width = 0.2

bin_start = (
    np.floor(minimum / bin_width) * bin_width
)

bin_end = (
    np.ceil(maximum / bin_width) * bin_width
    + bin_width
)

bins = np.arange(
    bin_start,
    bin_end + bin_width / 2,
    bin_width,
)

fig, ax = plt.subplots(
    figsize=(10, 5.5),
    dpi=150,
)

counts, bin_edges, patches = ax.hist(
    ideb,
    bins=bins,
    color="#005C4A",
    edgecolor="white",
    linewidth=0.8,
    alpha=0.9,
)

for count, patch in zip(counts, patches):
    if count > 0:
        x = patch.get_x() + patch.get_width() / 2
        y = patch.get_height()

        ax.text(
            x,
            y + 1,
            f"{int(count)}",
            ha="center",
            va="bottom",
            fontsize=9,
            color="black",
        )

ax.axvline(
    mean,
    color="#D97706",
    linewidth=2.5,
    linestyle="--",
    label=f"Média: {mean:.2f}".replace(".", ","),
    zorder=6,
)

ax.axvline(
    median,
    color="#17324D",
    linewidth=2,
    linestyle=":",
    label=f"Mediana: {median:.2f}".replace(".", ","),
)

ax.set_xlabel(
    "IDEB do Ensino Médio da rede pública (2023)",
    fontsize=11,
)

ax.set_ylabel(
    "Número de municípios",
    fontsize=11,
)

ax.set_title(
    "Distribuição Municipal do IDEB no Paraná, 2023",
    fontsize=13,
    fontweight="bold",
    pad=15,
)

ax.text(
    0.98,
    0.96,
    f"n = {n} municípios",
    transform=ax.transAxes,
    ha="right",
    va="top",
    fontsize=10,
)

ax.grid(
    axis="y",
    alpha=0.2,
)

ax.set_axisbelow(True)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.legend(
    frameon=False,
    loc="upper left",
)

fig.tight_layout()


fig.savefig(
    OUTPUT_PATH,
    dpi=300,
    bbox_inches="tight",
    facecolor="white",
)

plt.show()

print(f"\nFigura salva em: {OUTPUT_PATH.resolve()}")