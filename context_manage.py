import time
from contextlib import contextmanager


class CheckIn:
    def __init__(self, name, office_location):
        self.name = name
        self.office_location = office_location
        self.file = None

    def __enter__(self):
        print(f"{self.name} 你好，你已经在{self.office_location} 完成签到打卡")
        now_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        file = open(f"work-{now_time_str}.txt", "w")
        self.file = file
        return file

    def __exit__(self, exc_type, exc_value, trace_back_info):
        print(f"{self.name} 你好，你已经在{self.office_location} 完成签退打卡")
        self.file.close()


@contextmanager
def check_in(name, office_location):
    now_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    file = open(f"work-{now_time_str}.txt", "w")
    try:
        print(f"{name} 你好，你已经在{office_location} 完成签到打卡")
        yield file
    finally:
        print(f"{name} 你好，你已经在{office_location} 完成签退打卡")
        file.close()


if __name__ == "__main__":
    with check_in("华哥", "开放办公区") as pub_office:
        pub_office.write("开放式办公区 签到")
        now_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        pub_office.write(now_time_str)
        pub_office.write("\n")
        time.sleep(1.5)

        with check_in("华哥", "封闭办公区") as pri_office:
            pri_office.write("封闭式办公区 签到")
            now_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            pri_office.write(now_time_str)
            pri_office.write("\n")
            # raise Exception("媳妇快生了，得赶紧去医院")
            time.sleep(1.5)
            pri_office.write("封闭式办公区 签退")
            now_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            pri_office.write(now_time_str)

        pub_office.write("开放式办公区 签退")
        now_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        pub_office.write(now_time_str)

    # with CheckIn("华哥", "开放办公区") as pub_office:
    #     pub_office.write("开放式办公区 签到")
    #     now_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    #     pub_office.write(now_time_str)
    #     pub_office.write("\n")
    #     raise Exception("媳妇快生了，得赶紧去医院")
    #     time.sleep(1.5)

    #     with CheckIn("华哥", "封闭办公区") as pri_office:
    #         pri_office.write("封闭式办公区 签到")
    #         now_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    #         pri_office.write(now_time_str)
    #         pri_office.write("\n")
    #         time.sleep(1.5)
    #         pri_office.write("封闭式办公区 签退")
    #         now_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    #         pri_office.write(now_time_str)

    #     pub_office.write("开放式办公区 签退")
    #     now_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    #     pub_office.write(now_time_str)
