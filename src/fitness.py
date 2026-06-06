from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Sequence

from .cromossomo import decodificar
from .modelo import Aula, Disciplina

P1_PERIODO = 10
P2_PROFESSOR = 8
P3_PREREQUISITO = 6


def calcular_conflitos(
    cromossomo: Sequence[int],
    aulas_a_alocar: list[Aula],
    disciplinas: dict[str, Disciplina],
) -> dict[str, int]:
    slots = decodificar(cromossomo, aulas_a_alocar)

    conflitos_periodo = 0
    conflitos_professor = 0
    conflitos_prerequisito = 0

    for aulas_no_slot in slots.values():
        n = len(aulas_no_slot)
        if n < 2:
            continue  # slot com 0 ou 1 aula não gera conflito

        cont_periodo = Counter(a.periodo for a in aulas_no_slot)
        for c in cont_periodo.values():
            conflitos_periodo += c * (c - 1) // 2

        por_professor: dict[str, list[Aula]] = {}
        for a in aulas_no_slot:
            por_professor.setdefault(a.professor_id, []).append(a)
        for grupo in por_professor.values():
            k = len(grupo)
            if k < 2:
                continue
            total_pares = k * (k - 1) // 2
            cont_disc = Counter(a.codigo_disciplina for a in grupo)
            pares_mesma_disc = sum(c * (c - 1) // 2 for c in cont_disc.values())
            conflitos_professor += total_pares - pares_mesma_disc

        for i in range(n):
            for j in range(i + 1, n):
                cod_i = aulas_no_slot[i].codigo_disciplina
                cod_j = aulas_no_slot[j].codigo_disciplina
                if cod_i == cod_j:
                    continue
                if (
                    cod_j in disciplinas[cod_i].pre_requisitos
                    or cod_i in disciplinas[cod_j].pre_requisitos
                ):
                    conflitos_prerequisito += 1

    return {
        "conflitos_periodo": conflitos_periodo,
        "conflitos_professor": conflitos_professor,
        "conflitos_prerequisito": conflitos_prerequisito,
    }


def criar_fitness_func(
    aulas_a_alocar: list[Aula], disciplinas: dict[str, Disciplina]
) -> Callable[[object, Sequence[int], int], float]:

    def fitness_func(ga_instance: object, solucao: Sequence[int], idx: int) -> float:
        conflitos = calcular_conflitos(solucao, aulas_a_alocar, disciplinas)
        penalidade = (
            P1_PERIODO * conflitos["conflitos_periodo"]
            + P2_PROFESSOR * conflitos["conflitos_professor"]
            + P3_PREREQUISITO * conflitos["conflitos_prerequisito"]
        )
        return float(-penalidade)

    return fitness_func
