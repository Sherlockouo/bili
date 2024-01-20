from bilibili_api import Credential, sync,user
from bilibili_api.session import Session, Event
from bilibili_api.utils.picture import Picture
from credential import credential
from service.gpt import chat
from utils.logger import logger
from dal import user_dal

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
            async def register(user_id):
                sender = user.User(user_id)
                sender_info = await sender.get_user_info()
                if len(user_dal.query_by_user_id(user_id)) > 0 :
                    return 0
                user_dal.create_user(user_id, sender_info['name'])
                
                return 1

            try:
                
                if await register(event.sender_uid) == 0:
                    await session.reply(event,"has been registed")
                else:
                    await session.reply(event,"success")


            except Exception as e:
                await session.reply(event, "plz retry later")
                logger.error(f"regit error: {e}")
            
        elif event.content.startswith("/pictue"):
            img = await Picture.from_file("test.jpg").upload_file(session.credential)
            await session.reply(event, img)

        elif event.content.startswith("/chat"):
            chat_response = await chat(event.content)
            chat_str = ''.join(chat_response)
            chunks = [chat_str[i:i+100] for i in range(0, len(chat_str), 100)]
            for chunk in chunks:
                print("chunk length ",len(chunk))
                await session.reply(event, chunk)
        else:
            await session.reply(event, "你好呀,请问需要什么帮助")

    async def start(self) -> None:
       print(1111)
       await session.run()
       print(2222)


    def __del__(self):
        session.close()