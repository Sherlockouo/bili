import os
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
from config import OPENAI_API_KEY
from utils.once import Once
from utils.logger import logger

messages = []
historyMsgs = []
client = OpenAI(api_key="")

def init():
    global client
    

    client = OpenAI(
        # This is the default and can be omitted
        api_key= OPENAI_API_KEY
    )

once = Once()
once.do(init)

def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0):
    response = client.with_options(max_retries=3).chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature, # this is the degree of randomness of the model"s output
        stream=True
    )
    return response

def buildMsgs(theme):
    historyMsgs.append({"role":"user","content":theme})
    global messages
    messages =  [  
        {"role":"system", "content":"you are a daily assistant"},    
        {"role":"user","content":theme}
    ]
    # logger.info("builded ",messages)
    
def extractMsg(response):
    chatCompletions = []
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            chatCompletions.append(chunk.choices[0].delta.content)
    return chatCompletions

async def  persistence():
    logger.info("saving... ",messages)

def chat(theme):
    # 配置message
    buildMsgs(theme)
    # 请求 openai 
    responseMsgs = get_completion_from_messages(messages=messages,temperature=1)
    # 保存 持久化 保存message
    
    chatCompletions = extractMsg(responseMsgs)
    # 响应
    return chatCompletions