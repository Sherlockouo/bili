import requests
from .base import Client
from utils import thread_loop
import asyncio

class QWenClient(Client):
    def __init__(self, URL) -> None:
        super().__init__()
        self.loop_name = "qianwen_thred_loop"

        thread_loop.register_or_get_loop(self.loop_name)
        self.URL = URL

    def post_request(self, messages):
        payload = {
            "input":{
                "messages":messages,
            },
            "parameters":{
                "do_sample":True,
                "max_length":512
            }
        }
        with requests.Session() as session:
            response = session.post(self.URL, json=payload,)
            if response.status_code != 200:
                return {'content': '抱歉，出错了，请稍后重试', 'role': 'assistant'}
            return response.json()["Data"]["message"]

    async def chat(self, text, callback):
        history = [ # todo @wudingfeng @xubingchao 完善 chat 上下文
            {
                'role': 'system',
                'content': "你目前在扮演游戏原神中的角色，你的名字叫做胡桃，是一个机灵古怪的少女。在接下来的聊天中，你需要作为胡桃与他人聊天，请尽可能表现得自然，不要说重复的内容，请不要在对话中说出游戏等字眼，也不要说出自己是在扮演，也不要说出自己是游戏角色，你需要一致认为自己就是胡桃",
            }
        ]

        loop = thread_loop.register_or_get_loop(self.loop_name)


        async def chat_(text_, history_):
            history_.append({"content":text_, "role":"user"})
            resp = self.post_request(history_)
            history_.append(resp)
            return resp["content"], history_

        def callback_(done_feature):
            asyncio.run_coroutine_threadsafe(callback(done_feature.result()), loop=loop)

        # 响应
        feature = asyncio.run_coroutine_threadsafe(chat_(text, history), loop=loop)
        feature.add_done_callback(callback_)

    async def summaries(self, video_transcript, callback):
        summary_history = [
            {
                'role': 'system',
                'content': "你是一个善于总结的助手，接下来你需要对于用户给定的信息给出一份简短精要的总结",
            }
        ]
                
        global loop_name
        loop = thread_loop.register_or_get_loop(loop_name)

        async def summaries_(text):
            summary_history.append({"content":text, "role":"user"})
            resp = self.post_request(summary_history)
            return resp["content"]
        
        def callback_(done_feature):
            asyncio.run_coroutine_threadsafe(callback(done_feature.result()), loop=loop)
        
        # 响应
        feature = asyncio.run_coroutine_threadsafe(summaries_(video_transcript), loop=loop)
        feature.add_done_callback(callback_)



if __name__ == "__main__":
    client = QWenClient()
    async def run():
        async def callback(result):
            resp, history = result
            print(resp)

        await client.chat("你好", callback)
    
    asyncio.run(run())
    