import getpass
import os
import re
from io import BytesIO
from zipfile import ZipFile

try:
    from Crypto import Random
    from Crypto.Cipher import AES
    from Crypto.Hash import SHA256
except ImportError:
    print("\033[37;41m pip install pycryptodome \033[0m")
    exit(1)

# 跳过档案的规则
SKIP_FILES = (re.compile(r".*[/\\]\.git/.*"), re.compile(r"\.[/\\]\.vscode"),
              re.compile(r".*\.png$",
                         flags=re.I), re.compile(r".*\.jpg$", flags=re.I),
              re.compile(r".*\.jpeg$", flags=re.I), re.compile(r".*[/\\]logs"),
              re.compile(r"\.[/\\]files"),
              re.compile(r".*[/\\]__pycache__[/\\]"),
              re.compile(r".*\.py[co]$"), re.compile(r"\.[/\\]codes\.py$"),
              re.compile(r".*\.zip$",
                         flags=re.I), re.compile(r".*\.bin$", flags=re.I))

# 不跳过这些档案，优先级高于上面跳过档案规则
NONSKIP_FILES = (re.compile(r"\.[/\\]static"), re.compile(r"\.[/\\]template"))

content = BytesIO()
with ZipFile(content, mode="w") as myzip:
    for dirpath, dirnames, file_names in os.walk("."):
        for file_name in file_names:
            full_filename = os.path.join(dirpath, file_name)
            for rule in NONSKIP_FILES:
                # 优先尝试匹配不跳过的规则
                if rule.match(full_filename):
                    print(full_filename)
                    myzip.write(full_filename)
                    break
            else:
                for rule in SKIP_FILES:
                    # 如果匹配到跳过该文件的规则则不处理
                    if rule.match(full_filename):
                        break
                else:
                    print(full_filename)
                    myzip.write(full_filename)

content.seek(0)


def encrypt(key, source):
    key = SHA256.new(
        key).digest()  # use SHA-256 over our key to get a proper-sized AES key
    IV = Random.new().read(AES.block_size)  # generate IV
    encryptor = AES.new(key, AES.MODE_CBC, IV)
    padding = AES.block_size - len(
        source) % AES.block_size  # calculate needed padding
    source += bytes(
        [padding]) * padding  # Python 2.x: source += chr(padding) * padding
    data = IV + encryptor.encrypt(
        source)  # store the IV at the beginning and encrypt
    return data


passwd = getpass.getpass("Input unzip password:")
passwd1 = getpass.getpass("Confirm password:")
if passwd != passwd1:
    print("\033[37;41m The passwords entered are inconsistent  \033[0m")
    exit(1)
content_encrypted = encrypt(passwd.encode("utf-8"), content.read())

codes_content = f"""
import getpass
from io import BytesIO
from zipfile import ZipFile

try:
    from Crypto.Cipher import AES
    from Crypto.Hash import SHA256
except ImportError:
    print("\\033[37;41m pip install pycryptodome \\033[0m")
    exit(1)


def decrypt(key, source):
    key = SHA256.new(
        key).digest()  # use SHA-256 over our key to get a proper-sized AES key
    IV = source[:AES.block_size]  # extract the IV from the beginning
    decryptor = AES.new(key, AES.MODE_CBC, IV)
    data = decryptor.decrypt(source[AES.block_size:])  # decrypt
    padding = data[
        -1]  # pick the padding value from the end; Python 2.x: ord(data[-1])
    if data[-padding:] != bytes([padding]) * padding:
        # Python 2.x: chr(padding) * padding
        raise ValueError("Invalid padding...")
    return data[:-padding]  # remove the padding


content = {content_encrypted}

passwd = getpass.getpass("Input unzip password:")
content = decrypt(passwd.encode("utf-8"), content)

zf = ZipFile(BytesIO(content), mode="r")
zf.extractall(path=".")
"""

with open("codes.py", "w", encoding="utf-8") as f:
    f.write(codes_content)
pass
