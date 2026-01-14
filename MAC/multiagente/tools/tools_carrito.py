from langchain_core.tools import tool
from uuid import uuid4

@tool
def add_to_cart(carrito: list, producto: str, precio: float, cantidad: int):
    carrito.append({
        "id": str(uuid4()),
        "nombre": producto,
        "precio": precio,
        "cantidad": cantidad
    })
    return carrito


@tool
def view_cart(carrito: list):
    if not carrito:
        return "El carrito está vacío"
    return "\n".join(
        f"{p['nombre']} x{p['cantidad']} = ${p['precio'] * p['cantidad']}"
        for p in carrito
    )


@tool
def checkout(carrito: list):
    total = sum(p["precio"] * p["cantidad"] for p in carrito)
    return {
        "total": total,
        "estado": "confirmado"
    }
