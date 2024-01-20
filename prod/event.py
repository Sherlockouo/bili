from bilibili_api import Credential, sync
from bilibili_api.session import Session, Event
from bilibili_api.utils.picture import Picture
from credential import credential
from service.gpt import chat


session = Session(credential)

class Chat:   
    def __init__(self) -> None:
        super().__init__()
        
    @session.on(Event.PICTURE)
    async def pic(event: Event):
        img: Picture = event.content
        img.download("./")

    @session.on(Event.TEXT)
    async def reply(event: Event):
        if event.content == "/register":
            pass
            # session.close()
        elif event.content.startswith("/pictue"):
            img = await Picture.from_file("test.jpg").upload_file(session.credential)
            await session.reply(event, img)
        elif event.content.startswith("/chat"):
            chat_response = chat(event.content)
            chat_str = ''.join(chat_response)
            chunks = [chat_str[i:i+100] for i in range(0, len(chat_str), 100)]
            for chunk in chunks:
                print("chunk length ",len(chunk))
                await session.reply(event, chunk)
        else:
            await session.reply(event, "你好呀,请问需要什么帮助")

    async def start(self) -> None:
       await session.start()