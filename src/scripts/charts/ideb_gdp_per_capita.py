
from matplotlib.ticker import FuncFormatter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


DATA_PATH = Path(
    "data/process/csv_complete_data/PR.csv"
)

OUTPUT_DIR = Path("outputs/figures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = (
    OUTPUT_DIR
    / "figura_4_pib_per_capita_ideb_pr_2023.png"
)

IDEB_COLUMN = "ideb_publica_medio_todos_1_4"

GDP_PER_CAPITA_COLUMN = (
    "gdp_per_capita_2023_current_reais"
)

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

required_columns = (
    EDUCATIONAL_COLUMNS
    + [GDP_PER_CAPITA_COLUMN, "city_code"]
)

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        "Colunas não encontradas: "
        f"{missing_columns}"
    )


def convert_numeric(series: pd.Series) -> pd.Series:
    """Converte valores com ponto ou vírgula decimal."""

    values = series.astype("string").str.strip()

    has_comma = values.str.contains(
        ",",
        regex=False,
        na=False,
    )

    values.loc[has_comma] = (
        values.loc[has_comma]
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )

    return pd.to_numeric(
        values,
        errors="coerce",
    )


for column in EDUCATIONAL_COLUMNS + [
    GDP_PER_CAPITA_COLUMN
]:
    df[column] = convert_numeric(df[column])


df_valid = df.dropna(
    subset=EDUCATIONAL_COLUMNS
).copy()

if len(df_valid) != 387:
    raise ValueError(
        "Quantidade inesperada de municípios "
        "após o filtro educacional: "
        f"{len(df_valid)}"
    )

if df_valid["city_code"].duplicated().any():
    raise ValueError(
        "Foram encontrados códigos "
        "municipais duplicados."
    )

df_plot = df_valid.dropna(
    subset=[GDP_PER_CAPITA_COLUMN]
).copy()

if len(df_plot) != 387:
    raise ValueError(
        "Há municípios sem PIB per capita "
        "válido. Confira a amostra antes "
        "de comparar com a Tabela 5."
    )

x = df_plot[GDP_PER_CAPITA_COLUMN].to_numpy(
    dtype=float
)

y = df_plot[IDEB_COLUMN].to_numpy(
    dtype=float
)

n = len(df_plot)


correlation = np.corrcoef(x, y)[0, 1]

slope, intercept = np.polyfit(
    x,
    y,
    deg=1,
)

x_line = np.linspace(
    x.min(),
    x.max(),
    300,
)

y_line = slope * x_line + intercept


print("\nPIB per capita × IDEB — Paraná, 2023")
print("-" * 45)
print(f"Municípios analisados: {n}")
print(
    "Correlação de Pearson: "
    f"{correlation:.6f}"
)
print(
    "Correlação arredondada: "
    f"{correlation:.3f}".replace(".", ",")
)

if not np.isclose(
    correlation,
    0.065,
    atol=0.001,
):
    print(
        "\nATENÇÃO: a correlação obtida difere "
        "do valor informado na Tabela 5. "
        "Confira a base e os filtros."
    )


fig, ax = plt.subplots(
    figsize=(10, 5.5),
    dpi=150,
)

# Um ponto para cada município.
ax.scatter(
    x,
    y,
    s=38,
    color="#005C4A",
    alpha=0.65,
    edgecolors="white",
    linewidths=0.4,
    label="Municípios",
)

ax.plot(
    x_line,
    y_line,
    color="#D97706",
    linewidth=2.2,
    linestyle="--",
    label="Tendência linear",
)

def format_reais(value, position):
    return (
        "R$ "
        + f"{value:,.0f}"
        .replace(",", ".")
    )


ax.xaxis.set_major_formatter(
    FuncFormatter(format_reais)
)

ax.set_xlabel(
    "PIB per capita municipal (2023)",
    fontsize=11,
)

ax.set_ylabel(
    "IDEB do Ensino Médio da rede pública (2023)",
    fontsize=11,
)

ax.set_title(
    "PIB per capita e IDEB nos municípios do Paraná",
    fontsize=13,
    fontweight="bold",
    pad=15,
)

correlation_label = (
    f"n = {n} municípios\n"
    f"r = {correlation:.3f}"
).replace(".", ",")

ax.text(
    0.98,
    0.96,
    correlation_label,
    transform=ax.transAxes,
    ha="right",
    va="top",
    fontsize=10,
    bbox={
        "facecolor": "white",
        "edgecolor": "none",
        "alpha": 0.85,
    },
)

ax.margins(
    x=0.04,
    y=0.10,
)

ax.grid(
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

print(
    "\nFigura salva em: "
    f"{OUTPUT_PATH.resolve()}"
)
