import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from config.conexionDB import get_conexion
from config.jwt import create_access_token

router = APIRouter()


# ---------- Modelos ----------

class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    id_usuario: int
    id_personal: int
    nombre: str
    rol: str
    id_rol: int


# ---------- Endpoint ----------

@router.post("/login", response_model=LoginResponse)
async def login(datos: LoginRequest, conn=Depends(get_conexion)):
    """
    Autentica un usuario por email y contraseña.
    Retorna un JWT con datos del usuario y su rol.

    Solo usuarios activos cuyo personal también esté activo pueden ingresar.
    """
    consulta = """
        SELECT
            u.id_usuario,
            u.password_hash,
            u.activo       AS usuario_activo,
            p.id_personal,
            p.nombres      AS nombres,
            p.primer_apellido,
            p.activo       AS personal_activo,
            r.id_rol,
            r.nombre       AS rol
        FROM usuario u
        JOIN personal p ON p.id_personal = u.id_personal
        JOIN rol r      ON r.id_rol      = p.id_rol
        WHERE u.email = %s;
    """

    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, (datos.email,))
            usuario = await cursor.fetchone()

        # 1. Usuario no encontrado → misma respuesta genérica (no revelar si el email existe)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas"
            )

        # 2. Verificar contraseña con bcrypt
        password_ok = bcrypt.checkpw(
            datos.password.encode(),
            usuario["password_hash"].encode()
        )
        if not password_ok:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas"
            )

        # 3. Verificar que la cuenta esté activa
        if not usuario["usuario_activo"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cuenta de usuario deshabilitada. Contacta al administrador."
            )

        # 4. Verificar que el empleado esté activo
        if not usuario["personal_activo"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El empleado está inactivo. Contacta al administrador."
            )

        # 5. Generar JWT
        nombre_completo = f"{usuario['nombres']} {usuario['primer_apellido']}"
        token_data = {
            "sub": str(usuario["id_usuario"]),
            "id_usuario": usuario["id_usuario"],
            "id_personal": usuario["id_personal"],
            "nombre": nombre_completo,
            "rol": usuario["rol"],
            "id_rol": usuario["id_rol"],
            "email": datos.email,
        }
        token = create_access_token(token_data)

        return LoginResponse(
            access_token=token,
            id_usuario=usuario["id_usuario"],
            id_personal=usuario["id_personal"],
            nombre=nombre_completo,
            rol=usuario["rol"],
            id_rol=usuario["id_rol"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
