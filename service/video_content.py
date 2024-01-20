import asyncio, re
import async_requests
from bilibili_api import video

from langchain.document_loaders.bilibili import BiliBiliLoader

async def load_video(credential, url) -> None:
    bvid = re.search(r"BV\w+", url)
    # 实例化 Video 类
    v = video.Video(bvid=bvid.group(), credential=credential)
    # 获取信息
    video_info = await v.get_info()
    sub = await v.get_subtitle(video_info["cid"])
    # 打印信息
    sub_list = sub["subtitles"]
    if sub_list:
        sub_url = sub_list[0]["subtitle_url"]
        if not sub_url.startswith("http"):
            sub_url = "https:" + sub_url

        req = async_requests.Request(sub_url)
        result = await req.get()
        raw_sub_titles = result.json["body"]
        raw_transcript = ";".join([c["content"] for c in raw_sub_titles])

        raw_transcript_with_meta_info = (
            f"Video Title: {video_info['title']},"
            f"description: {video_info['desc']}\n\n"
            f"Transcript: {raw_transcript}"
        )
        return raw_transcript_with_meta_info, video_info

    raw_transcript_with_meta_info = (
            f"Video Title: {video_info['title']},"
            f"description: {video_info['desc']}\n\n"
            f"Transcript: None"
        )
    return raw_transcript_with_meta_info, video_info