import datetime
import time
from bilibili_api import session
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from dal import user_dal

from service import gpt, video_content

class GetReply:
    def __init__(self, credential) -> None:
        super().__init__()
        # 会话状态
        self.__status = 0

        # 会话UID为键 会话中最大Seqno为值
        self.maxSeqno = [456401906614284]

        # 凭证
        self.credential = credential

        # 异步定时任务框架
        self.sched = AsyncIOScheduler(timezone="Asia/Shanghai")

    def get_status(self) -> int:
        """
        获取连接状态

        Returns:
            int: 0 初始化，1 已连接，2 断开连接中，3 已断开，4 错误
        """
        return self.__status

    async def run(self):
        @self.sched.scheduled_job(
            "interval",
            id="query",
            seconds=10,
            max_instances=3,
            next_run_time=datetime.datetime.now(),
        )
        async def _():
            last_uid = None
            last_time = int(time.time())
            while True:
                res = await session.get_at(self.credential,at_time=last_time, last_uid=last_uid) # type: ignore
                # print(res)

                for (idx, item) in enumerate(res["items"]):
                    if item["id"] in self.maxSeqno:
                        break

                    if idx == 0:
                        self.maxSeqno.insert(0, res["items"][0]["id"])

                    # 85902173 Sherlockouo
                    user_id = item["user"]["mid"]
                    if not user_dal.query_by_user_id(user_id):
                        print(item["user"]["nickname"], ":", "has no auth")
                        continue

                    video_url = item["item"]["uri"]

                    def callback_warpper():
                        user, content = item["user"]["nickname"], item["item"]["source_content"]
                        async def callback(response):
                            print(user, content, "总结内容:")
                            print(response)
                        return callback

                    raw_transcript, _ = await video_content.load_video(self.credential, video_url)
                    await gpt.summaries(raw_transcript, callback_warpper())

                if res['cursor']['is_end']:
                    break
                else:
                    last_uid = res['cursor']['id']
                    last_time = res['cursor']['time']

            if len(self.maxSeqno) >= 2:
                self.maxSeqno = self.maxSeqno[-2:-1]

        self.sched.start()

    async def start(self) -> None:
        """
        阻塞异步启动 通过调用 self.close() 后可断开连接

        Args:
            except_self: bool 是否排除自己发出的消息，默认是
        """

        await self.run()
        while self.get_status() < 2:
            await asyncio.sleep(1)

        if self.get_status() == 2:
            self.__status = 3

