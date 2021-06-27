__version__ = 1 + 1e-1 + 1j
__author__ = "Bavon C. K. Chao (赵庆华)"

import asyncio

import numpy as np


async def yiled_number(num_list):
    for idx, num in enumerate(num_list):
        await asyncio.sleep(.6)
        # if (b := np.mean(num)) < 73:
        if np.mean(num) < 73:
            yield idx, np.mean(num)


async def async_func_1():
    await asyncio.sleep(3)
    print(f"succeed {async_func_1.__name__}")
    return f"succeed {async_func_1.__name__}"


async def async_func_2():
    await asyncio.sleep(1.5)
    print(f"succeed {async_func_2.__name__}")
    return f"succeed {async_func_2.__name__}"


async def async_main():
    a_array = np.random.randint(50, 100, (10, 10))
    task1 = asyncio.create_task(async_func_1())
    task2 = asyncio.create_task(async_func_2())
    # res = asyncio.gather(async_func_1(), async_func_2())
    async for res in yiled_number(a_array):
        print(res)
    res = asyncio.gather(task1, task2)


def test_yield(num_list):
    idx = 0
    while -len(num_list) <= idx < len(num_list):
        res = yield num_list[idx]
        if res is None:
            idx += 1
        elif isinstance(res, int):
            idx = res


def test_yield_from_1():
    a = np.random.randint(50, 100, (10, 10))
    # a = list(range(10))
    yield from test_yield(a)


def test_yield_from_2():
    a = np.random.randint(50, 100, (10, 10))
    # a = list(range(10))
    b = iter(test_yield(a))
    print(next(b))
    while True:
        random_idx = np.random.randint(-len(a), len(a) + 1)
        try:
            res = b.send(random_idx)
        except StopIteration:
            print(random_idx, "迭代结束")
            break
        else:
            yield random_idx, res


if __name__ == "__main__":
    asyncio.run(async_main())
    for i in test_yield_from_1():
        print(i)
    for i in test_yield_from_2():
        print(i)
