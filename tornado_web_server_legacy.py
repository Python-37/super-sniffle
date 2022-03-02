#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用了以下连结中提到的实现，可以正常运行在较低Python版本(如3.6)上
https://stackoverflow.com/questions/17101502/how-to-stop-the-tornado-web-server-with-ctrlc
"""
__version__ = 1 + 1e-1 + 2j
__author__ = "Bavon C. K. Chao (赵庆华)"

import os
import signal
import time

import tornado
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.log import logging as t_logging
from tornado.options import options as t_options

from tornado_web_server import application, config

tornado_settings = config["tornado server"]
HOST_PORT = tornado_settings.getint("host_port")


class MyHTTPServer(HTTPServer):
    is_closing = False

    def signal_handler(self, signum, frame):
        t_logging.info("exiting...")
        self.is_closing = True

    def try_exit(self):
        if self.is_closing:
            # clean up here
            tornado.ioloop.IOLoop.instance().stop()
            t_logging.info("exit success")


if __name__ == "__main__":
    t_options.logging = "debug"  # 日志等级 "debug|info|warning|error|none"
    t_options.log_rotate_mode = "time"
    # 时间单位 "other options:('S', 'M', 'H', 'D', 'W0'-'W6')"
    t_options.log_rotate_when = "D"
    t_options.log_rotate_interval = 5  # 间隔
    t_options.log_file_prefix = "%s/logs/app.log" % (os.path.dirname(os.path.abspath(__file__)),)
    t_options.log_file_num_backups = 0
    t_options.log_to_stderr = True  # 输出到屏幕
    t_options.define("port", default=HOST_PORT, type=int)
    t_options.parse_command_line()

    sockets = tornado.netutil.bind_sockets(t_options.port)
    # tornado.process.fork_processes(1)  # not available on windows
    server = MyHTTPServer(application)
    server.add_sockets(sockets)

    signal.signal(signal.SIGINT, server.signal_handler)
    PeriodicCallback(server.try_exit, 100).start()
    IOLoop.instance().start()
