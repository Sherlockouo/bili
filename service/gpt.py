import os

client = None

print(os.environ.get("GPT_CLIENT"))

if os.environ.get("GPT_CLIENT") == "qianwen":
    from .gpt_client import qwen
    client = qwen.QWenClient(os.environ.get("QWEN_URL"))

elif  os.environ.get("GPT_CLIENT") == "chatgml":
    from .gpt_client import chatgml
    client = chatgml.QWenClient()

async def chat(text, callback):
    await client.chat(text, callback)

async def summaries(video_transcript, callback):
    await client.summaries(video_transcript, callback)