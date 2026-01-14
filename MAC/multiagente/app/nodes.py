import uuid
import json
from datetime import datetime
from typing import List

from langgraph.types import Command
from langgraph.graph import END

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

from multiagente.app.llm import llm_general
from multiagente.app.schemas import InterestSchema, FeedbackSchema
from multiagente.tools.tools_carrito import add_to_cart, view_cart, checkout



# Constructor

def build_messages(state, system_prompt) -> List[BaseMessage]:
    messages: List[BaseMessage] = [HumanMessage(content=system_prompt)]

    for m in state.get("messages", []):
        if isinstance(m, BaseMessage):
            messages.append(m)

    return messages



# Agente de conversación general
def general_conversation_agent(state) -> Command:
    r = llm_general.invoke(
        build_messages(state, "Responde de forma cordial y general al usuario.")
    ).content

    return Command(
        goto="product_recommendation_agent",
        update={
            "messages": state["messages"] + [AIMessage(content=r)]
        }
    )


# Agente de recomendaciones

def product_recommendation_agent(state) -> Command:
    schema = llm_general.with_structured_output(InterestSchema)

    intereses = InterestSchema._get_value(
        build_messages(state, "Detecta los intereses del usuario.")
    ).interest

    r = f"intereses: {', '.join(intereses)}"

    return Command(
        goto="product_details_agent",
        update={
            "messages": state["messages"] + [AIMessage(content=r)]
        }
    )



# Agente detalles de producto
def product_details_agent(state) -> Command:
    r = llm_general.invoke(
        build_messages(state, "Responde a las preguntas de detalles de productos.")
    ).content

    return Command(
        goto="product_recommendation_agent",
        update={
            "messages": state["messages"] + [AIMessage(content=r)]
        }
    )


# Agente reseñas de producto
def product_reviews_agent(state) -> Command:
    r = llm_general.invoke(
        build_messages(state, "Proporciona reseñas de productos relevantes.")
    ).content

    return Command(
        goto="create_order_agent",
        update={
            "messages": state["messages"] + [AIMessage(content=r)]
        }
    )


# Agente comercial (tool-calling)

tools = [add_to_cart, view_cart, checkout]

agent = llm_general.bind_tools(tools)


def commerce_agent(state) -> Command:
    """
    El LLM devuelve un AIMessage.
    Si hay tool_calls, LangGraph debe enrutar a ToolNode.
    """
    response = agent.invoke(state["messages"])

    return Command(
        goto="supervisor",
        update={
            "messages": state["messages"] + [response],
            "carrito": state.get("carrito", [])
        }
    )


# Agente crear orden de compra

def create_order_agent(state) -> Command:
    id_venta = str(uuid.uuid4())

    pedido = {
        "id_venta": id_venta,
        "fecha": datetime.now().isoformat(),
        "estado": "confirmado"
    }

    with open("pedidos.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(pedido, ensure_ascii=False) + "\n")

    r = "Compra confirmada. Gracias por tu pedido."

    return Command(
        goto="feedback_agent",
        update={
            "messages": state["messages"] + [AIMessage(content=r)],
            "id_venta": id_venta
        }
    )


# Agente de feedback
def feedback_agent(state) -> Command:
    schema = llm_general.with_structured_output(FeedbackSchema)

    feedback = schema.invoke(
        build_messages(
            state,
            "Solicita al usuario la calificación de su experiencia de compra "
            "y extrae puntuación, recomendación y comentarios."
        )
    )

    data = {
        "id_venta": state.get("id_venta", "desconocido"),
        "puntuacion": FeedbackSchema.puntuacion,
        "recomendacion": FeedbackSchema.recomendacion,
        "comentario": FeedbackSchema.comentario,
        "fecha": datetime.now().isoformat()
    }

    with open("feedback.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

    r = "¡Gracias por su calificación!"

    return Command(
        goto=END,
        update={
            "messages": state["messages"] + [AIMessage(content=r)]
        }
    )
