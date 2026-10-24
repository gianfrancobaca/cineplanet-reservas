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
| 2 | PostgreSQL + tabla de asientos + demo de doble venta y su corrección | 🔄 En curso |
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
            │    db     │   PostgreSQL (fase 2)
            └───────────┘
```

| Servicio | Tipo | Responsabilidad |
|---|---|---|
| `reservas` | Microservicio | Estado de los asientos y venta de entradas |
| `catalogo` | Microservicio | Películas, cines y funciones |
| `db` | Infraestructura | Almacenamiento (PostgreSQL) |
| `nginx` | Infraestructura | Balanceo de carga entre réplicas |

**Limitación conocida:** `reservas` y `catalogo` compartirán una sola base de datos para simplificar el prototipo. En una arquitectura de microservicios estricta, cada servicio tendría sus propios datos.

## Tecnologías

- **Python 3.13**, **FastAPI** y **uvicorn** (servidor ASGI)
- **Docker** y **Docker Compose**
- **PostgreSQL** (fase 2)
- **Nginx**, **Locust** y **pandas** (fase 3)
- **Azure Container Apps** (fase 4)

## Cómo ejecutarlo

Requisito: tener [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y abierto.

```bash
git clone https://github.com/gianfrancobaca/cineplanet-reservas.git
cd cineplanet-reservas
docker compose up --build
```

En otra terminal:

```bash
curl localhost:8000/salud
# {"estado":"ok"}
```

La documentación interactiva de la API queda disponible en `http://localhost:8000/docs`.

Para detener y eliminar los contenedores:

```bash
docker compose down
```

## Estructura del repositorio

```
cineplanet-reservas/
├── docker-compose.yml       # define y conecta los servicios
├── .gitignore
├── README.md
└── servicios/
    └── reservas/
        ├── Dockerfile       # receta de la imagen del servicio
        ├── requirements.txt # dependencias con versiones fijas
        └── app/
            └── main.py      # aplicación FastAPI
```

## Relación con Sistemas Operativos

| Concepto del curso | Dónde aparece en el proyecto |
|---|---|
| Proceso y PID | Cada contenedor ejecuta un proceso; dentro del contenedor, uvicorn tiene PID 1 |
| Aislamiento | Los contenedores usan *namespaces* y *cgroups* del kernel Linux |
| Máquinas virtuales | En macOS, Docker Desktop ejecuta los contenedores dentro de una VM Linux ligera |
| Concurrencia y condición de carrera | Compras simultáneas del mismo asiento (fase 2) |
| Exclusión mutua | Bloqueo en PostgreSQL para corregir la doble venta (fase 2) |
| Planificación Round Robin | Reparto de peticiones de Nginx entre réplicas (fase 3) |

## Autor

**Gianfranco Baca** — responsable del bloque de tecnología (microservicios con Docker) del Grupo 21.
GitHub: [@gianfrancobaca](https://github.com/gianfrancobaca)
