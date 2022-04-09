## KDE 图形介面设定

```text
系统设定->工作空间->工作空间行为->一般行为->按两下开启档案与资料夹
视窗管理->视窗行为->视窗动作->内部视窗、标题列及边框动作左键无动作
底部栏右键->设定 只有图示的工作管理员->行为->使用滑鼠滚轮循环切换工作 取消勾选
```

## Linux 必要软件

```
aria2 firefox-esr openbsd-netcat
fcitx fcitx-rime rsync terminator tree vim zsh light-locker
7z ark dolphin
flameshot kate kolourpaint kmix awesome blueman conky network-manager-applet
```

#### xfce 桌面锁屏工具

> 卸载 xfce4-screensaver
> 安装 light-locker

## 解决无法使用中文输入法问题

```bash
vim ~/.xprofile
```

```text
export GTK_IM_MODULE=fcitx
export QT_IM_MODULE=fcitx
export XMODIFIERS="@im=fcitx"
```

## Docker 常用指令

```bash
docker build -t py38:v1.0 .
docker run -i -t -p 8000:8000 -v /path/to/code_dir:/home --name test py38:v1.0 python3.8 tornado_web_server.py -port=8000
```

## Firefox 扩展套件

```text
Dark Reader
FoxyProxy Standard
HTTPS Everywhere
Tampermonkey
uBlock Origin
Wappalyzer
Weather Extension
Bing Search Engine
```

## 配置 zsh

```bash
sh -c "$(curl -fsSL https://raw.github.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"
```

## 将 VS Code 快捷方式添加到桌面

```bash
vim ~/桌面/VSCode.desktop
```

```text
#!/usr/bin/env xdg-open
[Desktop Entry]
Name=Visual Studio Code
Comment=Multi-platform code editor for Linux
Exec=/opt/VSCode-linux-x64/code
Icon=/opt/VSCode-linux-x64/resources/app/resources/linux/code.png
Type=Application
StartupNotify=true
Categories=TextEditor;Development;Utility;
MimeType=text/plain;
```

## VS Code 添加网易云音乐插件无法使用问题

```python
import re
import argparse
import zipfile
from io import BytesIO

from tornado.httpclient import HTTPClient, HTTPError


def download_ffmpeg(vscode_version):
    FIND_FFMPEG_VERSION_RE = re.compile(
        r"disturl.*?https\://electronjs.org/headers.*?" \
        r"target.*?(\d+\.\d+\.\d+).*runtime.*?electron",
        re.S)
    http_client = HTTPClient()
    try:
        response = http_client.fetch(
            f"https://github.com/microsoft/vscode/blob/{vscode_version}/.yarnrc"
        )
        ffmpeg_version = response.body.decode()
    except HTTPError as e:
        # HTTPError is raised for non-200 responses; the response
        # can be found in e.response.
        print("Error: " + str(e))
        return
    except Exception as e:
        print("Error: " + str(e))
        return

    ffmpeg_version = FIND_FFMPEG_VERSION_RE.findall(ffmpeg_version)
    if not ffmpeg_version:
        print("匹配当前VS Code版本出现错误，开始手动匹配")
        print("正则表达式变量名是`FIND_FFMPEG_VERSION_RE`")
        print("正则匹配结果变量名是`ffmpeg_version`")
        breakpoint()
    ffmpeg_version = ffmpeg_version[0]
    print(f"VS Code {vscode_version} 对应的 ffmpeg 版本为：{ffmpeg_version}，正在下载")
    ffmpeg_down_url = f"https://cdn.npm.taobao.org/dist/electron/{ffmpeg_version}" \
                      f"/ffmpeg-v{ffmpeg_version}-linux-x64.zip"

    ffmpeg = http_client.fetch(ffmpeg_down_url)
    if not 200 <= int(ffmpeg.code) < 300:
        print(f"下载ffmpeg {ffmpeg_version} 出错")
        exit(1)
    ffmpeg = BytesIO(ffmpeg.body)
    print("正在解压ffmpeg")
    fz = zipfile.ZipFile(ffmpeg, "r")
    for file in fz.namelist():
        fz.extract(file)


def arg_parser():
    parser = argparse.ArgumentParser(
        f"python {__file__} vscode 版本，如python {__file__} 1.41.1")
    parser.add_argument("vscode_version", help="VS Code 的版本")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = arg_parser()
    download_ffmpeg(args.vscode_version)

```

```text
将libffmpeg放到vs code安装目录下同名文件位置替换掉
```

## 将 git 提交历史记录删除

```bash
git checkout --orphan latest_branch
git add -A
git commit -am "这里是commit信息"
git branch -D master
git branch -m master
git push -f origin master
```

## Windows 手动安装最新版本 OpenCV

#### 方法 1

```text
下载 https://sourceforge.net/projects/opencvlibrary/files/ 中的exe
运行exe，程序会解压文件到指定文件夹
将 build/x64/vc15/bin 中的dll复制到 python/cv2/ 当前Python版本文件夹下
复制cv2文件夹到Python安装路径 Lib/site-packages/ 下
```

#### 方法 2

```text
下载 https://sourceforge.net/projects/opencvlibrary/files/ 中的形如opencv-4.3.0-dldt-2020.2-vc16-avx2.zip文件名的压缩档，大小在200兆以上
解压压缩档到指定文件夹
将 build/bin 中的dll复制到 build/python/cv2/ 当前Python版本文件夹下
复制cv2文件夹到Python安装路径 Lib/site-packages/ 下
```

## Git 配置

```ini
[core]
	repositoryformatversion = 0
	filemode = false
	bare = false
	logallrefupdates = true
	symlinks = false
	ignorecase = true
	autocrlf = true
	eol = lf
```

## 删除 powershell 历史

```
Remove-Item (Get-PSReadlineOption).HistorySavePath
```
