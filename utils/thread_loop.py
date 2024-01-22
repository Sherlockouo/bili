import asyncio
import threading

loops = {}

stop = False

def start_loop(thread_loop: asyncio.AbstractEventLoop):
    asyncio.set_event_loop(thread_loop)
    thread_loop.run_forever()

def register_or_get_loop(loop_name) -> asyncio.AbstractEventLoop:
    if stop:
        return None
    
    if loop_name in loops:
        return loops[loop_name]
    
    thread_loop = asyncio.new_event_loop()
    loops[loop_name] = thread_loop

    t = threading.Thread(target=start_loop, args=(thread_loop,))
    t.setDaemon(True) # 设置为守护线程，不然主线程出异常退出，子线程一样会继续运行。
    t.start()

def stop_all_loop():
    for loop in loops.values():
        loop.stop()