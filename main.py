import prod
from utils import thread_loop
import asyncio, time
from credential import credential

loop_name = "main_thread_loop"

thread_loop.registe_or_get_loop(loop_name)

# 调用实例方法
async def launch():
   await prod.start_task(credential)


def main():
   asyncio.run_coroutine_threadsafe(launch(), thread_loop.registe_or_get_loop(loop_name),)
   
   try:
      while True:
         time.sleep(1)
   except KeyboardInterrupt:
      thread_loop.stop_all_loop()
      print("exit...")
      exit()
   

if __name__ == "__main__":
   main()