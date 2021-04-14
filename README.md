# reusable-code

# 包含了一些可以复用的样板代码

|             名称             |                                            用途                                             | 是否可靠 |
| :--------------------------: | :-----------------------------------------------------------------------------------------: | :------: |
|       deepin_directory       |        深入遍历文件夹，提供一个装饰器，按照生成器方式调用，改变了函数签名和调用方式         |    Y     |
|       detect_colour.py       |                         通过将图片转换成 HSV 颜色通道，进行颜色识别                         |    Y     |
|       detect_table.py        |                         用于将图片中表格的边框（包括内部边框）去除                          |    Y     |
|      floyd_steinberg.py      |                                 Floyd-Steinberg 算法的实现                                  |    Y     |
|  image_format_conversion.py  | Pillow、Numpy、二进制流几种图片形式相互转换，及大型数组通过 socket 传输到另一个 Python 进程 |    Y     |
|     image_skeletonize.py     |                                       图像内容骨架化                                        |    Y     |
|       rotate_point.py        |                         计算某一点围绕另一点旋转指定角度之后的座标                          |    Y     |
| test_yield_from_and_async.py |                                yield from 和异步生成器的写法                                |    Y     |
|          tiny_code           |                                      可复用的少量代码                                       |    Y     |
|     tornado_handlers.py      |                                       tornado 路由类                                        |    Y     |
|    tornado_web_server.py     |                            使用 ctrl+c 可以停止的 tornado 服务器                            |    Y     |
| tornado_web_server_legacy.py |        使用 ctrl+c 可以停止的 tornado 服务器，相容较旧版本 Python 或 tornado 的写法         |    Y     |
| tornado_websocket_client.py  |                            使用 totnado 实现的 websocket 客户端                             |    N     |
|           utils.py           |                               提供绝对单例类和同参单例类元类                                |    Y     |
|           .conkyrc           |                                         conky 配置                                          |    Y     |
|        settings.json         |                                    保存了 VS Code 的配置                                    |    Y     |
