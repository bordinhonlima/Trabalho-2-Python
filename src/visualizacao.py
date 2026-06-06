from __future__ import annotations

import csv
import logging
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from .modelo import SlotAlocado

logger = logging.getLogger(__name__)

# rotulos
DIAS = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
ROTULOS_HORARIOS = [
    "07:30-08:20",
    "08:20-09:10",
    "09:20-10:10",
    "10:10-11:00",
    "13:30-14:20",
    "14:20-15:10",
    "15:20-16:10",
    "16:10-17:00",
]


def plotar_convergencia(
    historico_melhor: list[float],
    historico_medio: list[float],
    caminho_saida: str | Path,
) -> None:
    # plota a evolucao do fitness
    geracoes = range(1, len(historico_melhor) + 1)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(geracoes, historico_melhor, label="Melhor fitness", color="#1b7837", linewidth=2)
    ax.plot(geracoes, historico_medio, label="Fitness médio", color="#762a83", linewidth=1.2, alpha=0.8)
    ax.axhline(0, color="gray", linestyle="--", linewidth=1, label="Solução perfeita (0)")
    ax.set_xlabel("Geração")
    ax.set_ylabel("Fitness (0 = sem conflitos)")
    ax.set_title("Convergência do Algoritmo Genético")
    ax.legend(loc="lower right")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    caminho_saida = Path(caminho_saida)
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(caminho_saida, dpi=120)
    plt.close(fig)
    logger.info("Gráfico de convergência salvo em %s", caminho_saida)


def _cor_por_disciplina(slots: list[SlotAlocado]) -> dict[str, tuple]:
    codigos = sorted({s.disciplina.codigo for s in slots})
    cmap = plt.get_cmap("tab20")
    return {cod: cmap(i % 20) for i, cod in enumerate(codigos)}


def plotar_grade_periodo(
    grade_por_periodo: dict[int, list[SlotAlocado]],
    periodo: int,
    caminho_saida: str | Path,
    dias: list[str] = DIAS,
    rotulos_horarios: list[str] = ROTULOS_HORARIOS,
) -> None:
    slots = grade_por_periodo.get(periodo, [])
    cores = _cor_por_disciplina(slots)
    n_dias = len(dias)
    n_hor = len(rotulos_horarios)

  
    celulas: dict[tuple[int, int], list[SlotAlocado]] = {}
    for s in slots:
        celulas.setdefault((s.dia, s.horario), []).append(s)

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, n_dias)
    ax.set_ylim(0, n_hor)
    ax.invert_yaxis()

    for h in range(n_hor):
        for d in range(n_dias):
            aulas_celula = celulas.get((d, h), [])
            conflito = len(aulas_celula) > 1
            if aulas_celula:
                cor = cores[aulas_celula[0].disciplina.codigo]
                texto = "\n".join(
                    f"{a.disciplina.codigo}\n{a.professor.nome.split()[-1]}"
                    for a in aulas_celula
                )
            else:
                cor = "white"
                texto = ""
            ax.add_patch(
                Rectangle(
                    (d, h),
                    1,
                    1,
                    facecolor=cor,
                    edgecolor="red" if conflito else "black",
                    linewidth=2.5 if conflito else 0.6,
                )
            )
            if texto:
                ax.text(
                    d + 0.5,
                    h + 0.5,
                    texto,
                    ha="center",
                    va="center",
                    fontsize=7,
                    weight="bold" if conflito else "normal",
                )

    ax.set_xticks([d + 0.5 for d in range(n_dias)])
    ax.set_xticklabels(dias)
    ax.set_yticks([h + 0.5 for h in range(n_hor)])
    ax.set_yticklabels(rotulos_horarios)
    ax.xaxis.tick_top()
    ax.set_title(f"Grade Horária — {periodo}º Período", pad=20)
    ax.tick_params(length=0)
    fig.tight_layout()

    caminho_saida = Path(caminho_saida)
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(caminho_saida, dpi=120)
    plt.close(fig)
    logger.info("Grade do período %d salva em %s", periodo, caminho_saida)


def exportar_csv(
    grade_por_periodo: dict[int, list[SlotAlocado]],
    caminho_saida: str | Path,
    dias: list[str] = DIAS,
    rotulos_horarios: list[str] = ROTULOS_HORARIOS,
) -> None:
    caminho_saida = Path(caminho_saida)
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    with caminho_saida.open("w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow(["periodo", "dia", "horario", "codigo", "disciplina", "professor"])
        for periodo in sorted(grade_por_periodo):
            linhas = sorted(
                grade_por_periodo[periodo], key=lambda s: (s.dia, s.horario)
            )
            for s in linhas:
                escritor.writerow(
                    [
                        periodo,
                        dias[s.dia],
                        rotulos_horarios[s.horario],
                        s.disciplina.codigo,
                        s.disciplina.nome,
                        s.professor.nome,
                    ]
                )
    logger.info("CSV de alocações salvo em %s", caminho_saida)
