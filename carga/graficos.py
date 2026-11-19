"""Gráficos de las pruebas de carga con Locust contra Azure (fase 3)."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter, LogLocator, NullFormatter

RESULTADOS = Path("carga/resultados")
SALIDA = Path("carga/graficos")
SALIDA.mkdir(parents=True, exist_ok=True)

# Cada usuario de Locust espera entre 1 y 2 s (1,5 s en promedio) y luego su
# respuesta (~0,095 s sin fila). Por eso cada usuario genera ~0,63 peticiones/s.
PETICIONES_POR_USUARIO = 1 / (1.5 + 0.095)

# Un color fijo por configuración, igual en todos los gráficos.
ESCENARIOS = {
    "A": ("azure_a_1replica", "A · sin pool, 1 réplica", "#2a78d6"),
    "B": ("azure_b_escalado", "B · sin pool, 1–3 réplicas", "#eb6834"),
    "A2": ("azure_a2_1replica_pool", "A2 · con pool, 1 réplica", "#1baf7a"),
    "A3": ("azure_a3_1replica_pool_1000", "A3 · con pool, 1 réplica", "#1baf7a"),
    "B3": ("azure_b3_escalado_pool_1000", "B3 · con pool, 1–3 réplicas", "#6250d6"),
}

TINTA = "#0b0b0b"
TINTA_SECUNDARIA = "#52514e"
REJILLA = "#e4e3df"
GRIS_REFERENCIA = "#8a8984"


def cargar(clave):
    archivo, etiqueta, color = ESCENARIOS[clave]
    df = pd.read_csv(RESULTADOS / f"{archivo}_stats_history.csv", na_values=["N/A"])
    df = df[df["Name"] == "Aggregated"].copy()
    # Al final Locust apaga a los usuarios (el contador cae a 0): esos segundos se quitan.
    df = df[df["User Count"] == df["User Count"].cummax()]
    df["segundo"] = df["Timestamp"] - df["Timestamp"].min()
    df["mediana_ms"] = df["50%"]
    return df, etiqueta, color


def estilo(ax, titulo, eje_y):
    ax.set_title(titulo, loc="left", fontsize=12, color=TINTA, pad=12)
    ax.set_xlabel("Segundos desde el inicio de la prueba", color=TINTA_SECUNDARIA)
    ax.set_ylabel(eje_y, color=TINTA_SECUNDARIA)
    ax.grid(axis="y", color=REJILLA, linewidth=0.8)
    ax.tick_params(colors=TINTA_SECUNDARIA, length=0)
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    ax.spines["bottom"].set_color(REJILLA)


# A y B terminan casi en el mismo valor: B se etiqueta un poco más abajo.
DESPLAZAMIENTO = {"B": -9}


def etiqueta_al_final(ax, df, columna, texto, desplazar=False):
    ultimo = df.dropna(subset=[columna]).iloc[-1]
    ax.annotate(
        texto,
        xy=(ultimo["segundo"], ultimo[columna]),
        xytext=(6, DESPLAZAMIENTO.get(texto, 0) if desplazar else 0),
        textcoords="offset points",
        va="center",
        fontsize=9,
        color=TINTA,
    )


def grafico_rps(claves, titulo, archivo):
    fig, ax = plt.subplots(figsize=(9, 5.4))
    referencia = None
    for clave in claves:
        df, etiqueta, color = cargar(clave)
        ax.plot(df["segundo"], df["Requests/s"], color=color, linewidth=2, zorder=2, label=etiqueta)
        etiqueta_al_final(ax, df, "Requests/s", clave, desplazar=True)
        if referencia is None:
            referencia = df
    ax.plot(
        referencia["segundo"],
        referencia["User Count"] * PETICIONES_POR_USUARIO,
        color=GRIS_REFERENCIA,
        linewidth=1.5,
        zorder=1,
        label="Peticiones que hacen los usuarios (estimado)",
    )
    estilo(ax, titulo, "Peticiones atendidas por segundo")
    ax.set_ylim(bottom=0)
    ax.legend(
        frameon=False, fontsize=9, ncol=2,
        loc="upper center", bbox_to_anchor=(0.5, -0.16),
    )
    fig.tight_layout()
    fig.savefig(SALIDA / archivo, dpi=200)
    plt.close(fig)


def grafico_mediana(claves, titulo, archivo):
    fig, ax = plt.subplots(figsize=(9, 5.4))
    for clave in claves:
        df, etiqueta, color = cargar(clave)
        ax.plot(df["segundo"], df["mediana_ms"], color=color, linewidth=2, label=etiqueta)
        etiqueta_al_final(ax, df, "mediana_ms", clave, desplazar=True)
    estilo(ax, titulo, "Mediana de /salud y /salud/db juntas (ms, escala log.)")
    ax.set_yscale("log")
    ax.yaxis.set_major_locator(LogLocator(base=10, subs=(1.0, 2.0, 5.0)))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:,.0f}".replace(",", " ")))
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.legend(
        frameon=False, fontsize=9, ncol=2,
        loc="upper center", bbox_to_anchor=(0.5, -0.16),
    )
    fig.tight_layout()
    fig.savefig(SALIDA / archivo, dpi=200)
    plt.close(fig)


grafico_rps(
    ["A", "B", "A2"],
    "300 usuarios: sin pool la app se estanca; con pool sigue a la carga",
    "1_rps_300_usuarios.png",
)
grafico_mediana(
    ["A", "B", "A2"],
    "300 usuarios: tiempo de respuesta",
    "2_mediana_300_usuarios.png",
)
grafico_rps(
    ["A3", "B3"],
    "1000 usuarios con pool: 1 réplica se satura; 3 réplicas atienden la carga",
    "3_rps_1000_usuarios.png",
)
grafico_mediana(
    ["A3", "B3"],
    "1000 usuarios con pool: tiempo de respuesta",
    "4_mediana_1000_usuarios.png",
)
print("Gráficos guardados en", SALIDA)