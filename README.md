# FluffyProtect

Telegram group anti-spam for humans.

[中文说明](/README-zh.md)


## Background

"Traditional" Telegram anti-spam bots lets new members click on a message, usually sent directly in the group that it's operating in.

But then the bot itself becomes the biggest spam: in large groups with frequent joins, those "join" messages are literally flushing actual messages away.

Even with the verification done in private chat, the counter-intuitive experience and the "command" button in the message bar is just kind of out-of-place.

Most importantly, those bots are mostly not fully self-hosted, meaning that you must trust the person hosting the bot.

FluffyProtect is a creative solution for this problem: It does nothing in the group itself, but rather relies on external captcha services, like Cloudflare's hCaptcha.

With a private group, it generates a one-time invite link when someone attempts to join. This link is then replaced by another one when the person actually joins. Bots can't even request an invite link because the CAPTCHA will block them from reaching FluffyProtect.

FluffyProtect is also completely self-hosted, with you controlling the groups that it works in.


## Installation

Clone this repository:

```
$ git clone https://github.com/noarchwastaken/FluffyProtect
```

### Dependencies

- `python3` (tested on 3.9.1)
- `flask` (tested on 1.1.2)
- `requests` (tested on 2.25.1)
- Optional: `gunicorn` (tested on 20.0.4)

You can install the dependencies using `pip` or your system package manager.

Of course, you need to create a bot using [@BotFather](https://t.me/BotFather). Write down the API key that @BotFather gave you.


## Running

To test that everything works up to this point, run:

```
$ FPROTECT_API_KEY=<YOUR BOT API KEY> ./fprotect.py
```

You should see Flask listening on `127.0.0.1:5000`.

Note that you have to pass your bot API key using an environment variable, like the command above.

Quit the program, and let's set more things up.

### Making FluffyProtect work for your group

Invite the bot to your group. Make the bot administrator; you can turn off all extra permissions other than "Add members".

Now send a message mentioning your bot. After doing so, browse:

```
https://api.telegram.org/bot<YOUR BOT API KEY>/getUpdates
```

You should see the message that you just sent, with a `chat` object and `id` key in it. The `id` is the chat ID of the group. Write this down.

### Reverse proxy

FluffyProtect should **not** directly respond to any external requests.

For maximum security, you should set up a reverse proxy (e.g. Nginx) for it, and have yet another reverse proxy CDN *connecting to your previous reverse proxy* like Cloudflare for CAPTCHA.

For setting up Nginx and Cloudflare, please see Nginx's built-in examples, seek online help or instructions from Cloudflare.

In your Nginx configuration, you should have at least two URLs on reverse proxy: your API key, and your redirection URL pointing to the chat ID. For example:

```
location / {
    proxy_pass http://127.0.0.1:8000/<YOUR GROUP CHAT ID>;
}

location /<YOUR BOT API KEY> {
    proxy_pass http://127.0.0.1:8000/<YOUR BOT API KEY>/;
}
```

If you want FluffyProtect to work in multiple groups of yours, just repeat [Making FluffyProtect work for your group](#making-fluffyprotect-work-for-your-group) and add corresponding `location` blocks in your Nginx configuration.

In the "Firewall" tab in Cloudflare control panel, create custom firewall rules that matches the URL of redirection. Make it always "JS Challenge" or "Challenge" depending on your threat model.

You might also want to add an exception for Telegram's request: add a firewall IP rule matching `AS62041`, and set to "Allow".

This will prevent Cloudflare from challenging Telegram WebHook requests, and allow Telegram to show description of your group as if your group is public.

### systemd service, and Gunicorn

With every layer of reverse proxy set-up, you can now run FluffyProtect with Gunicorn for multi-processing and better performance:

```
$ FPROTECT_API_KEY=<YOUR BOT API KEY> gunicorn -w 4 fprotect:app
```

You can create a systemd service for auto-starting. An example systemd service file is included in the above `fprotect.service`.

With FluffyProtect up and running, browse your redirection URL. You should see the CAPTCHA that you just set; after solving the CAPTCHA, you should be redirected to your Telegram Group.

After joining the group, the invite link that you just used is replaced by a new one, which must be requested in the same way above.
