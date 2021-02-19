__version__ = 1 + 1e-1 + 1j
__author__ = "Bavon C. K. Chao (赵庆华)"

import os
from functools import partial, wraps
from typing import Generator, List


def deepin_dirs(func=None,
                file_type: List[str] = [],
                target_dir=".") -> Generator:
    """由于glob不能向下寻找多层文件夹，所以有了这样一个样板代码来实现，
    递归遍历文件夹装饰器，被装饰函数必须至少接受第一个位置参数表示文件名。
    NOTE 被装饰函数应当是针对单一文件进行处理的函数，加上本装饰器处理一个文件夹
    目标文件夹（即target_dir）最好是当前文件夹或当前文件夹下面一层文件夹，
    如果不需按照后缀名过滤文件，此处file_type保持空列表不变即可
    """
    if func is None:
        return partial(deepin_dirs, file_type=file_type, target_dir=target_dir)

    @wraps(func)
    def inner(*args, **kwargs):
        CURRENT_PATH = os.path.abspath(os.getcwd())
        for path_item in os.walk(target_dir):
            os.chdir(os.path.join(CURRENT_PATH, path_item[0]))
            for file_name in path_item[2]:
                current_file_type = file_name.split(".")[-1]
                if not file_type or current_file_type in file_type:
                    res = func(file_name, *args, **kwargs)
                    yield res
            os.chdir(CURRENT_PATH)

    return inner


@deepin_dirs(file_type=["jpg", "py"], target_dir=".")
def test(file_name, *args, **kwargs):
    print(args, kwargs)
    return os.path.abspath(file_name)


def list_dir(dir_name, deepth=0):
    """使用递归实现的类似tree命令"""
    os.chdir(dir_name)
    print("|" + "── " * deepth, os.getcwd())
    child_dirs = []
    for item in os.listdir("."):
        if os.path.isdir(item):
            child_dirs.append(item)
        else:
            print("|  " * (deepth + 1), "├── ", item, "    [",
                  os.path.getsize(item), "]")
    for child_dir in child_dirs:
        list_dir(child_dir, deepth + 1)
    os.chdir("..")


if __name__ == "__main__":
    list_dir(".")
    # for item in test("位置参数", test_arg="具名参数"):
    #     print(item)
