from fastapi import APIRouter
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

from multiagente.app.graph_builder import graph_builder
from multiagente.app.graph_builder import feedback_agent

router = APIRouter()

class Mensaje(BaseModel):
    contenido: str

class Feedback(BaseModel):
    id_venta: str
    puntuacion: int
    recomendacion: int
    comentario: str = ""

@router.post("/chat")
def chat(msg: Mensaje):
    response = graph_builder.invoke({
        "messages": [HumanMessage(content=msg.contenido)]
    })

    return {"respuesta": response["messages"][-1].content}

@router.post("/feedback")
def feedback(data: Feedback):
    feedback_agent(**data.dict())
    return {"status": "ok"}
