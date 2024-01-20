from utils.once import Once
from utils.logger import logger
from modelscope import AutoTokenizer, AutoModel, snapshot_download
from utils import thread_loop
import asyncio

loop_name = "chatgml_thred_loop"

thread_loop.registe_or_get_loop(loop_name)

model_dir = snapshot_download("ZhipuAI/chatglm3-6b")

tokenizer = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True)
model = AutoModel.from_pretrained(model_dir, trust_remote_code=True).half().cuda()

model = model.eval()


async def chat(text, callback):
    history = [ # todo @wudingfeng @xubingchao 完善 chat 上下文
        {
            'role': 'system',
            'content': "你目前在扮演游戏原神中的角色，你的名字叫做胡桃，是一个机灵古怪的少女。在接下来的聊天中，你需要作为胡桃与他人聊天，请尽可能表现得自然，不要说重复的内容，请不要在对话中说出游戏等字眼，也不要说出自己是在扮演，也不要说出自己是游戏角色，你需要一致认为自己就是胡桃",
        }
    ]

    global loop_name
    loop = thread_loop.registe_or_get_loop(loop_name)


    async def chat_(text_, history_):
        response, history_res = model.chat(tokenizer, text_, history=history_)
        return response, history_res
    
    def callback_(done_feature):
        asyncio.run_coroutine_threadsafe(callback(done_feature.result()), loop=loop)
    
    # 响应
    feature = asyncio.run_coroutine_threadsafe(chat_(text, history), loop=loop)
    feature.add_done_callback(callback_)

async def summaries(video_transcript, video_info, callback):
    summary_history = [
        {
            'role': 'system',
            'content': "你是一个善于总结的助手，接下来你需要对于给定信息给出一份简短精要的总结",
        }
    ]
            
    global loop_name
    loop = thread_loop.registe_or_get_loop(loop_name)

    async def summaries_(text):
        response, _ = model.chat(tokenizer, text, history=summary_history)
        return response
    
    def callback_(done_feature):
        asyncio.run_coroutine_threadsafe(callback(done_feature.result()), loop=loop)
    
    # 响应
    feature = asyncio.run_coroutine_threadsafe(summaries_(video_transcript), loop=loop)
    feature.add_done_callback(callback_)
    