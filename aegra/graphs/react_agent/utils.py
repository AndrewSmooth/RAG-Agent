"""Utility & helper functions."""

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from fastmcp import Client


def get_message_text(msg: BaseMessage) -> str:
    """Get the text content of a message."""
    content = msg.content
    if isinstance(content, str):
        return content
    elif isinstance(content, dict):
        return content.get("text", "")
    else:
        txts = [c if isinstance(c, str) else (c.get("text") or "") for c in content]
        return "".join(txts).strip()


def load_chat_model(fully_specified_name: str) -> BaseChatModel:
    """Load a chat model from a fully specified name.

    Args:
        fully_specified_name (str): String in the format 'provider/model'.
    """
    provider, model = fully_specified_name.split("/", maxsplit=1)
    return init_chat_model(model, model_provider=provider)

async def get_mcp_client() -> Client:
    global mcp_client
    if mcp_client is None:
        mcp_client = Client(os.getenv("RAG_URL"))
        await mcp_client.__aenter__()
    return mcp_client

async def shutdown_mcp_client():
    global mcp_client
    if mcp_client is not None:
        await mcp_client.__aexit__(None, None, None)
        mcp_client = None
