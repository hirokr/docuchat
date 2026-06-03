"""Topic-scoped chat with LangChain memory and streamed responses."""

from __future__ import annotations

from collections.abc import Iterator
from uuid import uuid4

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq

_memories: dict[str, InMemoryChatMessageHistory] = {}
_topics: dict[str, str] = {}

_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant. The conversation is about: {topic}"),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]
)

_LLM = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7, streaming=True)


def create_topic_memory(session_id: str, topic: str) -> InMemoryChatMessageHistory:
    """Create (or replace) in-memory conversation history for a topic."""
    memory = InMemoryChatMessageHistory()
    _memories[session_id] = memory
    _topics[session_id] = topic
    return memory


def get_topic_memory(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in _memories:
        raise KeyError(
            f"No memory for session {session_id!r}. Call create_topic_memory() first."
        )
    return _memories[session_id]


def stream_topic_chat(
    topic: str,
    message: str | None = None,
    *,
    session_id: str | None = None,
) -> tuple[str, Iterator[str]]:
    """
    Bind a topic to session memory and stream the model reply token-by-token.

    Returns:
        (session_id, iterator of text chunks)
    """
    sid = session_id or uuid4().hex
    if sid not in _memories:
        create_topic_memory(sid, topic)
    elif _topics.get(sid) != topic:
        create_topic_memory(sid, topic)

    user_message = message or f"Give a clear, engaging overview of: {topic}"
    return sid, _stream_reply(sid, user_message)


def _stream_reply(session_id: str, user_message: str) -> Iterator[str]:
    memory = get_topic_memory(session_id)
    topic = _topics[session_id]

    chain = (
        RunnablePassthrough.assign(history=lambda _: memory.messages)
        | _PROMPT
        | _LLM
    )

    full_response: list[str] = []

    for chunk in chain.stream({"input": user_message, "topic": topic}):
        text = chunk.content if isinstance(chunk.content, str) else ""
        if not text:
            continue
        full_response.append(text)
        yield text

    memory.add_messages(
        [
            HumanMessage(content=user_message),
            AIMessage(content="".join(full_response)),
        ]
    )


if __name__ == "__main__":
    import sys

    from dotenv import load_dotenv

    load_dotenv()

    topic = sys.argv[1] if len(sys.argv) > 1 else "retrieval-augmented generation"
    sid, stream = stream_topic_chat(topic)

    print(f"Session: {sid}\nTopic: {topic}\n")
    for token in stream:
        print(token, end="", flush=True)
    print()
