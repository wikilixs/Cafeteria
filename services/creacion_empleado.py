import logging
import bcrypt
from fastapi import HTTPException

logger = logging.getLogger(__name__)


async def crear_empleado(conn, id_rol, ci, nombres, primer_apellido, segundo_apellido,
                         fecha_nacimiento, telefono, fecha_ingreso, crear_usuario=False):
    """
    Crea un empleado en la tabla personal.
    Si crear_usuario=True, también crea un usuario con email y contraseña autogenerados.
    """
    try:
        cur = conn.cursor()

        # 1. Insertar personal
        await cur.execute(
            """
            INSERT INTO personal
            (id_rol, ci, nombres, primer_apellido, segundo_apellido, fecha_nacimiento, telefono, activo, fecha_ingreso)
            VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE, %s)
            RETURNING id_personal
            """,
            (id_rol, ci, nombres, primer_apellido, segundo_apellido, fecha_nacimiento, telefono, fecha_ingreso)
        )
        row = await cur.fetchone()
        id_personal = row["id_personal"]

        resultado = {
            "id_personal": id_personal,
            "ci": ci
        }

        # 2. Crear usuario si se solicita
        if crear_usuario:
            nombre_limpio = nombres.lower().replace(" ", "")
            apellido_limpio = primer_apellido.lower().replace(" ", "")
            email = f"{nombre_limpio}.{apellido_limpio}@cafeteria.com"
            password = str(ci)[-6:]

            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

            await cur.execute(
                """
                INSERT INTO usuario (id_personal, email, password_hash, activo)
                VALUES (%s, %s, %s, TRUE)
                RETURNING id_usuario
                """,
                (id_personal, email, password_hash)
            )
            row2 = await cur.fetchone()
            resultado["id_usuario"] = row2["id_usuario"]
            resultado["email"] = email
            resultado["password"] = password

        await conn.commit()
        return resultado

    except HTTPException:
        await conn.rollback()
        raise
    except Exception as e:
        await conn.rollback()
        logger.error(f"Error al crear empleado: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def crear_usuario_para_empleado(conn, id_personal):
    """
    Crea un usuario autocreando email y contraseña basado en datos del empleado.
    Email: nombre.apellido@cafeteria.com
    Contraseña: CI (últimos 6 dígitos)
    """
    try:
        cur = conn.cursor()

        # 1. Obtener datos del empleado
        await cur.execute(
            "SELECT nombres, primer_apellido, segundo_apellido, ci FROM personal WHERE id_personal = %s",
            (id_personal,)
        )
        empleado = await cur.fetchone()

        if not empleado:
            raise HTTPException(status_code=404, detail="Empleado no encontrado")

        nombres = empleado["nombres"]
        primer_apellido = empleado["primer_apellido"]
        ci = empleado["ci"]

        # 2. Autogenerar email y contraseña
        nombre_limpio = nombres.lower().replace(" ", "")
        apellido_limpio = primer_apellido.lower().replace(" ", "")
        email = f"{nombre_limpio}.{apellido_limpio}@cafeteria.com"
        password = str(ci)[-6:]

        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        # 3. Insertar usuario
        await cur.execute(
            """
            INSERT INTO usuario (id_personal, email, password_hash, activo)
            VALUES (%s, %s, %s, TRUE)
            RETURNING id_usuario
            """,
            (id_personal, email, password_hash)
        )
        row = await cur.fetchone()

        await conn.commit()
        return {
            "id_usuario": row["id_usuario"],
            "email": email,
            "password": password,
            "id_personal": id_personal
        }

    except HTTPException:
        raise
    except Exception as e:
        await conn.rollback()
        logger.error(f"Error al crear usuario para empleado {id_personal}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
