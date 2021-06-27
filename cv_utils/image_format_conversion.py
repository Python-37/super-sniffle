__version__ = 1 + 1e-1 + 1j
__author__ = "Bavon C. K. Chao (赵庆华)"

import argparse
import base64
from io import BytesIO
from socket import AF_INET, SO_REUSEADDR, SOCK_STREAM, SOL_SOCKET, socket

import cv2
import numpy as np
from PIL import Image

# base64与opencv、numpy之间转换
# 图片转换成base64
image = cv2.imread("test.jpg", cv2.IMREAD_UNCHANGED)
# pillow形式
image_pillow = Image.fromarray(image)
# 使用pillow将图片转化为二进制流形式
image_io = BytesIO()
image_pillow.save(image_io, format="png")
is_succeed, image_encoded = cv2.imencode(".jpg", image)
# base64形式
image_b64 = base64.b64encode(image_encoded.tobytes()).decode()
# bytes流形式
# 实际上直接将image_encoded.tobytes()写入一个文件中也可以成功，此处显式进行一步转换是为了强调OpenCV的作用
image_bytes = BytesIO(image_encoded.tobytes())
image_bytes.seek(0)  # 此处将指针放到字节流开始处，可以进行读取
with open("output.jpg", "wb") as f:
    f.write(image_bytes.read())

# base64转回图片
image_b64 = base64.b64decode(image_b64)  # Python的base64字符串解码不接受带头
image_pillow = Image.open(BytesIO(image_b64))
# 以下两种等效
image_a = cv2.imdecode(np.asarray(bytearray(image_b64), dtype=np.uint8),
                       cv2.IMREAD_COLOR)
image_b = cv2.imdecode(np.frombuffer(image_b64, dtype=np.uint8),
                       cv2.IMREAD_COLOR)


def send_array(arr: np.ndarray, dest):
    array_send = memoryview(arr).cast('B')
    while len(array_send):
        size_sent = dest.send(array_send)
        print("发送数据大小：", size_sent)
        array_send = array_send[size_sent:]


def recv_array(arr: np.ndarray, source):
    array_recv = memoryview(arr).cast('B')
    while len(array_recv):
        size_recv = source.recv_into(array_recv)
        print("接收数据大小：", size_recv)
        array_recv = array_recv[size_recv:]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-mode", "--m", choices=("c", "s"), help="服务端还是客户端模式")
    args = parser.parse_args()
    if args.m == "s":
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        server_socket.bind(('', 25000))
        server_socket.listen(1)
        client_socket, client_address = server_socket.accept()
        print("侦测到客户端连结", client_socket)
        send_array(image, client_socket)
    if args.m == "c":
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect(('localhost', 25000))
        received_array = np.zeros_like(image)
        recv_array(received_array, client_socket)
        Image.fromarray(received_array[..., ::-1]).show()
