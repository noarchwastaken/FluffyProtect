# FluffyProtect

真正不打扰你的 Telegram 群验证。


## 背景

“传统” Telegram 反垃圾机器人让新成员点击一条通常直接发到其所在群组的消息。

但是这样机器人本身就成了最大的垃圾：在大型的，频繁有人加入的群组中，这些“加入”消息实际上冲走了聊天内容。

即使在私聊中完成了验证，逆天的体验和消息栏中的“命令”按钮实在是格格不入。

更重要的是，这些机器人大多不是完全自建的，这意味着你必须完全信任托管/维护者。

FluffyProtect 是一个创新的解决方案：它自己不在群组内做任何事，而是依靠外部的验证码服务，比如 Cloudflare 的 hCaptcha.

对于私人群组，当有人试图加入时，它会生成一个一次性的邀请链接。当那个人确实加入后，这个链接将被替换成另一个。并且，验证码能将爬虫和骚扰者挡在门外。

FluffyProtect 也是完全自建的，你同时控制着它和它所在的群组。


## 安装

克隆这个仓库：

```
git clone https://github.com/noarchwastaken/FluffyProtect
```

### 依赖

- `python3` (tested on 3.9.1)
- `flask` (tested on 1.1.2)
- `requests` (tested on 2.25.1)
- 可选： `gunicorn` (tested on 20.0.4)

使用 `pip` 或系统自带的包管理器安装依赖。

当然，你还需要使用 [@BotFather](https://t.me/BotFather) 创建一个bot.


## 运行

为了测试这之前的操作，运行：

```
$ FPROTECT_API_KEY=<你的 BOT API KEY> ./fprotect.py
```

你应该能看见 Flask 监听着`127.0.0.1:5000`.

退出程序，继续下一步。

### 将 FluffyProtect 部署到你的群

把 bot 邀请到你的群组中，然后设置成管理员。你可以关掉除"添加成员"以外的所有额外权限。

现在，发一条 `@` 你 bot 的消息。完成后，浏览：

```
https://api.telegram.org/bot<你的 bot API 密钥>/getUpdates
```

在返回的 JSON 文本中，你应该能看到你刚才发的消息，其中包含 `chat` 对象和 `id`. 记下 `id`, 我们之后会用到。

### 反向代理

FluffyProtect **不应该**直接响应任何外部请求。

为了最大化安全性，你应该为它设置一个反向代理（如 Nginx），并有另一个反向代理 CDN *连接着你之前的反向代理*，例如开启了验证码的 Cloudflare。

关于 Nginx 和 Cloudflare 的设置，请参阅 Nginx 的内置示例，阅读 Cloudflare 的文档或上网搜索。

在你的 Nginx 配置中，你需要将至少两个地址设置为反向代理：

```
location / {
    proxy_pass http://127.0.0.1:8000/<你的群组 ID>;
}

location /<YOUR BOT API KEY> {
    proxy_pass http://127.0.0.1:8000/<你的 bot API 密钥>/;
}
```

如果你想让 FluffyProtect 保护多个群组，只需要重复[将 FluffyProtect 部署到你的群](#将-FluffyProtect-部署到你的群)步骤，并在 Nginx 配置中添加相应的 `location` 区块。

在 Cloudflare 控制面板的"防火墙"选项卡中，创建与重定向 URL 相匹配的自定义规则。根据你的威胁模型，选择“JS质询”或是“质询 (Captcha)”。

你可能还需要将 Telegram 的 WebHook 请求加入白名单： 添加一个 `ASN` 匹配 `62041` 的防火墙规则，然后设置为“允许”。

这将防止 Cloudflare 质询 Telegram 的 WebHook 请求，并允许 Telegram 像公开群组一样显示群组描述。

### systemd 服务，以及 Gunicorn

当每一层的反向代理都设置完成后，为了多进程和更好的性能，你现在可以用 Gunicorn 运行 FluffyProtect:

```
$ FPROTECT_API_KEY=<你的 BOT API KEY> gunicorn -w 4 fprotect:app
```

你可以参考 `fprotect.service` 创建一个 systemd 服务来自动启动。

启动并运行 FluffyProtect 后，访问你的重定向 URL, 应该能看见刚才设置的验证码。在输入验证码之后，你应该会被重定向到你的 Telegram 群组。

在加入群组后，刚才使用的邀请链接会被新的链接取代，必须用上面的方法重新申请。
