import chromadb
from datetime import datetime
from typing import Dict, Any

# Cliente persistente
_client = chromadb.PersistentClient(path="./chromadb")

# Colecciones
_orders = _client.get_or_create_collection("orders")
_feedback = _client.get_or_create_collection("feedback")


def save_order(order: Dict[str, Any]) -> None:
    """
    Guarda una orden de compra en ChromaDB.
    """
    _orders.add(
        ids=[order["id_venta"]],
        documents=[str(order)],
        metadatas=[{
            "fecha": order.get("fecha", datetime.now().isoformat()),
            "estado": order.get("estado", "desconocido")
        }]
    )


def save_feedback(feedback: Dict[str, Any]) -> None:
    """
    Guarda feedback de usuario en ChromaDB.
    """
    _feedback.add(
        ids=[f"{feedback['id_venta']}_{datetime.now().isoformat()}"],
        documents=[feedback.get("comentario", "")],
        metadatas=[{
            "puntuacion": feedback.get("puntuacion"),
            "recomendacion": feedback.get("recomendacion"),
            "fecha": feedback.get("fecha", datetime.now().isoformat())
        }]
    )
