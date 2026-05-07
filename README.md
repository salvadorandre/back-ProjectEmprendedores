
### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd back-ProjectEmprendedores
```

### 2. Crear y activar el entorno virtual

```bash
# Crear entorno virtual
python -m venv .venv

# Activar (macOS / Linux)
source .venv/bin/activate

# Activar (Windows)
.venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env
```

Edita el archivo `.env` con credenciales de Mysql


```sql
CREATE DATABASE emprendedores_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 6. Ejecutar migraciones

```bash
python manage.py migrate
```

### 7. Crear superusuario (opcional)

```bash
python manage.py createsuperuser
```

### 8. Levantar el servidor

```bash
python manage.py runserver
```

El servidor estará disponible en: `http://127.0.0.1:8000/`

## Documentación de la API


| Recurso | URL |
|---|---|
| Swagger UI | `http://127.0.0.1:8000/api/docs/` |
| Schema OpenAPI | `http://127.0.0.1:8000/api/schema/` |

## Estructura del proyecto

```
back-ProjectEmprendedores/
├── configEmprendedores/     # Configuración principal de Django
│   ├── __init__.py          # Configuración de PyMySQL
│   ├── settings.py          # Settings del proyecto
│   ├── urls.py              # URLs raíz
│   ├── wsgi.py
│   └── asgi.py
├── autentication/           # App de autenticación
│   ├── models.py            # Modelo Usuario personalizado
│   ├── serializers.py       # Serializadores de usuario
│   ├── views.py             # Endpoints de registro/login/logout
│   └── urls.py
├── clinix/                  # App principal clínica
│   ├── models.py            # Paciente, Doctor, Medicamento, Tratamiento...
│   ├── serializers.py       # Serializadores de modelos clínicos
│   ├── api.py               # Endpoints CRUD
│   └── urls.py
├── .env.example             # Plantilla de variables de entorno
├── .gitignore
├── requirements.txt         # Dependencias del proyecto
├── manage.py
└── README.md
```

## Endpoints principales

### Autenticación
| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/api/auth/register/` | Registro de usuario |
| POST | `/api/auth/register/doctor/` | Registro de doctor |
| POST | `/api/auth/register/paciente/` | Registro de paciente |
| POST | `/api/auth/login/` | Inicio de sesión |
| POST | `/api/auth/logout/` | Cerrar sesión |
| POST | `/api/auth/token/refresh/` | Refrescar token JWT |

### Clinix
| Método | Endpoint | Descripción |
|---|---|---|
| GET/POST | `/api/clinix/medicamentos/` | Listar / Crear medicamentos |
| GET/PUT/DELETE | `/api/clinix/medicamentos/<id>/` | Detalle / Actualizar / Eliminar |
| GET/POST | `/api/clinix/tratamientos/` | Listar / Crear tratamientos |
| GET/PUT/DELETE | `/api/clinix/tratamientos/<uuid>/` | Detalle / Actualizar / Eliminar |
| GET/POST | `/api/clinix/paciente-tratamiento/` | Listar / Crear asignaciones |
| GET/PUT/DELETE | `/api/clinix/paciente-tratamiento/<id>/` | Detalle / Actualizar / Eliminar |
| GET/POST | `/api/clinix/tratamiento-medicamento/` | Listar / Crear asignaciones |
| GET/PUT/DELETE | `/api/clinix/tratamiento-medicamento/<id>/` | Detalle / Actualizar / Eliminar |

> **Nota:** Todos los endpoints requieren autenticación JWT. Envía el header `Authorization: Bearer <access_token>`.
