#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
使用了以下连结中提到的实现，赞最多的实现可以在较低版本中正常运作，
此处使用的是可以工作在新版本（Python 3.8）的实现。
https://stackoverflow.com/questions/17101502/how-to-stop-the-tornado-web-server-with-ctrlc
"""
__version__ = 1 + 1e-1 + 1j
__author__ = "Bavon C. K. Chao (赵庆华)"

import os
import signal
import time
from configparser import ConfigParser

import tornado
from tornado.ioloop import IOLoop
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


def sig_exit(signum, frame):
    t_logging.warning("exiting...")
    IOLoop.current().add_callback_from_signal(IOLoop.current().stop)


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
    t_options.parse_command_line()

    application.listen(HOST_PORT)
    signal.signal(signal.SIGINT, sig_exit)
    signal.signal(signal.SIGTERM, sig_exit)
    IOLoop.current().start()
