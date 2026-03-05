# Frontend - Sistema de Cafetería

Este es el frontend HTML/CSS/JavaScript vanilla para el sistema de gestión de cafetería, enfocado en dos funcionalidades principales:

## 📋 Funcionalidades

### 1. **Hacer una Compra** (compra.html)
Permite registrar las compras de insumos a proveedores.

**Campos:**
- Seleccionar Proveedor
- ID Usuario (quien realiza la compra)
- Agregar detalles de compra:
  - Insumo
  - Cantidad
  - Costo Unitario
  - Fecha de Vencimiento (opcional)

**Características:**
- Agregar múltiples insumos a una compra
- Calcular total automáticamente
- Eliminar filas individuales

### 2. **Hacer una Venta** (venta.html)
Permite registrar las ventas de productos a clientes.

**Campos:**
- ID Usuario (el vendedor/cajero)
- Agregar detalles de venta:
  - Producto
  - Cantidad
  - Precio Unitario (se carga automáticamente)
  - Subtotal (se calcula automáticamente)

**Características:**
- Agregar múltiples productos a una venta
- Visibilización en tiempo real del total
- Calcular subtotales automáticamente
- Eliminar líneas de productos

## 🚀 Cómo Usar

### Página Principal (index.html)
Abre `index.html` en tu navegador. Verás dos botones:
- **Hacer una Compra** → redirige a `compra.html`
- **Hacer una Venta** → redirige a `venta.html`

### Configuración del API

El frontend se conecta a un backend FastAPI en `http://localhost:8000`

**Endpoints usados:**
- `GET /proveedor/` - Lista de proveedores
- `GET /insumo/` - Lista de insumos
- `POST /compra/` - Registrar una compra
- `GET /producto/` - Lista de productos
- `POST /venta/` - Registrar una venta

### Variables de Entorno (si es necesario cambiar el endpoint)

Si tu backend está en un puerto o host diferente, edita la variable `API_BASE` en los archivos HTML:

```javascript
const API_BASE = 'http://localhost:8000'; // Cambiar según necesidad
```

## 📝 Estructura de Datos Enviados

### Compra
```json
{
  "id_proveedor": 1 (opcional),
  "id_usuario": 1,
  "detalles": [
    {
      "id_insumo": 1,
      "cantidad": 10.5,
      "costo_unitario": 2.50,
      "fecha_vencimiento": "2026-12-31" (opcional)
    }
  ]
}
```

### Venta
```json
{
  "id_usuario": 1,
  "detalles": [
    {
      "id_producto": 1,
      "cantidad": 2,
      "precio_unitario": 15.00
    }
  ]
}
```

## 🎨 Estilos

El frontend utiliza CSS vanilla con estilos básicos pero funcionales:
- Tablas con bordes
- Inputs con estilos simples
- Botones con padding y márgenes
- Diseño responsive (centrado en pantallas pequeñas)

## ✅ Validaciones

- **Compra:** Se requiere al menos un insumo antes de registrar
- **Venta:** Se requiere al menos un producto antes de registrar
- Todos los campos obligatorios están marcados con `required`

## 📱 Compatibilidad

- Navegadores modernos (Chrome, Firefox, Edge, Safari)
- Responsive para pantallas pequeñas
- Sin dependencias externas (vanilla JavaScript)

## 🔧 Notas Técnicas

- Las fechas de vencimiento se capturan en formato ISO (YYYY-MM-DD)
- Los montos se calculan con precisión decimal (hasta 2 decimales)
- Las respuestas del servidor se manejan con try-catch
- CORS debe estar habilitado en el backend (ya configurado en FastAPI)

---

**Última actualización:** 5 de marzo de 2026