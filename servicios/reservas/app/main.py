import os
import psycopg
from fastapi import FastAPI

app = FastAPI()

@app.get("/salud")
async def salud():
    return {"estado": "ok"}

@app.get("/salud/db")
def salud_db():
    with psycopg.connect(
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        dbname=os.environ["DB_NAME"]
    ) as conn:
        fila = conn.execute("SELECT count(*) FROM asientos").fetchone()
    return {"estado": "ok", "asientos": fila[0]}