from fastapi import FastAPI
from multiagente.app.router import router

app = FastAPI(
    title="Multi Agente Comercial - API",
    description="API para interactuar con el Multi Agente Comercial MAC",
    version="1.0"
)

# Incluir rutas
app.include_router(router, prefix="/api")

@app.get("/")
def root():
    return {"status": "ok", "message": "API Multi Agente Comercial ONLINE"}
