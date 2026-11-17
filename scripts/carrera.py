"""Lanza N compras simultáneas del mismo asiento y cuenta las respuestas."""
import json
import sys
import threading
import urllib.error
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

URL_BASE = "http://localhost:8000/reservas/"
N = 50
ASIENTO_ID = 1

ruta = sys.argv[1] if len(sys.argv) > 1 else "insegura"
barrera = threading.Barrier(N)


def comprar(i):
    cuerpo = json.dumps({"asiento_id": ASIENTO_ID, "cliente": f"cliente-{i}"}).encode()
    peticion = urllib.request.Request(
        URL_BASE + ruta,
        data=cuerpo,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    barrera.wait()  # todos los hilos esperan aquí y salen a la vez
    try:
        with urllib.request.urlopen(peticion, timeout=30) as respuesta:
            return respuesta.status
    except urllib.error.HTTPError as error:
        return error.code


with ThreadPoolExecutor(max_workers=N) as pool:
    codigos = list(pool.map(comprar, range(N)))

print(f"Ruta: /reservas/{ruta}  |  {N} compras del asiento {ASIENTO_ID}")
for codigo, cantidad in sorted(Counter(codigos).items()):
    print(f"  HTTP {codigo}: {cantidad}")
    