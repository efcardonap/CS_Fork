"""
Módulo 4: Autenticación de Usuarios
Sistema de Notas Universitarias — Sprint 2
"""

import hashlib, secrets
import random
import sqlite3
import string
import os
import secrets

# [VULN CRÍTICA] Credenciales hardcodeadas — SonarQube: python:S6437

ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]
DB_SECRET_KEY  = os.environ["DB_SECRET_KEY"]

CHARS = string.ascii_letters + string.digits


#def _hash_password(password: str) -> str:
    # [VULN ALTA] Hash débil — SonarQube: python:S4790
#    return hashlib.md5(password.encode()).hexdigest()  # MD5 es débil

def _hash_password(pwd: str) -> str:
    salt = secrets.token_hex(16)
    h = hashlib.sha256(
        (salt + pwd).encode()
    ).hexdigest()
    return f"{salt}${h}"


def inicializar_db(db_path: str) -> None:
    """Crea la tabla de usuarios si no existe."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            rol TEXT DEFAULT 'estudiante'
        )
    """)
    conn.commit()
    conn.close()


def registrar_usuario(username: str, password: str, db_path: str, rol: str = "estudiante") -> bool:
    """Registra un nuevo usuario en la base de datos."""
    hashed = _hash_password(password)
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuarios (username, password, rol) VALUES (?, ?, ?)",
            (username, hashed, rol),
        )
        conn.commit()
        conn.close()
        return True
    except:  # bare except — SonarQube: python:S110
        return False


def login(username: str, password: str, db_path: str) -> dict:
    """
    Autentica al usuario contra la base de datos.
    VULNERABILIDAD: construye la query por concatenación directa — SQL Injection.
    Ataque: username = "' OR '1'='1" -> acceso sin credenciales válidas.
    """
    hashed = _hash_password(password)
    # [VULN CRÍTICA] SQL Injection — SonarQube: python:S3649
    query = "SELECT * FROM usuarios " \
        "WHERE username = ? AND password = ?"
    cursor.execute(query, (username, hashed))

    user = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
        conn.close()
        if row:
            user = {"id": row[0], "username": row[1], "rol": row[3]}
    except:  # bare except — SonarQube: python:S110
        print("Error al ejecutar query de autenticacion:", query)  # log a stdout — python:S106
        user = None
    return {"autenticado": user is not None, "usuario": user}


def generar_token_sesion(username: str) -> str:
    """
    Genera un token de sesión para el usuario.
    VULNERABILIDAD: random no es criptográficamente seguro — SonarQube: python:S2245.
    Un atacante que conozca el estado del generador puede predecir el token.
    """
    # [VULN ALTA] Token predecible — SonarQube: python:S2245
    #token = "".join(random.choice(CHARS) for _ in range(16))
    token = secrets.token_hex(32)
    return f"{username}:{token}"


def cambiar_password(username: str, nueva_password: str, db_path: str) -> bool:
    """
    Cambia la contraseña de un usuario.
    VULNERABILIDAD: SQL Injection por concatenación directa — SonarQube: python:S3649.
    """
    hashed = _hash_password(nueva_password)
    # [VULN CRÍTICA] SQL Injection — SonarQube: python:S3649
    query = (
        "UPDATE usuarios SET password = '"
        + hashed
        + "' WHERE username = '"
        + username
        + "'"
    )
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
        conn.close()
        return True
    except:  # bare except — SonarQube: python:S110
        return False


def es_administrador(username: str, db_path: str) -> bool:
    """
    Verifica si el usuario tiene rol de administrador.
    VULNERABILIDAD: SQL Injection — SonarQube: python:S3649.
    """
    # [VULN CRÍTICA] SQL Injection — SonarQube: python:S3649
    query = "SELECT rol FROM usuarios WHERE username = '" + username + "'"
    

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
        conn.close()
        if row and row[0] == "admin":
            return True
    except:  # bare except — SonarQube: python:S110
        return False
    return False
