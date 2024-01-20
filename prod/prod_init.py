from .get_reply import GetReply
import asyncio
from .event import Chat

async def start_task(credential):
    get_reply = GetReply(credential)
    chat = Chat()

    await asyncio.gather(get_reply.start(), chat.start(), return_exceptions=True)