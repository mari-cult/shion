from discord import Intents

from .client import Shion
from .settings import parse_settings

intents = Intents.default()
intents.message_content = True

settings = parse_settings()
client = Shion(intents=intents, proxy=settings.https_proxy)

if __name__ == "__main__":
    client.run(settings.DISCORD_TOKEN)
