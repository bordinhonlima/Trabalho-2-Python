from __future__ import annotations

from collections.abc import Sequence

from .modelo import Aula, Disciplina, Professor, SlotAlocado

HORARIOS_POR_DIA = 8
DIAS_NA_SEMANA = 5
TOTAL_SLOTS = HORARIOS_POR_DIA * DIAS_NA_SEMANA  # 40


def slot_para_dia_horario(slot: int) -> tuple[int, int]:
    return slot // HORARIOS_POR_DIA, slot % HORARIOS_POR_DIA


def decodificar(
    cromossomo: Sequence[int], aulas_a_alocar: list[Aula]
) -> dict[int, list[Aula]]:
    slots: dict[int, list[Aula]] = {}
    for indice_gene, slot in enumerate(cromossomo):
        slot = int(slot)
        slots.setdefault(slot, []).append(aulas_a_alocar[indice_gene])
    return slots


def cromossomo_para_grade(
    cromossomo: Sequence[int],
    aulas_a_alocar: list[Aula],
    disciplinas: dict[str, Disciplina],
    professores: dict[str, Professor],
) -> dict[int, list[SlotAlocado]]:
    grade: dict[int, list[SlotAlocado]] = {}
    for indice_gene, slot in enumerate(cromossomo):
        aula = aulas_a_alocar[indice_gene]
        dia, horario = slot_para_dia_horario(int(slot))
        disciplina = disciplinas[aula.codigo_disciplina]
        professor = professores[aula.professor_id]
        slot_alocado = SlotAlocado(
            dia=dia, horario=horario, disciplina=disciplina, professor=professor
        )
        grade.setdefault(aula.periodo, []).append(slot_alocado)
    return grade
