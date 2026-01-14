from typing import List, Literal
from pydantic import BaseModel
from typing_extensions import TypedDict

# Para extraer intereses del usuario
class InterestSchema(BaseModel):
    interest: List[str]

# Para la salida del supervisor
class Router(TypedDict):
    next: Literal[
        "general_conversation_agent",
        "product_recommendation_agent",
        "product_details_agent",
        "product_reviews_agent",
        "create_order_agent",
        "feedback_agent",
        "FINISH"
    ]

# Para las calificaciones de experiencia de compra
class FeedbackSchema(BaseModel):
    puntuacion: int
    recomendacion: int
    comentario: str