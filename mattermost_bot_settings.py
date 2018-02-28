from config.loader import load_config

SSL_VERIFY = True if load_config().get("mattermost").get("ssl_verify") is "yes" else False
BOT_URL = load_config().get("mattermost").get("url")
BOT_LOGIN = load_config().get("mattermost").get("login")
BOT_PASSWORD = load_config().get("mattermost").get("password")
BOT_TEAM = load_config().get("mattermost").get("team")

IGNORE_NOTIFIES = ['@channel', '@all', '@here']
