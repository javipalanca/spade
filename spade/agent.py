import asyncio
from threading import Thread, Event


class Agent(object):
    def __init__(self):
        self.aiothread = AioThread()
        self.aiothread.start()
        self.aiothread.event.wait()

        self.behaviours = []
        self._values = {}

    def add_behaviour(self, behav):
        behav.set_aiothread(self.aiothread)
        behav.set_agent(self)
        self.behaviours.append(behav)
        behav.start()

    def stop(self):
        for behav in self.behaviours:
            behav.kill()
        self.aiothread.finalize()

    def set(self, name, value):
        self._values[name] = value

    def get(self, name):
        return self._values[name]


class AioThread(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop, self.event = None, Event()

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.call_soon(self.event.set)
        self.loop.run_forever()

    def add_task(self, coro):
        fut = asyncio.run_coroutine_threadsafe(coro, loop=self.loop)
        return fut

    def finalize(self):
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.join()
