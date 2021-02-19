#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = 1 + 1e-1 + 1j
__author__ = "Bavon C. K. Chao (赵庆华)"

import datetime
import hashlib
import hmac
import os
import os.path as opth
import socket
import sqlite3
import time
import urllib
from configparser import ConfigParser
from typing import Tuple, Union

import tornado
from tornado.escape import utf8
from tornado.log import logging as t_logging
from tornado.web import HTTPError, RequestHandler, authenticated
from tornado.websocket import WebSocketHandler

os.makedirs("logs", exist_ok=True)
config = ConfigParser()
config.read("settings.ini")
tornado_settings = config["tornado server"]
HOST_NAME = socket.getfqdn(socket.gethostname())
HOST_IP = socket.gethostbyname(HOST_NAME)
LOCAL_IP = tornado_settings["local_ip"]
HOST_PORT = tornado_settings.getint("host_port")

userdb_conn = sqlite3.connect("file:logs/users.db3?mode=rwc", uri=True)
userdb_cursor = userdb_conn.cursor()
userdb_cursor.execute(
    "CREATE TABLE IF NOT EXISTS `user` (id INTEGER PRIMARY " \
    "KEY AUTOINCREMENT, name text, password text)"
)


class BaseHandler(RequestHandler):
    """解决JS跨域请求、编码等问题"""
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Accept-Charset', 'utf-8')

    def check_xsrf_cookie(self):
        try:
            super().check_xsrf_cookie()
        except HTTPError:
            post_data = tornado.escape.json_decode(self.request.body)
            token = post_data.get("_xsrf")
            if not token:
                raise HTTPError(403, "'_xsrf' argument missing from POST")
            _, token, _ = self._decode_xsrf_token(token)
            _, expected_token, _ = self._get_raw_xsrf_token()
            if not token:
                raise HTTPError(403, "'_xsrf' argument has invalid format")
            if not hmac.compare_digest(utf8(token), utf8(expected_token)):
                raise HTTPError(403,
                                "XSRF cookie does not match POST argument")

    def post(self, *args, **kwargs):
        self.set_header('Content-type', 'application/json;charset=UTF-8')


class MustLoginMixin:
    """支持根据登录状态鉴权的混入类"""
    __slots__ = ()

    def get_current_user(self):
        return self.get_secure_cookie("uname")


class CheckLoggedMixin:
    """检查是否已经登录和获取用户名的混入类"""
    __slots__ = ()

    def check_login(
            self: Union[RequestHandler, WebSocketHandler]) -> Tuple[str, bool]:
        """用于检查是否已经登入"""
        user_name = self.get_secure_cookie("uname")
        user_ip = "管理员" if self.request.remote_ip == \
            LOCAL_IP else self.request.remote_ip
        user_ip = user_name or user_ip
        user_ip = user_ip.decode() if isinstance(user_ip, bytes) else user_ip
        return user_ip, user_name is not None


class UserLogin(CheckLoggedMixin, MustLoginMixin, BaseHandler):
    async def get(self):
        _, logged_in = self.check_login()
        params = {
            "title": "登入",
            "notice_message": "",
            "logged_in": logged_in,
            "logging_in": True
        }
        return self.render("login.html", **params)

    def post(self):
        uname = self.get_argument('uname')
        upass = self.get_argument('upass')
        text = uname + upass
        md5pass = hashlib.md5(text.encode()).hexdigest()
        cur = userdb_cursor.execute("SELECT password FROM user WHERE name=(?)",
                                    (uname, ))
        r = cur.fetchone()
        if r:
            password = r[0]
            if password == md5pass:
                self.set_secure_cookie('uname', uname)
                return self.redirect("/")
            else:
                params = dict(title="登入",
                              logging_in=True,
                              logged_in=False,
                              notice_message="输入正确的用户名或密码")
                return self.render("login.html", **params)
        else:
            return self.redirect("/regis")


class UserLogout(MustLoginMixin, BaseHandler):
    async def get(self):
        self.clear_cookie("uname")
        return self.redirect('/')


class UserRegis(CheckLoggedMixin, MustLoginMixin, BaseHandler):
    async def get(self):
        _, logged_in = self.check_login()
        params = {
            "notice_message": "",
            "logging_in": True,
            "logged_in": logged_in
        }
        return self.render("regis.html", **params)

    def post(self):
        _, logged_in = self.check_login()
        params = {
            "notice_message": "此用户名已存在",
            "logging_in": True,
            "logged_in": logged_in
        }
        uname = self.get_argument('uname', None)
        with userdb_conn:
            cur = userdb_conn.execute(
                "SELECT name FROM user WHERE name == (?)", (uname, ))
        if cur.fetchone():
            return self.render("regis.html", **params)
        upass = self.get_argument('upass', None)
        text = uname + upass
        md5pass = hashlib.md5(text.encode()).hexdigest()
        with userdb_conn:
            userdb_conn.execute(
                "INSERT INTO `user` (`id`, `name`, `password`) VALUES (NULL, ?, ?)",
                (uname, md5pass))
        return self.redirect('/login')


class ChatHandler(CheckLoggedMixin, WebSocketHandler):
    """使用 WebSocket 实现的聊天服务器
    """
    users = set()  # 用来存放在线用户的容器
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    LOCAL_ADDR = f"{LOCAL_IP}:{HOST_PORT}"
    HOST_ADDR = f"{HOST_IP}:{HOST_PORT}"
    # 如果没有 logs 文件夹则新建一个
    if not opth.exists("logs") or not opth.isdir("logs"):
        os.mkdir("logs")
    sql_conn = sqlite3.connect(
        f"file:logs/{time.strftime('%Y-%m-%d', time.localtime())}.db3?mode=rwc",
        uri=True)
    sql_cursor = sql_conn.cursor()
    sql_cursor.execute(
        "CREATE TABLE IF NOT EXISTS `messages` (msg text, msg_id " \
        "INTEGER PRIMARY KEY AUTOINCREMENT)")

    def open(self):
        self.users.add(self)  # 建立连接后添加用户到容器中
        user_ip, _ = self.check_login()
        current_time = datetime.datetime.now().strftime(self.DATETIME_FORMAT)
        message_str = u"[%s]-[%s]-进入聊天室，当前在线人数 [%s]" % (user_ip, current_time,
                                                        len(self.users))
        for user in self.users:  # 向已在线用户发送消息
            user.write_message(message_str)
        for history_msg in self.sql_cursor.execute(
                "SELECT msg FROM messages WHERE msg_id > " \
                "(SELECT count(msg_id) FROM messages) - ?;", \
                (tornado_settings.getint("message_buffer_size"), )):  # noqa
            self.write_message(history_msg[0])

    def on_message(self, message):
        user_ip, _ = self.check_login()
        current_time = datetime.datetime.now().strftime(self.DATETIME_FORMAT)
        message_str = u"[%s]-[%s]-说：%s" % (user_ip, current_time, message)
        for user in self.users:  # 向在线用户广播消息
            user.write_message(message_str)

        self.update_log(message_str)

    def on_close(self):
        self.users.remove(self)  # 用户关闭连接后从容器中移除用户
        user_ip, _ = self.check_login()
        current_time = datetime.datetime.now().strftime(self.DATETIME_FORMAT)
        message_str = u"[%s]-[%s]-离开聊天室，当前在线人数 [%s]" % (user_ip, current_time,
                                                        len(self.users))
        for user in self.users:
            user.write_message(message_str)

    @classmethod
    def update_log(cls, chat):
        try:
            with cls.sql_conn:
                cls.sql_conn.execute("INSERT INTO messages VALUES (?, ?)",
                                     (chat, None))
        except sqlite3.Error as e:
            t_logging.error("消息无法写入日志", e.args[0])
            return

    def check_origin(self, origin):
        # 接受所有跨源流量
        # return True
        # 允许来自站点子域的连接
        parsed_origin = urllib.parse.urlparse(origin)
        net_loc = parsed_origin.netloc
        if net_loc.endswith(self.LOCAL_ADDR) or net_loc.endswith(
                self.HOST_ADDR):
            return True
        return False


class ChatPageHandler(CheckLoggedMixin, BaseHandler):
    """处理聊天室网页内容显示"""
    def get(self, *args, **kwargs):
        user_name, logged_in = self.check_login()
        params = {
            "user_name": user_name,
            "logged_in": logged_in,
            "logging_in": False
        }
        self.render("chatroom.html", **params)


class CalcPageHandler(CheckLoggedMixin, BaseHandler):
    """处理聊天室网页内容显示"""
    def get(self, *args, **kwargs):
        _, logged_in = self.check_login()
        params = {"logged_in": logged_in, "logging_in": False}
        self.render("calc.html", **params)


class UploadFileHandler(CheckLoggedMixin, MustLoginMixin, BaseHandler):
    """文件上传下载功能"""
    SIZE_UNIT = ("B", "KB", "MB", "GB", "TB")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 文件的暂存路径
        self.upload_path = opth.join(opth.dirname(__file__),
                                     tornado_settings["file_upload_dir"])
        if not opth.exists(self.upload_path) or not opth.isdir(
                self.upload_path):
            os.mkdir(self.upload_path)

    @classmethod
    def get_size(cls, size, i=0):
        """计算文件大小，最大单位为 TB"""
        if size < 1024 or i >= len(cls.SIZE_UNIT) - 1:
            return "%.2f %s" % (size, cls.SIZE_UNIT[i])
        return cls.get_size(size / 1024, i + 1)

    @authenticated
    def get(self, *args, **kwargs):
        _, logged_in = self.check_login()
        files = os.listdir(self.upload_path)
        files = list(
            filter(lambda item: opth.isfile(opth.join(self.upload_path, item)),
                   files))
        sizes = list(
            map(lambda item: opth.getsize(opth.join(self.upload_path, item)),
                files))
        sizes = list(map(self.get_size, sizes))
        param_keys = ("dir_name", "files", "sizes", "logged_in", "logging_in")
        param_values = (opth.split(self.upload_path)[-1], files, sizes,
                        logged_in, False)
        params = {k: v for k, v in zip(param_keys, param_values)}
        self.render("files.html", **params)

    @authenticated
    def post(self, *args, **kwargs):
        # 提取表单中 name 为 file 的文件元数据
        file_metas = self.request.files.get("file", None)
        if file_metas:
            for meta in file_metas:
                filename = meta['filename']
                filepath = opth.join(self.upload_path, filename)
                with open(filepath, 'wb') as up:
                    up.write(meta['body'])
        # 上传成功后稍加等待自动跳转回上一介面
        self.write(
            "上传完成，返回上一介面<script>setTimeout(function () " \
            "{window.history.go(-1);}, 3000);</script>"
        )
