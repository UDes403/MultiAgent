import streamlit as st
import json
import uuid
from datetime import datetime
import chromadb
from langchain_core.messages import HumanMessage, AIMessage
from multiagente.app.graph_builder import graph_builder
from multiagente.app.inventario import (
    cargar_inventario,
    guardar_inventario,
    stock_disponible
)

# Inicializar cliente de ChromaDB
cliente = chromadb.PersistentClient(path="./chromadb")

st.title("🤖 Multi Agente Comercial (MAC)")

# Inicializar carrito
if "carrito" not in st.session_state:
    st.session_state["carrito"] = []

# Inicializar chat
if "mensajes" not in st.session_state:
    st.session_state["mensajes"] = []

# Mostrar mensajes anteriores
for mensaje in st.session_state.mensajes:
    st.chat_message(mensaje["role"]).write(mensaje["content"])

# Input de usuario
prompt = st.chat_input("Escribe tu mensaje aquí...")
if prompt:
    st.session_state.mensajes.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    lc_messages = [
    HumanMessage(content=m["content"]) if m["role"]=="user" else AIMessage(content=m["content"])
    for m in st.session_state.mensajes
]

# Pasar la lista directamente, no en un dict
response = graph_builder.invoke({
    "messages": lc_messages}) # type: ignore

# Obtener la última respuesta del agente
if response.get("messages"):
    r = response["messages"][-1].content
else:
    r = "Error: no hay respuesta del agente"

# Guardar la respuesta en session_state
st.session_state.mensajes.append({"role":"assistant","content":r})
st.chat_message("assistant").write(r)


# Carrito de compras UI
st.header("Carrito")

inventario = cargar_inventario()

for i, item in enumerate(st.session_state.carrito):
    col1, col2, col3 = st.columns([4, 2, 1])

    col1.write(f"**{item['nombre']}**  \n${item['precio']} c/u")

    nueva_cantidad = col2.number_input(
        "Cantidad",
        min_value=1,
        value=item["cantidad"],
        key=f"cant_{item['id']}"
    )

    # Actualizar cantidad
    if nueva_cantidad != item["cantidad"]:
        stock = stock_disponible(item["id"], inventario)
        if nueva_cantidad <= stock + item["cantidad"]:
            item["cantidad"] = nueva_cantidad
        else:
            st.warning("Stock insuficiente")

    if col3.button("Eliminar", key=f"del_{item['id']}"):
        st.session_state.carrito.pop(i)
        st.rerun()


# Agregar productos
with st.expander("Agregar producto"):
    opciones = {p["nombre"]: p for p in inventario}
    seleccion = st.selectbox("Producto", opciones.keys())
    cantidad = st.number_input("Cantidad", min_value=1, value=1)

    if st.button("Agregar al carrito"):
        producto = opciones[seleccion]

        stock = producto["cantidad"]
        en_carrito = next(
            (x for x in st.session_state.carrito if x["id"] == producto["id"]),
            None
        )

        cantidad_actual = en_carrito["cantidad"] if en_carrito else 0

        if cantidad + cantidad_actual > stock:
            st.error("Stock insuficiente")
        else:
            if en_carrito:
                # Reemplaza cantidad
                en_carrito["cantidad"] = cantidad
            else:
                st.session_state.carrito.append({
                    "id": producto["id"],
                    "nombre": producto["nombre"],
                    "precio": producto["precio"],
                    "cantidad": cantidad
                })
            st.success("Producto agregado o actualizado")
            st.rerun()

# actualiza inventario

if st.session_state.carrito:
    if st.button("Confirmar compra"):
        for item in st.session_state.carrito:
            p = next(p for p in inventario if p["id"] == item["id"])
            p["cantidad"] -= item["cantidad"]

        guardar_inventario(inventario)
        st.session_state.carrito = []
        st.success("Compra realizada y stock actualizado")
        st.rerun()







