import json
from pathlib import Path

# Ruta del archivo de inventario
INVENTARIO_PATH = Path("./data/inventario.json")


def cargar_inventario() -> list[dict]:
    """
    Carga el inventario desde un archivo JSON.

    Retorna una lista de productos con estructura:
    {
        "id": str,
        "nombre": str,
        "precio": float,
        "cantidad": int
    }
    """
    if not INVENTARIO_PATH.exists():
        return []

    with open(INVENTARIO_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def guardar_inventario(inventario: list[dict]) -> None:
    """
    Guarda el inventario actualizado en disco.
    """
    INVENTARIO_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(INVENTARIO_PATH, "w", encoding="utf-8") as f:
        json.dump(inventario, f, ensure_ascii=False, indent=2)


def stock_disponible(producto_id: str, inventario: list[dict]) -> int:
    """
    Retorna el stock disponible de un producto.
    Si no existe, retorna 0.
    """
    producto = next(
        (p for p in inventario if p.get("id") == producto_id),
        None
    )
    return producto["cantidad"] if producto else 0
