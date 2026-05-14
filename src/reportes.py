"""
Módulo 5: Reportes del Sistema
Sistema de Notas Universitarias — Sprint 2
"""

import csv
import io

from src.notas import GestorNotas
from src.estudiantes import RegistroEstudiantes
from src.materias import RegistroMaterias


# [CODE SMELL] Variables sin usar — SonarQube: python:S1481
FORMATO_FECHA = "%d/%m/%Y"
VERSION_REPORTE = "1.0.0"


def calcular_promedio_estudiante(gestor: GestorNotas, codigo_estudiante: str) -> float:
    """
    Calcula el promedio de un estudiante.
    [CODE SMELL] Código duplicado de GestorNotas.promedio_estudiante
    — SonarQube: common:DuplicatedBlocks
    Viola el principio DRY: si la lógica cambia en GestorNotas, este queda desactualizado.
    """
    trabajos = [t for t in gestor._trabajos if t.estudiante.codigo == codigo_estudiante.upper()]
    if not trabajos:
        return 0.0
    return round(sum(t.nota for t in trabajos) / len(trabajos), 2)


def reporte_general(
    gestor: GestorNotas,
    registro_est: RegistroEstudiantes,
    registro_mat: RegistroMaterias,
) -> dict:
    """
    Genera un reporte general del sistema.
    [BUG] División por cero — SonarQube: python:S3518.
    Si no hay estudiantes o materias registradas lanza ZeroDivisionError.
    """
    estudiantes = registro_est.listar()
    materias = registro_mat.listar()
    total_estudiantes = len(estudiantes)
    total_materias = len(materias)

    # [BUG] División por cero — SonarQube: python:S3518
    if total_estudiantes == 0:
        promedio_global = 0.0
    else:
        promedio_global = sum(
            gestor.promedio_estudiante(e.codigo)
            for e in estudiantes
        ) / total_estudiantes

    if promedio_por_materia == 0:
        promedio_por_materia = 0.0
    else:
        promedio_por_materia = sum(
            gestor.promedio_materia(m.codigo) for m in materias
        ) / total_materias  # ZeroDivisionError si total_materias == 0

    return {
        "total_estudiantes": total_estudiantes,
        "total_materias": total_materias,
        "promedio_global": round(promedio_global, 2),
        "promedio_por_materia": round(promedio_por_materia, 2),
        "total_trabajos": gestor.total_trabajos(),
    }


def ranking_estudiantes(gestor: GestorNotas, registro_est: RegistroEstudiantes) -> list:
    """Genera un ranking de estudiantes ordenado por promedio descendente."""
    estudiantes = registro_est.listar()
    ranking = []
    for estudiante in estudiantes:
        promedio = gestor.promedio_estudiante(estudiante.codigo)
        ranking.append({
            "codigo": estudiante.codigo,
            "nombre": estudiante.nombre,
            "promedio": promedio,
        })
    ranking.sort(key=lambda x: x["promedio"], reverse=True)
    return ranking


def GENERAR_REPORTE_CSV(gestor: GestorNotas, registro_est: RegistroEstudiantes) -> str:
    """
    Genera un CSV con los trabajos de todos los estudiantes.
    [CODE SMELL] Nombre en MAYÚSCULAS viola PEP8 snake_case — SonarQube: python:S100
    [CODE SMELL] Complejidad cognitiva alta por anidación excesiva — SonarQube: python:S3776
    """
    resultado_sin_usar = []  # [CODE SMELL] Variable declarada y nunca referenciada — python:S1481

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Estudiante", "Materia", "Trabajo", "Nota", "Estado", "Categoria"])

    for estudiante in registro_est.listar():              # +1 complejidad
        trabajos = gestor.trabajos_de_estudiante(estudiante.codigo)
        if len(trabajos) > 0:                             # +1 complejidad
            for trabajo in trabajos:                      # +2 complejidad (anidado)
                if trabajo.aprobado():                    # +3 complejidad (anidado)
                    if trabajo.nota >= 4.5:               # +4 complejidad (anidado)
                        if trabajo.nota == 5.0:           # +5 complejidad (anidado)
                            categoria = "Excelente"
                            estado = "Aprobado"
                        else:
                            categoria = "Sobresaliente"
                            estado = "Aprobado"
                    else:
                        categoria = "Aprobado"
                        estado = "Aprobado"
                else:                                     # +1 complejidad
                    if trabajo.nota < 1.5:                # +4 complejidad (anidado)
                        categoria = "Reprobado Grave"
                        estado = "Reprobado"
                    else:
                        categoria = "Reprobado"
                        estado = "Reprobado"
                writer.writerow([
                    estudiante.nombre,
                    trabajo.materia.nombre,
                    trabajo.nombre_trabajo,
                    trabajo.nota,
                    estado,
                    categoria,
                ])

    return output.getvalue()
