import streamlit as st
import json
import uuid
from datetime import datetime
import chromadb
from langchain_core.messages import HumanMessage, AIMessage
from multiagente.app.graph_builder import graph_builder

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
st.header("🛒 Carrito")
for i, item in enumerate(st.session_state["carrito"]):
    col1, col2, col3 = st.columns([4,1,1])
    col1.write(f"{item['nombre']} - ${item['precio']}")
    cantidad = col2.number_input("Cantidad", min_value=1, value=item['cantidad'], key=f"cant_{i}")
    col2.write(cantidad)
    if col3.button("Eliminar", key=f"del_{i}"):
        st.session_state["carrito"].pop(i)
        st.rerun()

# Agregar producto al carrito
with st.expander("Agregar producto al carrito"):
    with open("./data/inventario.json","r") as f:
        inventario = json.load(f)
    opciones = {p["nombre"]:p for p in inventario}
    seleccion = st.selectbox("Producto", list(opciones.keys()))
    cantidad = st.number_input("Cantidad", min_value=1, value=1)
    if st.button("Agregar al carrito"):
        producto = opciones[seleccion]
        st.session_state["carrito"].append({
            "id": producto["id"],
            "nombre": producto["nombre"],
            "precio": producto["precio"],
            "cantidad": cantidad
        })
        st.success(f"{producto['nombre']} agregado al carrito")
        st.rerun()
        
