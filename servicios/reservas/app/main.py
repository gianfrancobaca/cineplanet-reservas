import os
import psycopg
import time
from pydantic import BaseModel
from fastapi import FastAPI 
from fastapi import HTTPException

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

class Compra(BaseModel):
    asiento_id: int
    cliente: str

@app.post("/reservas/insegura")
def crear(c: Compra):
    with psycopg.connect(
            host=os.environ["DB_HOST"],
            port=os.environ["DB_PORT"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            dbname=os.environ["DB_NAME"]
        ) as conn:
            fila = conn.execute("SELECT estado FROM asientos WHERE id = %s", (c.asiento_id,)
                                ).fetchone()
            if fila is None:
                raise HTTPException(status_code=404, detail="Asiento no encontrado")
            if fila[0] != "libre":
                raise HTTPException(status_code=409, detail="Vendido")
            time.sleep(0.5)  # DEMO: amplía la ventana entre comprobar y vender
            conn.execute("UPDATE asientos SET estado = 'vendido' WHERE id = %s", (c.asiento_id,))
            conn.execute("INSERT INTO ventas (asiento_id, cliente) VALUES (%s, %s)", (c.asiento_id, c.cliente))

            
    return {"asiento_id": c.asiento_id, "cliente": c.cliente}
