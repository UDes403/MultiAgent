from langchain_community.chat_models import ChatOllama

# LLM genérico
llm_general = ChatOllama(
    model="llama3",
    temperature=0.7
)
