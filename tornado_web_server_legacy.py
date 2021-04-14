#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用了以下连结中提到的实现，可以正常运行在较低Python版本(如3.6)上
https://stackoverflow.com/questions/17101502/how-to-stop-the-tornado-web-server-with-ctrlc
"""
__version__ = 1 + 1e-1 + 1j
__author__ = "Bavon C. K. Chao (赵庆华)"

import os
import signal
import time
from configparser import ConfigParser

import tornado
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.log import logging as t_logging
from tornado.options import options as t_options
from tornado.web import Application, StaticFileHandler

from tornado_handlers import (BaseHandler, CalcPageHandler, ChatHandler,
                              ChatPageHandler, CheckLoggedMixin,
                              UploadFileHandler, UserLogin, UserLogout,
                              UserRegis)

os.makedirs("logs", exist_ok=True)
config = ConfigParser()
config.read("settings.ini")
tornado_settings = config["tornado server"]
HOST_PORT = tornado_settings.getint("host_port")


class MainHandler(CheckLoggedMixin, BaseHandler):
    """处理主页请求"""
    def get(self, *args, **kwargs):
        user_name, logged_in = self.check_login()
        params = {"logged_in": logged_in, "logging_in": False}
        self.render("index.html", **params)

    def post(self, *args, **kwargs):
        super().post(*args, **kwargs)
        self.write({"msg": "succeed"})


class DownloadHandler(CheckLoggedMixin, StaticFileHandler):
    """处理需要登录才能下载的文件"""
    async def get(self, *args, **kwargs) -> None:
        user_name, logged_in = self.check_login()
        if not logged_in:
            # 没登录禁止下载
            raise tornado.web.HTTPError(
                403.16,
                log_message=f"{user_name} 企图下载 {args}，但未成功",
                reason="Must login")
        t_logging.info(f"{user_name} 正在下载 {args}")
        await super().get(*args, **kwargs)


application = Application(
    [
        (r"/$", MainHandler),
        (r'/login', UserLogin),
        (r'/logout', UserLogout),
        (r'/regis', UserRegis),
        (r'/calc(ulator)?(\.html)?$', CalcPageHandler),
        (r"/chat(room)?(\.html)?$", ChatPageHandler),
        (r"/wsschat$", ChatHandler),
        (r"/file(s)?(\.html)?$", UploadFileHandler),
        (rf"/{tornado_settings['file_upload_dir']}/(.*\.*[\w\d]+)$",
         DownloadHandler, {
             "path": tornado_settings["file_upload_dir"],
         }),
        (r"/(.*\.(?!py\w*)\w+)$", StaticFileHandler, {
            "path": tornado_settings["static_dir"],
            "default_filename": "README.md"
        }),
    ],
    static_path=tornado_settings.get("static_dir"),
    template_path=tornado_settings.get("template_dir"),
    cookie_secret=tornado_settings.get("cookie_secret"),
    login_url='/login',
    xsrf_cookies=True,
    debug=tornado_settings.getboolean("debug"),
    autoreload=False,
)


class MyHTTPServer(HTTPServer):
    is_closing = False

    def signal_handler(self, signum, frame):
        t_logging.info('exiting...')
        self.is_closing = True

    def try_exit(self):
        if self.is_closing:
            # clean up here
            tornado.ioloop.IOLoop.instance().stop()
            t_logging.info('exit success')


if __name__ == "__main__":
    t_options.logging = "debug"  # 日志等级 "debug|info|warning|error|none"
    t_options.log_rotate_mode = "time"
    # 时间单位 "other options:('S', 'M', 'H', 'D', 'W0'-'W6')"
    t_options.log_rotate_when = "D"
    t_options.log_rotate_interval = 5  # 间隔
    t_options.log_file_prefix = "%s/logs/%s.log" % (os.path.dirname(
        os.path.abspath(__file__)), time.strftime("%Y-%m-%d"))  # 文件名
    t_options.log_file_num_backups = 10  # 间隔
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
