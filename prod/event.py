from bilibili_api import Credential, sync,user
from bilibili_api.session import Session, Event
from bilibili_api.utils.picture import Picture
from credential import credential
# from service.gpt import chat
from utils.logger import logger
from dal import user_dal
from service.user import is_follow

import asyncio

session = Session(credential)
from credential import session

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
			if not await is_follow(event.sender_uid):
				await session.reply(event, "还没有关注我哟，请先关注我再和我聊天，关注后可回复/register进行登记")
				return
			
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
			if not await is_follow(event.sender_uid):
				await session.reply(event, "还没有关注我哟，请先关注我再和我聊天，关注后可回复/register进行登记")
				return
			
			img = await Picture.from_file("test.jpg").upload_file(session.credential)
			await session.reply(event, img)

		elif event.content.startswith("/chat"):
			if not await is_follow(event.sender_uid):
				await session.reply(event, "还没有关注我哟，请先关注我再和我聊天，关注后可回复/register进行登记")
				return

			async def callback(result):
				limit = 499
				response, _ = result
				print(response)

				sentense_list = ''.join(response).replace("。", ".").split(".")

				current = ""

				curr_idx = 0
				while True:
					if len(current) > limit:
						await session.reply(event, current[:limit])
						await asyncio.sleep(1)
						current = current[limit:]
						continue

					if curr_idx >= len(sentense_list):
						if current != "":
							await session.reply(event, current)
						break
					
					if len(current) + len(sentense_list[curr_idx]) > limit:
						await session.reply(event, current)
						current = ""
						await asyncio.sleep(1)
						continue

					if curr_idx > 0:
						current += "."
					
					current += sentense_list[curr_idx]
					curr_idx += 1
			
			# await chat(event.content, callback)
		else:
			await session.reply(event, "你好呀,请问需要什么帮助")

	async def start(self) -> None:
		await session.run()


	def __del__(self):
		session.close()