from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Disciplina:
    codigo: str
    nome: str
    periodo: int
    aulas_semanais: int
    carga_horaria: int
    pre_requisitos: list[str] = field(default_factory=list)
    professor_id: str = ""


@dataclass(frozen=True)
class Professor:
    id: str
    nome: str
    area: str


@dataclass(frozen=True)
class Aula:
    periodo: int
    codigo_disciplina: str
    professor_id: str


@dataclass(frozen=True)
class SlotAlocado:
    dia: int
    horario: int
    disciplina: Disciplina
    professor: Professor
