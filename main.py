from __future__ import annotations

import logging
from pathlib import Path

from src.algoritmo import executar_ag
from src.carregar_dados import carregar_dados
from src.cromossomo import cromossomo_para_grade
from src.visualizacao import (
    exportar_csv,
    plotar_convergencia,
    plotar_grade_periodo,
)

RAIZ = Path(__file__).resolve().parent
DIR_DATA = RAIZ / "data"
DIR_OUTPUT = RAIZ / "output"

CAMINHO_LOG = DIR_OUTPUT / "log_execucao.txt"
CAMINHO_CONVERGENCIA = DIR_OUTPUT / "convergencia.png"
CAMINHO_CSV = DIR_OUTPUT / "grade_final.csv"
CAMINHOS_GRADES = [DIR_OUTPUT / f"grade_periodo_{p}.png" for p in (1, 2, 3, 4)]


def _configurar_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s | %(name)s | %(message)s",
    )


def main() -> None:
    _configurar_logging()
    DIR_OUTPUT.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print(" Algoritmo Genético — Grade Horária (UTFPR Santa Helena)")
    print("=" * 70)

    print("\n[1/7] Carregando dados...")
    disciplinas, professores, aulas_a_alocar = carregar_dados(
        DIR_DATA / "disciplinas.json", DIR_DATA / "professores.json"
    )
    print(
        f"      {len(disciplinas)} disciplinas | {len(professores)} professores | "
        f"{len(aulas_a_alocar)} aulas a alocar (tamanho do cromossomo)."
    )

    print("\n[2/7] Executando o Algoritmo Genético (até 1000 gerações)...")
    resultado = executar_ag(
        aulas_a_alocar, disciplinas, professores, caminho_log=CAMINHO_LOG
    )

    print("\n[3/7] Decodificando a melhor solução...")
    grade = cromossomo_para_grade(
        resultado.melhor_solucao, aulas_a_alocar, disciplinas, professores
    )

    print("\n[4/7] Gerando gráfico de convergência...")
    plotar_convergencia(
        resultado.historico_melhor, resultado.historico_medio, CAMINHO_CONVERGENCIA
    )
    print("[5/7] Gerando grades por período...")
    for periodo, caminho in zip((1, 2, 3, 4), CAMINHOS_GRADES):
        plotar_grade_periodo(grade, periodo, caminho)
    print("[6/7] Exportando CSV...")
    exportar_csv(grade, CAMINHO_CSV)

    _imprimir_resumo(resultado)


def _imprimir_resumo(resultado) -> None:
    """Imprime o resumo da execução (CLAUDE.md §8 / regra 6)."""
    c = resultado.conflitos
    total = sum(c.values())
    print("\n" + "=" * 70)
    print(" RESUMO DA EXECUÇÃO")
    print("=" * 70)
    print(f"  Gerações executadas .......: {resultado.num_geracoes}")
    print(f"  Fitness final .............: {resultado.melhor_fitness:.0f}")
    print(f"  Conflitos de período (P1) .: {c['conflitos_periodo']}")
    print(f"  Conflitos de professor (P2): {c['conflitos_professor']}")
    print(f"  Conflitos de pré-req. (P3) : {c['conflitos_prerequisito']}")
    print(f"  Total de conflitos ........: {total}")
    print(f"  Tempo total de execução ...: {resultado.tempo_execucao:.2f} s")

    if resultado.melhor_fitness == 0:
        print("\n  >>> Solução PERFEITA encontrada (zero conflitos)! <<<")
    else:
        print(
            f"\n  >>> Encerrado com {total} conflito(s) residual(is). "
            "<<<"
        )

    print("\n  Arquivos gerados em output/:")
    arquivos = [
        CAMINHO_CONVERGENCIA,
        *CAMINHOS_GRADES,
        CAMINHO_CSV,
        CAMINHO_LOG,
    ]
    for caminho in arquivos:
        existe = "✓" if caminho.exists() else "✗"
        print(f"    [{existe}] {caminho.resolve()}")
    print("=" * 70)


if __name__ == "__main__":
    main()
