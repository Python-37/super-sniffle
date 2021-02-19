// 定义表情与相关资源的键值对，表情动画数据会根据 key 进行访问。
const stickers = {
    bomb: {
        path: "./3145-bomb.json",
    },
    pumpkin: {
        path: "./43215-pumpkins-sticker-4.json",
    },
};

// 获取 DOM 控件
const panelEle = document.querySelector(".panel");
const chooseStickerBtn = document.querySelector(".chooseSticker");
const stickersEle = document.querySelector(".stickers");
const msgInputEle = document.querySelector(".messageInput");
const sendBtn = document.querySelector(".send");

// 初始化表情面板，也可以在表情选择窗弹出时再初始化
Object.keys(stickers).forEach((key) => {
    const lottieEle = stickersEle.appendChild(document.createElement("span"));
    // 对每个表情创建 lottie 播放器
    const player = lottie.loadAnimation({
        container: lottieEle,
        renderer: "svg",
        loop: true,
        autoplay: false,
        path: stickers[key].path,
    });

    // 当选择表情时，发送消息，并设置类型为 sticker 表情消息
    lottieEle.addEventListener("click", () => {
        WebSocketSend(key);
        // appendMsg(key, "sticker", "mine");
    });

    // 当鼠标划过时，播放动画预览
    lottieEle.addEventListener("mouseover", () => {
        player.play();
    });
    // 当鼠标划过时，停止动画预览
    lottieEle.addEventListener("mouseleave", () => {
        player.stop();
    });
});

// 点击选择表情按钮时，展示表情弹窗
chooseStickerBtn.addEventListener("click", () => {
    stickersEle.classList.toggle("show");
});

// 点击发送按钮时，发送普通消息
sendBtn.addEventListener("click", () => {
    const msg = msgInputEle.value;
    if (msg) {
        appendMsg(msg, "", "mine");
    }
});

/**
 * 追加消息到消息列表，如果是普通消息则直接追加，如果是表情消息则播放动画
 * 如果选择是“地雷”表情，播放爆炸动画并给消息添加震动效果动画
 * @param {string} msg
 * @param {string} type
 */
function appendMsg(msg, type, whos) {
    // 创建消息元素
    const msgEle = panelEle.appendChild(document.createElement("div"));
    msgEle.classList.add("message", whos); // 设置为“我“发送的样式
    msgEle.innerHTML = `
        <img class="avatar" src="./${whos}.png" alt="" />
        <p><span>${type === "sticker" ? "" : msg}</span></p>
    `;
    if (type == "sticker") {
        // 处理表情消息，播放相关动画
        playSticker(msg, msgEle);
        if (msg === "bomb") {
            // 播放爆炸动画
            setTimeout(() => {
                playExplosion(msgEle);
            }, 800);

            // 晃动消息列表
            shakeMessages();
        }
    }

    // 滚动到最新消息
    panelEle.scrollTop = panelEle.scrollHeight;
    msgInputEle.value = "";
}

/**
 * 播放表情动画
 * @param {string} key
 * @param {HTMLElement} msgEle
 */
function playSticker(key, msgEle) {
    // 表情消息，创建 lottie 动画
    const lottieEle = msgEle.querySelector("span");
    lottieEle.style.width = "40px";
    lottieEle.style.height = "40px";
    lottie.loadAnimation({
        container: lottieEle,
        renderer: "svg",
        loop: false,
        autoplay: true,
        path: stickers[key].path,
    });
}

function playExplosion(anchor) {
    const explosionAnimeEle = anchor.appendChild(document.createElement("div"));
    explosionAnimeEle.style.position = "absolute";
    explosionAnimeEle.style.width = "200px";
    explosionAnimeEle.style.height = "100px";
    explosionAnimeEle.style.right = 0;
    explosionAnimeEle.style.bottom = 0;

    const explosionPlayer = lottie.loadAnimation({
        container: explosionAnimeEle,
        renderer: "svg",
        loop: false,
        autoplay: true,
        path: "./9990-explosion.json",
    });
    explosionPlayer.setSpeed(0.3);
    // 播放完成后，销毁爆炸相关的动画和元素
    explosionPlayer.addEventListener("complete", () => {
        explosionPlayer.destroy();
        explosionAnimeEle.remove();
    });
}

/**
 * 对最新的 5 条消息添加晃动动画
 * @param {HTMLElement} panelEle
 */
function shakeMessages() {
    [...panelEle.children]
        .reverse()
        .slice(0, 5)
        .forEach((messageEle) => {
            const avatarEle = messageEle.querySelector("img");
            const msgContentEle = messageEle.querySelector("p");
            avatarEle.classList.remove("shake");
            msgContentEle.classList.remove("shake");
            setTimeout(() => {
                avatarEle.classList.add("shake");
                msgContentEle.classList.add("shake");
            }, 700);
        });
}

// 消息发送接收相关
var send_msg = document.getElementById("text");
var match_URL_re =
    "^((https|http|ftp|rtsp|mms)?://)" +
    "?(([0-9a-z_!~*'().&=+$%-]+: )?[0-9a-z_!~*'().&=+$%-]+@)?" + //ftp的user@
    "(([0-9]{1,3}.){3}[0-9]{1,3}" + // IP形式的URL- 199.194.52.184
    "|" + // 允许IP和DOMAIN（域名）
    "([0-9a-z_!~*'()-]+.)*" + // 域名- www.
    "([0-9a-z][0-9a-z-]{0,61})?[0-9a-z]." + // 二级域名
    "[a-z]{2,6})" + // first level domain- .com or .museum
    "(:[0-9]{1,5})?"; // 端口
var match_msg_re = /^\[(.+?)\]\-\[\d{4}\-\d{2}\-\d{2} \d{2}\:\d{2}:\d{2}\]\-说：(.*)/;
var match_URL_re = new RegExp(match_URL_re);
var current_URL = match_URL_re.exec(document.baseURI);
$(document).ready(function () {
    cleanup();
}); // 加载页面时将残留信息清除
function cleanup() {
    send_msg.value = "";
}

if ("WebSocket" in window) {
    /*判断浏览器是否支持WebSocket接口*/
    /*创建创建 WebSocket 对象，协议本身使用新的ws://URL格式*/
    var Socket = new WebSocket(
        "ws://" + current_URL[0].replace(current_URL[1], "") + "/wsschat"
    );
    /*连接建立时触发*/
    Socket.onopen = function () {
        appendMsg("连接已建立！╰(￣▽￣)╮", "", "yours");
        $(".send #text").attr("disabled", false);
    };
    /*客户端接收服务端数据时触发*/
    Socket.onmessage = function (ev) {
        var received_msg = ev.data; /*接受消息*/
        matched_user_name = match_msg_re.exec(received_msg);
        if (matched_user_name == null) {
            whos = "yours";
            msg_type = "";
        } else if (matched_user_name.length > 1) {
            msg_type = "";
            if (matched_user_name[1] === user_name) {
                whos = "mine";
            } else {
                whos = "yours";
            }
            if (matched_user_name[2] in stickers) {
                received_msg = matched_user_name[2];
                msg_type = "sticker";
            }
        } else {
            whos = "yours";
            msg_type = "";
        }

        appendMsg(received_msg, msg_type, whos);
        /*jq方式*/
        // $(mes).append($(aLi));
    };
    /*连接关闭时触发*/
    Socket.onclose = function () {
        appendMsg("连接已经关闭...(┬＿┬)", "", "yours");
        $(".send #text").attr("disabled", "disabled");
    };
} else {
    /*浏览器不支持 WebSocket*/
    alert("您的浏览器不支持 WebSocket!");
}
// 输入区域回车动作
$("#text").keypress(function (event) {
    if (event.code == "Enter" && event.ctrlKey) {
        // ctrl 回车换行
        send_msg.value += "\n";
    } else if (event.code == "Enter") {
        // 直接回车发送消息
        event.preventDefault();
        WebSocketSend();
    }
});
function WebSocketSend(content = "") {
    /*form 里的Dom元素(input select checkbox textarea radio)都是value*/
    //或者JQ中获取
    // var send_msg = $("#text").val();
    /*使用连接发送消息*/
    if (content.length == 0) {
        message = send_msg.value.replaceAll(" ", "");
    } else {
        message = content.replaceAll(" ", "");
    }
    if (message.length === 0) {
        appendMsg("不能发送空信息", "", "mine");
        cleanup();
        return;
    }
    Socket.send(message);
    cleanup();
}
