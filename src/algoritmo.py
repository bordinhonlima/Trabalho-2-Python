from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pygad

from .fitness import calcular_conflitos, criar_fitness_func
from .modelo import Aula, Disciplina, Professor

logger = logging.getLogger(__name__)

# seed global
SEED = 42

# hiperparametros
HIPERPARAMETROS: dict[str, object] = {
    "num_generations": 1000,
    "sol_per_pop": 100,
    "num_parents_mating": 40,
    "parent_selection_type": "tournament",
    "K_tournament": 3,
    "keep_elitism": 5,
    "crossover_type": "single_point",
    "crossover_probability": 0.8,
    "mutation_type": "random",
    "mutation_probability": 0.05,
    "mutation_by_replacement": True,
    "gene_type": int,
    "gene_space": range(0, 40),
    # saturate_500 garante minimo de 500 geracoes
    "stop_criteria": ["reach_0", "saturate_500"],
    "random_seed": SEED,
}


@dataclass
class ResultadoAG:
    melhor_solucao: np.ndarray
    melhor_fitness: float
    conflitos: dict[str, int]
    num_geracoes: int
    historico_melhor: list[float] = field(default_factory=list)
    historico_medio: list[float] = field(default_factory=list)
    tempo_execucao: float = 0.0


def _configurar_log_execucao(caminho_log: Path) -> logging.Logger:
    log_exec = logging.getLogger("ag.execucao")
    log_exec.setLevel(logging.INFO)
    log_exec.propagate = False
    # Remove handlers antigos para evitar duplicação em re-execuções.
    for h in list(log_exec.handlers):
        log_exec.removeHandler(h)
    caminho_log.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(caminho_log, mode="w", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s | %(message)s"))
    log_exec.addHandler(handler)
    return log_exec


def executar_ag(
    aulas_a_alocar: list[Aula],
    disciplinas: dict[str, Disciplina],
    professores: dict[str, Professor],
    caminho_log: Path | str = "output/log_execucao.txt",
) -> ResultadoAG:
    # fixa a seed do numpy
    np.random.seed(SEED)

    caminho_log = Path(caminho_log)
    log_exec = _configurar_log_execucao(caminho_log)

    num_genes = len(aulas_a_alocar)
    fitness_func = criar_fitness_func(aulas_a_alocar, disciplinas)

    # históricos coletados a cada geração para o gráfico
    historico_melhor: list[float] = []
    historico_medio: list[float] = []

    log_exec.info(
        "Início da execução | genes=%d | hiperparâmetros=%s",
        num_genes,
        {k: (v if not isinstance(v, range) else "range(0,40)") for k, v in HIPERPARAMETROS.items()},
    )

    def on_generation(ga: pygad.GA) -> None:
        fitness_atual = ga.last_generation_fitness
        melhor = float(np.max(fitness_atual))
        medio = float(np.mean(fitness_atual))
        historico_melhor.append(melhor)
        historico_medio.append(medio)
        ger = ga.generations_completed
        if ger % 10 == 0 or melhor == 0:
            log_exec.info(
                "Geração %4d | melhor=%.1f | médio=%.2f", ger, melhor, medio
            )

    ga = pygad.GA(
        num_genes=num_genes,
        fitness_func=fitness_func,
        on_generation=on_generation,
        suppress_warnings=True,
        **HIPERPARAMETROS,
    )

    inicio = time.perf_counter()
    ga.run()
    tempo_execucao = time.perf_counter() - inicio

    melhor_solucao, melhor_fitness, _ = ga.best_solution()
    melhor_solucao = np.asarray(melhor_solucao, dtype=int)
    conflitos = calcular_conflitos(melhor_solucao, aulas_a_alocar, disciplinas)

    log_exec.info(
        "Fim da execução | gerações=%d | fitness=%.1f | conflitos=%s | tempo=%.2fs",
        ga.generations_completed,
        float(melhor_fitness),
        conflitos,
        tempo_execucao,
    )

    return ResultadoAG(
        melhor_solucao=melhor_solucao,
        melhor_fitness=float(melhor_fitness),
        conflitos=conflitos,
        num_geracoes=ga.generations_completed,
        historico_melhor=historico_melhor,
        historico_medio=historico_medio,
        tempo_execucao=tempo_execucao,
    )
