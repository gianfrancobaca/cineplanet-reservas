# Cineplanet Reservas — prototipo de microservicios con Docker

Prototipo académico de un sistema de reserva de asientos para cine, construido con microservicios en contenedores. Su objetivo es demostrar cómo se comporta un sistema ante muchas compras simultáneas y cómo evitar la **doble venta** de un mismo asiento (condición de carrera).

> **Aviso:** proyecto académico del curso *Sistemas Operativos* (USIL, 2026-2, Grupo 21). No está afiliado a Cineplanet ni a Cineplex S.A. Todos los datos (películas, funciones, asientos) son **datos de prueba ficticios**.

## Escenario de estudio

Durante la preventa de un estreno, muchas personas intentan comprar entradas al mismo tiempo. Este prototipo plantea ese escenario para estudiar dos problemas:

1. **Concurrencia:** dos clientes que compran el mismo asiento a la vez pueden terminar con una doble venta si el sistema no se sincroniza.
2. **Escalabilidad:** atender más peticiones levantando varias copias (réplicas) de un servicio.

El escenario es planteado por el equipo; no se basa en datos internos de Cineplanet.

## Estado del proyecto

| Fase | Contenido | Estado |
|---|---|---|
| 1 | Servicio `reservas` (FastAPI) en Docker Compose, ruta `/salud` | ✅ Terminada |
| 2A | Servicio `db` (PostgreSQL 18.6) con credenciales en `.env` y volumen persistente | ✅ Terminada |
| 2B | Tablas de funciones, asientos y reservas | 🔄 En curso |
| 2C | Conexión `reservas` ↔ `db` con chequeo de salud | ⏳ Pendiente |
| 2D | Demo de doble venta (ruta insegura) y su corrección (ruta segura) | ⏳ Pendiente |
| 3 | Nginx como balanceador + réplicas + pruebas de carga con Locust | ⏳ Pendiente |
| 4 | Servicio `catalogo` + despliegue en Azure Container Apps | ⏳ Pendiente |

## Arquitectura propuesta

```
           Cliente / Locust
                  │
             localhost:8000
                  │
           ┌─────────────┐
           │    nginx    │   reparte el tráfico (fase 3)
           └──┬───────┬──┘
              │       │
   ┌──────────┴──┐  ┌─┴──────────┐
   │ reservas ×N │  │  catalogo  │   microservicios (FastAPI)
   └──────┬──────┘  └─────┬──────┘
          └───────┬───────┘
            ┌─────┴─────┐
            │    db     │   PostgreSQL 18.6 (solo en la red interna de Docker)
            └───────────┘
```

| Servicio | Tipo | Responsabilidad |
|---|---|---|
| `reservas` | Microservicio | Estado de los asientos y venta de entradas |
| `catalogo` | Microservicio | Películas, cines y funciones |
| `db` | Infraestructura | Almacenamiento (PostgreSQL) |
| `nginx` | Infraestructura | Balanceo de carga entre réplicas |

Los servicios están en la misma red de Docker Compose y se encuentran por su nombre de servicio (por ejemplo, `reservas` se conectará a la base usando el nombre `db`).

## Tecnologías

- **Python 3.13**, **FastAPI** y **uvicorn** (servidor ASGI)
- **Docker** y **Docker Compose**
- **PostgreSQL 18.6** (imagen oficial `postgres:18.6-trixie`)
- **Nginx**, **Locust** y **pandas** (fase 3)
- **Azure Container Apps** (fase 4)

## Cómo ejecutarlo

Requisito: tener [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y abierto.

```bash
git clone https://github.com/gianfrancobaca/cineplanet-reservas.git
cd cineplanet-reservas
```

Crea tu archivo de credenciales a partir de la plantilla y cambia los valores:

```bash
cp .env.example .env
```

El archivo `.env` no se sube al repositorio (está en `.gitignore`); `.env.example` solo muestra qué variables hacen falta.

Levanta los servicios:

```bash
docker compose up --build -d
docker compose ps
```

Comprueba la API:

```bash
curl localhost:8000/salud
# {"estado":"ok"}
```

La documentación interactiva de la API queda disponible en `http://localhost:8000/docs`.

Comprueba que la base de datos terminó de arrancar:

```bash
docker compose logs db | grep "ready to accept connections"
```

En el primer arranque aparecen dos líneas "ready": la primera es un servidor temporal que la imagen usa para crear la base de datos; la segunda es el servidor definitivo.

Para detener los contenedores:

```bash
docker compose down      # elimina los contenedores; los datos de la base se conservan en el volumen
docker compose down -v   # también elimina el volumen: se pierden los datos
```

## Estructura del repositorio

```
cineplanet-reservas/
├── docker-compose.yml       # define y conecta los servicios (reservas y db)
├── .env.example             # plantilla de credenciales (sin valores reales)
├── .gitignore               # excluye .env, .venv/, __pycache__/, etc.
├── README.md
└── servicios/
    └── reservas/
        ├── Dockerfile       # receta de la imagen del servicio
        ├── requirements.txt # dependencias con versiones fijas
        └── app/
            └── main.py      # aplicación FastAPI
```

## Decisiones de diseño

- **PostgreSQL 18.6 y no 19:** cuando se tomó la decisión, la versión 19 todavía era *release candidate*. Se fija el tag exacto para que el entorno sea reproducible; las actualizaciones de seguridad se aplican a mano.
- **Variante Debian (`trixie`) y no Alpine:** coincide con la base Debian de `python:3.13-slim` y usa `glibc`. El ahorro de tamaño de Alpine no es relevante para este prototipo.
- **Volumen con nombre montado en `/var/lib/postgresql`:** es la ruta que declara la imagen 18. Cubre el directorio de datos (`PGDATA`), evita volúmenes anónimos y deja todo en un mismo sistema de archivos, lo que facilita una futura actualización con `pg_upgrade --link`.
- **Puerto 5432 sin publicar:** la base solo es accesible desde la red interna de Docker, no desde el equipo anfitrión.
- **Credenciales en `.env` (`env_file`):** los secretos quedan fuera de Git.
- **Una sola base de datos compartida:** en una arquitectura de microservicios estricta, cada servicio tendría sus propios datos. Aquí se comparte una sola base porque con dos servicios separarla añade complejidad (sin `JOIN`, consistencia distribuida) sin aportar a la demo. Además, una base común es lo que permite que el bloqueo funcione entre varias réplicas de `reservas`. Mejora posible: un usuario y un esquema por servicio.
- **Arquitectura de CPU:** el desarrollo se hace en arm64 (Mac con Apple Silicon); para Azure Container Apps las imágenes se construirán para `linux/amd64`.

## Limitaciones conocidas

- La API usará el usuario creado por `POSTGRES_USER`, que es superusuario; lo correcto sería un usuario con privilegios mínimos.
- Las credenciales locales son de prueba y no deben reutilizarse en ningún despliegue.
- Un volumen no es una copia de seguridad: `docker compose down -v` lo borra. Para respaldos se usaría `pg_dump`.

## Relación con Sistemas Operativos

| Concepto del curso | Dónde aparece en el proyecto |
|---|---|
| Proceso y PID | Cada contenedor ejecuta un proceso; dentro del contenedor, uvicorn tiene PID 1 |
| Creación y reemplazo de procesos | El script de arranque de PostgreSQL hace `exec` y el servidor definitivo pasa a ser el PID 1 |
| Aislamiento | Los contenedores usan *namespaces* y *cgroups* del kernel Linux |
| Sistemas de archivos y montajes | El volumen se monta dentro del contenedor (mount namespace); los datos sobreviven al contenedor |
| Comunicación entre procesos | Socket Unix dentro del contenedor de la base vs. puerto TCP 5432 en la red de Docker |
| Máquinas virtuales | En macOS, Docker Desktop ejecuta los contenedores dentro de una VM Linux ligera |
| Concurrencia y condición de carrera | Compras simultáneas del mismo asiento (fase 2D) |
| Exclusión mutua | Bloqueo en PostgreSQL para corregir la doble venta (fase 2D) |
| Planificación Round Robin | Reparto de peticiones de Nginx entre réplicas (fase 3) |

## Autor

**Gianfranco Baca** — responsable del bloque de tecnología (microservicios con Docker) del Grupo 21.
GitHub: [@gianfrancobaca](https://github.com/gianfrancobaca)