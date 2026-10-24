from fastapi import FastAPI

app = FastAPI()

@app.get("/salud")
async def salud():
    return {"estado": "ok"}