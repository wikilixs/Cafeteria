# Guía de Pruebas con Postman

## Instalación de Postman
1. Descarga Postman desde: https://www.postman.com/downloads/
2. Instálalo y abre la aplicación
3. Crea una cuenta (opcional) o usa sin cuenta

---

## Configuración Base

### URL Base
```
http://localhost:8000
```

Tu servidor debe estar corriendo en el puerto 8000 (FastAPI por defecto)

---

## 1. CREAR EMPLEADO

**Método**: POST  
**URL**: `http://localhost:8000/personal/crear`

**Headers**:
```
Content-Type: application/json
```

**Body (JSON) - SIN USUARIO**:
```json
{
  "id_rol": 1,
  "ci": 1234567890,
  "nombres": "Juan",
  "primer_apellido": "Pérez",
  "segundo_apellido": "García",
  "fecha_nacimiento": "1990-05-15",
  "telefono": 76543210,
  "fecha_ingreso": "2026-03-08",
  "crear_usuario": false
}
```

**Body (JSON) - CON USUARIO AUTOGENERADO** (recomendado):
```json
{
  "id_rol": 1,
  "ci": 1234567890,
  "nombres": "Juan",
  "primer_apellido": "Pérez",
  "segundo_apellido": "García",
  "fecha_nacimiento": "1990-05-15",
  "telefono": 76543210,
  "fecha_ingreso": "2026-03-08",
  "crear_usuario": true
}
```

**Respuesta esperada (sin usuario)**:
```json
{
  "id_personal": 1,
  "ci": 1234567890
}
```

**Respuesta esperada (con usuario)**:
```json
{
  "id_personal": 1,
  "ci": 1234567890,
  "id_usuario": 1,
  "email": "juan.perez@cafeteria.com",
  "password": "234567"
}
```

**Nota**: 
- Si `crear_usuario: true`, se crea automáticamente un usuario con:
  - Email: nombre.apellido@cafeteria.com
  - Contraseña: últimos 6 dígitos del CI

---

## 2. CREAR USUARIO (para un empleado)

**Método**: POST  
**URL**: `http://localhost:8000/usuario/crear`

**Headers**:
```
Content-Type: application/json
```

**Body (JSON)**:
```json
{
  "id_personal": 1
}
```

**Respuesta esperada**:
```json
{
  "id_usuario": 1,
  "email": "juan.perez@cafeteria.com",
  "password": "234567",
  "id_personal": 1
}
```

**NOTA**: El email y contraseña se generan automáticamente:
- Email: nombre.apellido@cafeteria.com
- Contraseña: últimos 6 dígitos del CI

---

## 3. REGISTRAR COMPRA

**Método**: POST  
**URL**: `http://localhost:8000/compra/`

**Headers**:
```
Content-Type: application/json
```

> ⚠️ **`id_usuario`** debe ser el ID de la tabla `usuario` (no de `personal`).  
> Si el empleado no tiene usuario, créalo primero con `POST /personal/crear` usando `crear_usuario: true`.

> ℹ️ **`id_insumo` es automático**: en los detalles se pasa el `nombre` del insumo.  
> Si el insumo **no existe** → se crea automáticamente (requiere `unidad`).  
> Si el insumo **ya existe** → solo se actualiza su stock (`unidad` se ignora).

**Body (JSON) - Insumos nuevos**:
```json
{
  "id_proveedor": 1,
  "id_usuario": 1,
  "detalles": [
    {
      "nombre": "Harina",
      "unidad": "kg",
      "cantidad": 10,
      "costo_unitario": 5.50
    },
    {
      "nombre": "Azúcar",
      "unidad": "kg",
      "cantidad": 20,
      "costo_unitario": 2.75
    }
  ]
}
```

**Body (JSON) - Insumos ya existentes** (`unidad` opcional):
```json
{
  "id_proveedor": 1,
  "id_usuario": 1,
  "detalles": [
    {
      "nombre": "Harina",
      "cantidad": 5,
      "costo_unitario": 5.50
    }
  ]
}
```

**Respuesta esperada**:
```json
{
  "id_compra": 5,
  "insumos": [
    {
      "id_insumo": 1,
      "nombre": "Harina",
      "unidad": "kg",
      "stock_actual": 15.0,
      "cantidad_comprada": 10.0,
      "costo_unitario": 5.50
    }
  ]
}
```

---

## 4. REGISTRAR VENTA

**Método**: POST  
**URL**: `http://localhost:8000/venta/`

**Headers**:
```
Content-Type: application/json
```

> ⚠️ **`id_usuario`** debe ser el ID de la tabla `usuario` (no de `personal`).  
> **`id_cliente`** es opcional. Si no se manda (o es `null`), se pasa `nombre_cliente` y opcionalmente `nit_cliente` para crear el cliente automáticamente.

**Body (JSON) - CLIENTE EXISTENTE**:
```json
{
  "id_usuario": 1,
  "id_cliente": 2,
  "id_estado": 1,
  "metodo_pago": "EFECTIVO",
  "detalles": [
    {"id_producto": 1, "cantidad": 2, "precio_unitario": 25.00},
    {"id_producto": 3, "cantidad": 1, "precio_unitario": 30.00}
  ]
}
```

**Body (JSON) - CLIENTE NUEVO (se crea al vuelo)**:
```json
{
  "id_usuario": 1,
  "id_cliente": null,
  "nombre_cliente": "María López",
  "nit_cliente": "4567890",
  "id_estado": 1,
  "metodo_pago": "QR",
  "detalles": [
    {"id_producto": 1, "cantidad": 2, "precio_unitario": 25.00}
  ]
}
```

**Respuesta esperada**:
```json
{
  "id_venta": 10,
  "id_cliente": 3,
  "total": 80.0
}
```

---

## CÓMO HACERLO EN POSTMAN (Paso a Paso)

### Paso 1: Abrir Postman
1. Abre la aplicación Postman
2. Haz clic en "Create a request" o "+" para nueva pestaña

### Paso 2: Configurar la solicitud
1. **Selecciona el método**: Dropdown "GET" → elige "POST"
2. **Ingresa la URL**: Copia la URL base (ej: `http://localhost:8000/empleados/crear`)
3. **Headers**: 
   - Haz clic en la pestaña "Headers"
   - Agrega: Key: `Content-Type` Value: `application/json`

### Paso 3: Agregar Body (cuerpo de la solicitud)
1. Haz clic en la pestaña "Body"
2. Selecciona "raw"
3. Asegúrate que el idioma esté en "JSON" (dropdown a la derecha)
4. Pega el JSON del ejemplo
5. Modifica los valores según necesites

### Paso 4: Enviar la solicitud
1. Haz clic en el botón azul "Send"
2. Abajo verás la respuesta en "Response"

### Paso 5: Ver respuesta
- **Status**: Muestra el código HTTP (200 = OK, 400 = Error, 500 = Error servidor)
- **Body**: Muestra la respuesta JSON

---

## COLECCIÓN LISTA PARA USAR

Puedes crear una "Colección" en Postman para guardar todas tus solicitudes:

1. Haz clic en "Collections" (lado izquierdo)
2. Clic en "+" para nueva colección
3. Nombra: "Cafetería API"
4. Crea carpetas:
   - Empleados
   - Usuarios
   - Compras
   - Ventas
5. En cada carpeta, agrega las solicitudes correspondientes

---

## ALTERNATIVAMENTE: Usar curl en Terminal

Si prefieres línea de comandos, usa `curl`:

### Crear empleado (CON usuario automático):
```bash
curl -X POST http://localhost:8000/personal/crear \
  -H "Content-Type: application/json" \
  -d '{
    "id_rol": 1,
    "ci": 1234567890,
    "nombres": "Juan",
    "primer_apellido": "Pérez",
    "segundo_apellido": "García",
    "fecha_nacimiento": "1990-05-15",
    "telefono": 76543210,
    "fecha_ingreso": "2026-03-08",
    "crear_usuario": true
  }'
```

### Registrar compra:
```bash
curl -X POST http://localhost:8000/compra/ \
  -H "Content-Type: application/json" \
  -d '{
    "id_proveedor": 1,
    "id_usuario": 1,
    "detalles": [
      {"id_insumo": 1, "cantidad": 10, "costo_unitario": 5.50}
    ]
  }'
```

### Registrar venta:
```bash
curl -X POST http://localhost:8000/venta/ \
  -H "Content-Type: application/json" \
  -d '{
    "id_usuario": 1,
    "id_cliente": 2,
    "id_estado": 1,
    "metodo_pago": "EFECTIVO",
    "detalles": [
      {"id_producto": 1, "cantidad": 2, "precio_unitario": 25.00}
    ]
  }'
```

---

## ERRORES COMUNES

| Error | Causa | Solución |
|-------|-------|----------|
| `Connection refused` | Servidor no está corriendo | Ejecuta `python main.py` o `uvicorn main:app --reload` |
| `404 Not Found` | URL incorrecta | Verifica la URL y el método (GET/POST) |
| `400 Bad Request` | JSON inválido | Verifica la sintaxis del JSON en el body |
| `500 Internal Server Error` | Error en el servidor | Revisa los logs del servidor |

---

## ENDPOINTS DISPONIBLES

### Personal
- `GET /personal/` - Listar todos
- `GET /personal/{id}` - Obtener uno
- `POST /personal/crear` - Crear (con opción de crear usuario)
- `PUT /personal/{id}` - Actualizar
- `DELETE /personal/{id}` - Eliminar

### Usuario  
- `GET /usuario/` - Listar todos
- `GET /usuario/{id}` - Obtener uno
- `POST /usuario/` - Crear manual
- `POST /usuario/crear` - Crear con email/contraseña autogenerados
- `PUT /usuario/{id}` - Actualizar
- `DELETE /usuario/{id}` - Eliminar

### Compra
- `GET /compra/` - Listar todas
- `GET /compra/{id}` - Obtener una
- `POST /compra/` - Registrar compra con detalles
- `PUT /compra/{id}` - Actualizar
- `DELETE /compra/{id}` - Eliminar

### Venta
- `GET /venta/` - Listar todas
- `GET /venta/{id}` - Obtener una
- `POST /venta/` - Registrar venta con detalles
- `PUT /venta/{id}` - Actualizar
- `DELETE /venta/{id}` - Eliminar

---

## NOTAS IMPORTANTES

- **Crear Empleado**: Todos los campos de personal son **requeridos**. El parámetro `crear_usuario` es opcional (por defecto `false`)
- **Crear Usuario**: Se puede crear automáticamente al crear empleado (`crear_usuario: true`) o manualmente después con `POST /usuario/crear`
- **`id_usuario` en Compra y Venta**: Es el ID de la tabla `usuario` (no de `personal`). El empleado debe tener usuario creado primero
- **Cliente en Venta**: Pasar `id_cliente` con un cliente existente, o `id_cliente: null` + `nombre_cliente` para crear uno nuevón
- **Registrar Compra/Venta**: Requieren al menos un elemento en `detalles`
- Las fechas deben estar en formato `YYYY-MM-DD`
- Asegúrate que el servidor esté corriendo con `uv run uvicorn main:app --reload`
