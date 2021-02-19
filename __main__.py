print("""本模块提供了一些可复用的代码，主要包括：\n
deepin_directory: 深入遍历文件夹，提供一个装饰器，按照生成器方式调用，改变了函数签名和调用方式
detect_colour.py: 通过将图片转换成HSV颜色通道，进行颜色识别
detect_table.py: 用于将图片中表格的边框（包括内部边框）去除
image_format_conversion.py: Pillow、Numpy、二进制流几种图片形式相互转换，及大型数组通过socket传输到另一个Python进程
rotate_point.py: 计算某一点围绕另一点旋转指定角度之后的座标
tornado_web_server.py: 使用ctrl+c可以停止的tornado服务器
test_yield_from_and_async.py: yield from和异步生成器的写法
tornado_websocket_client.py: 使用 totnado 实现的 websocket 客户端
utils.py: 提供绝对单例类和同参单例类元类
""")
