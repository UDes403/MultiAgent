import pytest
from typing import cast
from langchain_core.messages import HumanMessage
from langgraph.graph import MessagesState

from multiagente.app.graph_builder import graph_builder


def test_graph_returns_response_message():
    """
    Test de grafo

    -anotaciones importantes!!!
    - Usa MessagesState como TypedDict
    - Se hace cast explícito para satisfacer al type checker
    - En runtime el objeto sigue siendo un dict
    """

    initial_state = cast(
        MessagesState,
        {
            "messages": [
                HumanMessage(content="Hola, quiero información sobre productos")
            ]
        }
    )

    result = graph_builder.invoke(initial_state)

    assert "messages" in result
    assert isinstance(result["messages"], list)
    assert len(result["messages"]) > 0

    last_message = result["messages"][-1]
    assert hasattr(last_message, "content")
    assert isinstance(last_message.content, str)
    assert last_message.content.strip() != ""
