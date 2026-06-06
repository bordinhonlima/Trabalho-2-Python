from __future__ import annotations

import json
import logging
from pathlib import Path

from .modelo import Aula, Disciplina, Professor

logger = logging.getLogger(__name__)

# raiz
_RAIZ_PROJETO = Path(__file__).resolve().parent.parent
PATH_DISCIPLINAS_PADRAO = _RAIZ_PROJETO / "data" / "disciplinas.json"
PATH_PROFESSORES_PADRAO = _RAIZ_PROJETO / "data" / "professores.json"


def carregar_dados(
    path_disciplinas: str | Path = PATH_DISCIPLINAS_PADRAO,
    path_professores: str | Path = PATH_PROFESSORES_PADRAO,
) -> tuple[dict[str, Disciplina], dict[str, Professor], list[Aula]]:
    path_disciplinas = Path(path_disciplinas)
    path_professores = Path(path_professores)

    with path_disciplinas.open(encoding="utf-8") as f:
        dados_disc = json.load(f)
    with path_professores.open(encoding="utf-8") as f:
        dados_prof = json.load(f)

    # monta o dicionario de professores
    professores: dict[str, Professor] = {}
    for p in dados_prof["professores"]:
        professores[p["id"]] = Professor(id=p["id"], nome=p["nome"], area=p["area"])

    # monta o dicionaario de disciplinas e a lista expandida de aulas
    disciplinas: dict[str, Disciplina] = {}
    aulas_a_alocar: list[Aula] = []

    # itera os períodos em ordem numérica crescente para garantir determinismo.
    for periodo_str in sorted(dados_disc["periodos"], key=int):
        periodo = int(periodo_str)
        for d in dados_disc["periodos"][periodo_str]:
            disciplina = Disciplina(
                codigo=d["codigo"],
                nome=d["nome"],
                periodo=periodo,
                aulas_semanais=d["aulas_semanais"],
                carga_horaria=d["carga_horaria"],
                pre_requisitos=list(d.get("pre_requisitos", [])),
                professor_id=d["professor_id"],
            )
            disciplinas[disciplina.codigo] = disciplina

            for _ in range(disciplina.aulas_semanais):
                aulas_a_alocar.append(
                    Aula(
                        periodo=periodo,
                        codigo_disciplina=disciplina.codigo,
                        professor_id=disciplina.professor_id,
                    )
                )

    logger.info(
        "Dados carregados: %d disciplinas, %d professores, %d aulas a alocar.",
        len(disciplinas),
        len(professores),
        len(aulas_a_alocar),
    )
    return disciplinas, professores, aulas_a_alocar
