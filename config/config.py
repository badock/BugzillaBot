from loader import load_config

BUGZILLA_USER = load_config().get("bugzilla").get("user")
BUGZILLA_PASSWORD = load_config().get("bugzilla").get("password")
