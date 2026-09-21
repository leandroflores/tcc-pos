
from pathlib import Path
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


DATA_PATH = Path(
    "outputs/modeling/"
    "ideb_random_forest_test_predictions.csv"
)

OUTPUT_DIR = Path("outputs/figures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = (
    OUTPUT_DIR
    / "figura_5_ideb_observado_estimado_floresta.png"
)


df = pd.read_csv(
    DATA_PATH,
    sep=";",
    decimal=",",
    encoding="utf-8-sig",
)

required_columns = [
    "ideb_observado",
    "ideb_estimado",
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Colunas não encontradas: {missing_columns}"
    )

if df[required_columns].isna().any().any():
    raise ValueError(
        "Foram encontrados valores ausentes "
        "nas observações ou previsões."
    )

y_test = df["ideb_observado"].to_numpy()
y_pred = df["ideb_estimado"].to_numpy()

n = len(df)

if n != 97:
    raise ValueError(
        f"Esperavam-se 97 municípios; "
        f"foram encontrados {n}."
    )

mae = mean_absolute_error(
    y_test,
    y_pred,
)

rmse = np.sqrt(
    mean_squared_error(
        y_test,
        y_pred,
    )
)

r2 = r2_score(
    y_test,
    y_pred,
)


def format_brazilian_decimal(value, decimals=3):
    return f"{value:.{decimals}f}".replace(".", ",")


print("\nFloresta aleatória — IDEB")
print("-" * 40)
print(f"Municípios no teste: {n}")
print(f"MAE: {format_brazilian_decimal(mae)}")
print(f"RMSE: {format_brazilian_decimal(rmse)}")
print(f"R²: {format_brazilian_decimal(r2)}")

expected = {
    "MAE": (mae, 0.236),
    "RMSE": (rmse, 0.306),
    "R²": (r2, 0.035),
}

for metric, (obtained, expected_value) in expected.items():
    if round(obtained, 3) != expected_value:
        print(
            f"ATENÇÃO: {metric} difere "
            "do valor da Tabela 6."
        )


fig, ax = plt.subplots(
    figsize=(9, 6),
    dpi=150,
)

ax.scatter(
    y_test,
    y_pred,
    s=52,
    color="#005C4A",
    alpha=0.70,
    edgecolors="white",
    linewidths=0.5,
    label="Municípios",
    zorder=3,
)

minimum = min(
    y_test.min(),
    y_pred.min(),
)

maximum = max(
    y_test.max(),
    y_pred.max(),
)

margin = 0.15

axis_min = minimum - margin
axis_max = maximum + margin

ax.plot(
    [axis_min, axis_max],
    [axis_min, axis_max],
    color="#D97706",
    linewidth=2,
    linestyle="--",
    label="Previsão perfeita",
    zorder=2,
)

ax.set_xlim(
    axis_min,
    axis_max,
)

ax.set_ylim(
    axis_min,
    axis_max,
)

ax.set_aspect(
    "equal",
    adjustable="box",
)


ax.set_title(
    "IDEB observado e estimado pelo Random Forest",
    fontsize=13,
    fontweight="bold",
    pad=15,
)

ax.set_xlabel(
    "IDEB observado no conjunto de teste",
    fontsize=11,
)

ax.set_ylabel(
    "IDEB estimado pela floresta aleatória",
    fontsize=11,
)

metrics_text = (
    f"n = {n} municípios\n"
    f"MAE = {format_brazilian_decimal(mae)}\n"
    f"RMSE = {format_brazilian_decimal(rmse)}\n"
    f"R² = {format_brazilian_decimal(r2)}"
)

ax.text(
    0.98,
    0.04,
    metrics_text,
    transform=ax.transAxes,
    ha="right",
    va="bottom",
    fontsize=10,
    bbox={
        "facecolor": "white",
        "edgecolor": "#D9D9D9",
        "alpha": 0.95,
        "boxstyle": "round,pad=0.5",
    },
)

ax.grid(
    alpha=0.20,
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
