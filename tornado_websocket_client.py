# -*- coding: utf-8 -*-
"""用于异步连结 websocket 服务器，与服务器通讯
NOTE 这里曾经想将客户端的类通过指定元类定义为单例类，但是 WebSocketClient
NOTE 是抽象基类的子类，抽象基类本身已经指定了元类，两个元类产生了冲突，
NOTE 所以无法使用这种方式实现单例类
"""

__version__ = 1 + 1e-1 + 1j
__author__ = "Bavon C. K. Chao (赵庆华)"

import asyncio
import logging
import random
import sys
import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from queue import deque
from typing import Union

import tornado
from tornado.gen import sleep
from tornado.httpclient import HTTPRequest
from tornado.httputil import HTTPHeaders
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.websocket import websocket_connect

logging.basicConfig(level=logging.INFO)


class WebSocketClient(ABC):
    """Base for web socket clients.
    """
    _websocket_client = None
    message_queue = deque([], 20)

    def __init__(self, url: str, io_loop=None):
        self.headers = HTTPHeaders({'Content-Type': "text/plain"})
        self.url = url
        # self._io_loop = io_loop or asyncio.get_event_loop()
        self._io_loop = io_loop or IOLoop.current()

    @abstractmethod
    def on_message(self, message: Union[str, bytes]):
        """子类需要自行实现的方法"""

    async def on_websocket_close(self):
        """注意这是当前 websocket 实例关闭时调用的方法，并非真正客户端关闭时调用的方法
        self._websocket_client 是连结服务器的客户端
        """
        while True:
            try:
                self._websocket_client = None
                await sleep(1.)
                await self.connect()
                if self._websocket_client:
                    break

            except Exception as err_info:
                logging.error("an error occurred when reconnecting", err_info)
                continue

            finally:
                if self._websocket_client is not None:
                    break

    def _connect_callback(self, future):
        """在此处添加连结成功后的回调
        """
        if future.exception() is None:
            self._websocket_client = future.result()
            logging.info("connect server %s succeed.", self.url)
        else:
            self._websocket_client = None
            logging.warning(f"connection lost {future.exception()}")

    async def connect(self):
        request = HTTPRequest(url=self.url, headers=self.headers)
        try:
            websocket_connect_future = websocket_connect(
                request, on_message_callback=self.on_message)
            websocket_connect_future.add_done_callback(self._connect_callback)
            await websocket_connect_future

        except Exception as err_info:
            logging.error("connect failed: %s", err_info)

    async def send(self, data: Union[str, bytes]) -> bool:
        """发送讯息使用的方法，如果发送失败则将要发送的内容存入一个快取队列
        (self.message_queue)中等待重新发送，但是当出现断线需要重连时不奏效
          :return : 是否发送成功
        """
        if not data:
            return False
        try:
            logging.info("posting message :%s", data)
            if self._websocket_client is None:
                self.message_queue.append(data)
                # await self.on_websocket_close()
                return False
            while len(self.message_queue):
                self._websocket_client.write_message(self.message_queue.pop())
            self._websocket_client.write_message(data)
        except tornado.websocket.WebSocketClosedError as err_info:
            self.message_queue.append(data)
            logging.error("send data to server failed: %s", err_info)
            await self.on_websocket_close()
            return False

        except Exception as err_info:
            self.message_queue.append(data)
            logging.error("send data to server failed: %s", err_info)
            return False
        else:
            return True

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self._websocket_client and self._websocket_client.close()


class DemoWebsocketClient(WebSocketClient):
    CALLBACK_TIME = 100  # 任务轮询时间（按毫秒记）
    IO_TIMEOUT = 2

    def __init__(self, url, io_loop=None):
        # io_loop = io_loop or asyncio.get_event_loop()
        super().__init__(url, io_loop)
        self.input_task = None

    async def random_generate_num(self):
        """随机生成一个数，等待随机时间，模拟产出数据
        """
        msg = format(time.strftime('%Y-%m-%d %X', time.localtime()), "s")
        msg = f"这是发送时间随机的消息{msg}"
        sleep_seconds = random.randint(2, 10)
        await asyncio.sleep(sleep_seconds)
        return str(msg)

    async def input_func(self, prompt: str = ""):
        """异步形式获取输入数据的函数"""
        with ThreadPoolExecutor(1, "AsyncInput",
                                lambda x: print(x, end="", flush=True),
                                (prompt, )) as executor:
            message = (await self._io_loop.run_in_executor(
                executor, sys.stdin.readline)).rstrip()
            return message

    async def input_func_1(self):
        await sleep(5)
        msg = format(time.strftime('%Y-%m-%d %X', time.localtime()), "s")
        msg = f"这是休眠5秒后生成的消息 {msg}"
        return msg

    async def task_run_until_complete(self):
        """调用异步获取输入数据函数的方法
        适合长期等待的场景
        """
        if self.input_task is None:
            self.input_task = asyncio.create_task(self.input_func())
            # self.input_task = asyncio.create_task(self.input_func_1())
        elif self.input_task.done():
            try:
                msg = await self.input_task
            except Exception as err_info:
                logging.error(err_info)
                pass
            else:
                await self.send(msg)
                self.input_task = asyncio.create_task(self.input_func())
                # self.input_task = asyncio.create_task(self.input_func_1())
        else:
            pass

    async def task_with_timeout(self):
        """等待固定时间获取数据，获取数据后发送
        适合需要超时机制的场景
        """
        try:
            msg = await asyncio.wait_for(self.random_generate_num(),
                                         timeout=self.IO_TIMEOUT)
        except (asyncio.TimeoutError, ):
            return
        else:
            await self.send(msg)

    def on_message(self, message: str = None):
        """收到消息时的回调"""
        try:
            if message is None:
                logging.info("web socket connection have disconnect")
            else:
                logging.info("receive message = %s", message)

        except Exception as err_info:
            logging.error("handle websocket message failed:%s", err_info)

    def run_forever(self):
        self._io_loop.current().run_sync(self.connect)
        # 带超时时间的任务
        # PeriodicCallback(self.task_with_timeout, self.CALLBACK_TIME).start()
        # 连续等待的任务
        PeriodicCallback(self.task_run_until_complete,
                         self.CALLBACK_TIME).start()
        try:
            self._io_loop.start()
        except (KeyboardInterrupt, ):
            logging.info("exiting...")
            self._io_loop.stop()

    def __del__(self):
        logging.info("exiting...")
        self._io_loop.stop()


async def send_single_msg(client: DemoWebsocketClient, msg: str):
    async with client as cl:
        await cl.send(msg)


if __name__ == "__main__":
    io_loop = asyncio.get_event_loop()
    client = DemoWebsocketClient("ws://127.0.0.1:8888/wsschat", io_loop)

    # client.run_forever()
    asyncio.run(
        send_single_msg(client,
                        f"消息 {time.strftime('%Y-%m-%d %X',time.localtime())}")
    )  # 此处会报错，但是不影响运行
    del client
