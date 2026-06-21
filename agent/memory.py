from langchain.memory import ConversationBufferWindowMemory

def get_memory(k: int = 5) -> ConversationBufferWindowMemory:
    """
    Returns a sliding window conversation memory.
    k=5 means it remembers the last 5 exchanges.
    """
    return ConversationBufferWindowMemory(
        k=k,
        memory_key="chat_history",
        return_messages=True,
        output_key="output"
    )
