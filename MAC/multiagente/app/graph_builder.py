from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode
from multiagente.tools.tools_carrito import add_to_cart, view_cart, checkout
from langgraph.types import Command
from langchain_core.messages import SystemMessage 
from multiagente.app.llm import llm_general
from multiagente.app.schemas import Router
from multiagente.app.nodes import (
    general_conversation_agent,
    product_recommendation_agent,
    product_details_agent,
    product_reviews_agent,
    create_order_agent,
    feedback_agent
)

PROMPT_SYSTEM = "Eres un supervisor que decide qué agente debe actuar según la conversación del usuario."

def supervisor_node(
    state: MessagesState
) -> Command[
    str
]:
    messages_list = state.get("messages", [])
    messages = [SystemMessage(content=PROMPT_SYSTEM)] + messages_list
    r = llm_general.with_structured_output(Router).invoke(messages)
    goto = r"next"
    if goto == "FINISH":
        goto = END
    return Command(goto=goto)

# Construcción del grafo
builder = StateGraph(MessagesState)
builder.add_node("supervisor", supervisor_node)
builder.add_node("general_conversation_agent", general_conversation_agent)
builder.add_node("product_recommendation_agent", product_recommendation_agent)
builder.add_node("product_details_agent", product_details_agent)
builder.add_node("product_reviews_agent", product_reviews_agent)
builder.add_node("create_order_agent", create_order_agent)
builder.add_node("feedback_agent", feedback_agent)
builder.add_edge("create_order_agent", "feedback_agent")
builder.add_edge(START, "supervisor")

graph_builder = builder.compile()
