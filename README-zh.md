# FluffyProtect

Telegram group anti-spam for humans.


## 背景

“传统”Telegram反垃圾机器人让新成员点击一条通常直接发到其所在群组的消息。

但是这样机器人本身就成了最大的垃圾：在大型的，频繁有人加入的群组中，这些“加入”消息实际上冲走了聊天内容。

即使在私聊中完成了验证，逆天的体验和消息栏中的“命令”按钮实在是格格不入。

更重要的是，这些机器人大多不是完全自建的，这意味着你必须完全信任托管/维护者。

FluffyProtect是一个创新的解决方案：它自己不在群组内做任何事，而是依靠外部的验证码服务，比如Cloudflare的hCaptcha。

对于私人群组，当有人试图加入时，它会生成一个一次性的邀请链接。当那个人确实加入后，这个链接将被替换成另一个。其他机器人也不能请求邀请链接，因为CAPTCHA将阻止他们到达FluffyProtect。

FluffyProtect也是完全自建的，你同时控制着它和它所在的群组。


## 安装

Clone这个repo：

```
git clone https://github.com/noarchwastaken/FluffyProtect
```

### 依赖

- `python3` (tested on 3.9.1)
- `flask` (tested on 1.1.2)
- `requests` (tested on 2.25.1)
- 可选： `gunicorn` (tested on 20.0.4)

使用`pip`或系统自带的包管理器安装依赖。

当然，你还需要使用[@BotFather](https://t.me/BotFather)创建一个bot。

### 硬编码API密钥

为简单起见，API密钥是硬编码进FluffyProtect的。

在`fprotect.py`中，用你的API密钥替换`API_KEY`。


## 运行

为了测试这之前的操作，运行：

```
./fprotect.py
```

你应该能看见Flask监听着`127.0.0.1:5000`。

退出程序，继续下一步。

### 让FluffyProtect在你的群组工作

把bot邀请到你的群组中，然后设置成管理员。你可以关掉除"添加成员"以外的所有额外权限。

现在，发送一条提到了你机器人的消息。完成后，浏览：

```
https://api.telegram.org/bot<YOUR BOT API KEY>/getUpdates
```

你应该能看到你刚才发的消息，其中包含`chat`对象和`id`。`id`是群组聊天的ID，把它记下来。

### 反向代理

FluffyProtect**不**应该直接响应任何外部请求。

为了最大化安全性，你应该为它设置一个反向代理(如Nginx)，并有另一个反向代理CDN*连接着你之前的反向代理*，像Cloudflare的CAPTCHA。

关于Nginx和Cloudflare的设置，请参阅Nginx的内置示例，阅读Cloudflare的说明或在线寻求帮助。

在你的Nginx配置中，反向代理至少有两个URL：你的API密钥，和指向聊天ID的重定向URL。例如：

```
location / {
    proxy_pass http://127.0.0.1:8000/<YOUR GROUP CHAT ID>;
}

location /<YOUR BOT API KEY> {
    proxy_pass http://127.0.0.1:8000/<YOUR BOT API KEY>/;
}
```

如果你想让FluffyProtect在你的多个群组中工作，只需要重复[让FluffyProtect在你的群组工作](#让FluffyProtect在你的群组工作)步骤，并在Nginx的配置中添加相应的`location`区块。

在Cloudflare控制面板的"防火墙"选项卡中，创建与重定向URL相匹配的自定义规则。选择“JS质询”或是“质询 (Captcha)”取决于你的威胁种类。

你可能还想为Telegram的请求添加一个例外： 添加一个`ASN`匹配`62041`的防火墙规则，然后设置为“允许”。

这将防止Cloudflare质询Telegram的WebHook请求，并允许Telegram显示群组描述，好像你的群组是公开的一样。

### systemd服务，以及Gunicorn

当每一层的反向代理都设置完成后，你现在可以用Gunicorn运行FluffyProtect，以获得更好的性能：

```
$ gunicorn -w 1 fprotect:app
```

> 注意**只能运行一个进程**，否则FluffyProtect将返回无效的邀请链接。
你也可以创建一个systemd服务来自动启动，`fprotect.service`中包含了一个示例文件。

启动并运行FluffyProtect后，访问你的重定向URL，应该能看见刚才设置的CAPTCHA。在解决CAPTCHA之后，你应该会被重定向到你的Telegram群组。

在加入群组后，刚才使用的邀请链接会被新的链接取代，必须用上面的方法重新申请。
