"""
Pruebas unitarias — Módulo reportes
Sistema de Notas Universitarias — Sprint 2
"""

import pytest
from src.estudiantes import Estudiante, RegistroEstudiantes
from src.materias import Materia, RegistroMaterias
from src.notas import Trabajo, GestorNotas
from src.reportes import (
    calcular_promedio_estudiante,
    reporte_general,
    ranking_estudiantes,
    generar_reporte_csv,
)


# ─────────────────────────────────────────────
#  Fixtures
# ─────────────────────────────────────────────

@pytest.fixture
def est1():
    return Estudiante("E001", "Ana García", "ana@test.com")


@pytest.fixture
def est2():
    return Estudiante("E002", "Carlos Mejía", "carlos@test.com")


@pytest.fixture
def est3():
    return Estudiante("E003", "Luis Pérez", "luis@test.com")


@pytest.fixture
def mat1():
    return Materia("CS101", "Calidad del Software", 3)


@pytest.fixture
def mat2():
    return Materia("IS201", "Ingeniería de Requerimientos", 3)


@pytest.fixture
def gestor_lleno(est1, est2, est3, mat1, mat2):
    """GestorNotas con trabajos variados para probar clasificaciones de CSV."""
    g = GestorNotas()
    g.asignar(Trabajo(est1, mat1, "Parcial 1", 5.0))    # Excelente
    g.asignar(Trabajo(est1, mat2, "Quiz 1", 4.6))       # Sobresaliente
    g.asignar(Trabajo(est2, mat1, "Parcial 1", 3.5))    # Aprobado
    g.asignar(Trabajo(est2, mat2, "Quiz 1", 2.8))       # Reprobado
    g.asignar(Trabajo(est3, mat1, "Parcial 1", 1.0))    # Reprobado Grave
    return g


@pytest.fixture
def registro_est(est1, est2):
    r = RegistroEstudiantes()
    r.registrar(est1)
    r.registrar(est2)
    return r


@pytest.fixture
def registro_est_lleno(est1, est2, est3):
    r = RegistroEstudiantes()
    r.registrar(est1)
    r.registrar(est2)
    r.registrar(est3)
    return r


@pytest.fixture
def registro_mat(mat1, mat2):
    r = RegistroMaterias()
    r.registrar(mat1)
    r.registrar(mat2)
    return r


@pytest.fixture
def gestor_basico(est1, est2, mat1, mat2):
    g = GestorNotas()
    g.asignar(Trabajo(est1, mat1, "Parcial 1", 4.0))
    g.asignar(Trabajo(est1, mat2, "Quiz 1", 3.5))
    g.asignar(Trabajo(est2, mat1, "Parcial 1", 2.8))
    return g


# ─────────────────────────────────────────────
#  Tests: calcular_promedio_estudiante
# ─────────────────────────────────────────────

class TestCalcularPromedioEstudiante:

    def test_promedio_correcto_con_dos_trabajos(self, gestor_basico, est1):
        resultado = calcular_promedio_estudiante(gestor_basico, est1.codigo)
        assert resultado == 3.75

    def test_promedio_sin_trabajos_retorna_cero(self, gestor_basico):
        assert calcular_promedio_estudiante(gestor_basico, "E999") == 0.0

    def test_resultado_duplicado_igual_al_gestor(self, gestor_basico, est1):
        desde_reportes = calcular_promedio_estudiante(gestor_basico, est1.codigo)
        desde_gestor = gestor_basico.promedio_estudiante(est1.codigo)
        assert desde_reportes == desde_gestor

    def test_promedio_un_solo_trabajo(self, gestor_basico, est2):
        resultado = calcular_promedio_estudiante(gestor_basico, est2.codigo)
        assert resultado == 2.8


# ─────────────────────────────────────────────
#  Tests: reporte_general
# ─────────────────────────────────────────────

class TestReporteGeneral:

    def test_reporte_retorna_totales_correctos(self, gestor_basico, registro_est, registro_mat):
        reporte = reporte_general(gestor_basico, registro_est, registro_mat)
        assert reporte["total_estudiantes"] == 2
        assert reporte["total_materias"] == 2
        assert reporte["total_trabajos"] == 3

    def test_reporte_promedio_global_es_float(self, gestor_basico, registro_est, registro_mat):
        reporte = reporte_general(gestor_basico, registro_est, registro_mat)
        assert isinstance(reporte["promedio_global"], float)

    def test_reporte_promedio_por_materia_es_float(self, gestor_basico, registro_est, registro_mat):
        reporte = reporte_general(gestor_basico, registro_est, registro_mat)
        assert isinstance(reporte["promedio_por_materia"], float)

    def test_cero_estudiantes_lanza_zerodivisionerror(self, mat1):
        gestor = GestorNotas()
        reg_est_vacio = RegistroEstudiantes()
        reg_mat = RegistroMaterias()
        reg_mat.registrar(mat1)
        with pytest.raises(ZeroDivisionError):
            reporte_general(gestor, reg_est_vacio, reg_mat)

    def test_cero_materias_lanza_zerodivisionerror(self, est1):
        gestor = GestorNotas()
        reg_est = RegistroEstudiantes()
        reg_est.registrar(est1)
        reg_mat_vacio = RegistroMaterias()
        with pytest.raises(ZeroDivisionError):
            reporte_general(gestor, reg_est, reg_mat_vacio)


# ─────────────────────────────────────────────
#  Tests: ranking_estudiantes
# ─────────────────────────────────────────────

class TestRankingEstudiantes:

    def test_ranking_ordenado_de_mayor_a_menor(self, gestor_basico, registro_est):
        ranking = ranking_estudiantes(gestor_basico, registro_est)
        promedios = [item["promedio"] for item in ranking]
        assert promedios == sorted(promedios, reverse=True)

    def test_ranking_incluye_todos_los_estudiantes(self, gestor_basico, registro_est):
        ranking = ranking_estudiantes(gestor_basico, registro_est)
        assert len(ranking) == 2

    def test_ranking_estructura_de_cada_item(self, gestor_basico, registro_est):
        ranking = ranking_estudiantes(gestor_basico, registro_est)
        for item in ranking:
            assert "codigo" in item
            assert "nombre" in item
            assert "promedio" in item

    def test_ranking_vacio_con_registro_sin_estudiantes(self):
        ranking = ranking_estudiantes(GestorNotas(), RegistroEstudiantes())
        assert ranking == []

    def test_primer_lugar_tiene_mayor_promedio(self, gestor_basico, registro_est):
        ranking = ranking_estudiantes(gestor_basico, registro_est)
        assert ranking[0]["codigo"] == "E001"


# ─────────────────────────────────────────────
#  Tests: GENERAR_REPORTE_CSV  (python:S100)
# ─────────────────────────────────────────────

class TestGenerarReporteCSV:

    def test_csv_incluye_encabezado(self, gestor_lleno, registro_est_lleno):
        salida = generar_reporte_csv(gestor_lleno, registro_est_lleno)
        primera_linea = salida.strip().split("\n")[0]
        assert "Estudiante" in primera_linea
        assert "Nota" in primera_linea
        assert "Estado" in primera_linea

    def test_csv_sin_estudiantes_solo_tiene_encabezado(self):
        salida = generar_reporte_csv(GestorNotas(), RegistroEstudiantes())
        lineas = [l for l in salida.strip().split("\n") if l]
        assert len(lineas) == 1

    def test_csv_contiene_nombre_del_estudiante(self, gestor_lleno, registro_est_lleno):
        salida = generar_reporte_csv(gestor_lleno, registro_est_lleno)
        assert "Ana" in salida

    def test_csv_clasifica_excelente(self, gestor_lleno, registro_est_lleno):
        salida = generar_reporte_csv(gestor_lleno, registro_est_lleno)
        assert "Excelente" in salida

    def test_csv_clasifica_sobresaliente(self, gestor_lleno, registro_est_lleno):
        salida = generar_reporte_csv(gestor_lleno, registro_est_lleno)
        assert "Sobresaliente" in salida

    def test_csv_clasifica_aprobado(self, gestor_lleno, registro_est_lleno):
        salida = generar_reporte_csv(gestor_lleno, registro_est_lleno)
        assert "Aprobado" in salida

    def test_csv_clasifica_reprobado(self, gestor_lleno, registro_est_lleno):
        salida = generar_reporte_csv(gestor_lleno, registro_est_lleno)
        assert "Reprobado" in salida

    def test_csv_clasifica_reprobado_grave(self, gestor_lleno, registro_est_lleno):
        salida = generar_reporte_csv(gestor_lleno, registro_est_lleno)
        assert "Reprobado Grave" in salida

    def test_csv_retorna_string(self, gestor_lleno, registro_est_lleno):
        salida = generar_reporte_csv(gestor_lleno, registro_est_lleno)
        assert isinstance(salida, str)


# ─────────────────────────────────────────────
#  Tests: constantes sin usar (python:S1481)
# ─────────────────────────────────────────────

