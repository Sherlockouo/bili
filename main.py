from bilibili_api import Credential, sync
import prod
import asyncio
from credential import credential

# 调用实例方法
async def launch():
   await asyncio.gather(
      # prod.start_chat(),
   prod.start_task(credential),)

asyncio.run(launch())