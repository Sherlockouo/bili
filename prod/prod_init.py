from .get_reply import GetReply
import asyncio
from .event import Chat

async def start_task(credential):
    get_reply = GetReply(credential)
    await get_reply.start()
    
async def start_chat():
    chat = Chat()
    await chat.start()