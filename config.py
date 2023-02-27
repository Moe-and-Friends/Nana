
from dynaconf import Dynaconf, Validator

DISCORD_TOKEN = "DISCORD_TOKEN"
RSS_OBSERVED_CHANNELS = "RSS_OBSERVED_CHANNELS"
RSS_WEBHOOKS = "RSS_WEBHOOKS"

settings = Dynaconf(
    environments=True,
    envvar_prefix="NANA",
    load_dotenv=True,
    redis_enabled=False,
    settings_files=['settings.toml',
                    '.secrets.toml',
                    'configs/settings.toml',
                    'configs/.secrets.toml'],
    validators=[
        Validator(DISCORD_TOKEN, is_type_of=str, must_exist=True),
        Validator(RSS_OBSERVED_CHANNELS, is_type_of=list, default=[]),
        Validator(RSS_WEBHOOKS, is_type_of=list, default=[]),
    ],
    vault_enabled=False,
)