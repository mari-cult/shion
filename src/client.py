import logging
from io import StringIO
from typing import Any

from discord import Client, Message, Intents, MessageType, File

from .settings import parse_settings
from .gemini import GeminiService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Get a logger for the current module (good practice)
logger = logging.getLogger(__name__)


class Shion(Client):
    """
    Discord client that processes user messages and responds using
    Gemini API
    """

    def __init__(self):
        self._settings = parse_settings()

        intents = Intents.default()
        intents.message_content = True
        options: dict[str, Any] = dict()
        if self._settings.https_proxy:
            options["proxy"] = self._settings.https_proxy
        print(options)
        super().__init__(intents=intents, **options)

        self._gemini = GeminiService(
            self._settings.GEMINI_TOKEN,
            self._settings.GEMINI_MODEL,
            self._settings.GEMINI_PROMPT,
            self._settings.DISCORD_HISTORY_MAX_LEN,
        )

    def run(self):
        super().run(self._settings.DISCORD_TOKEN)

    async def on_ready(self):
        """Logs when the bot is ready and connected to Discord."""
        print(f"{self.user.name} has connected to Discord!")
        print("Bot is ready!")

    async def on_message(self, message: Message):
        if message.type not in [MessageType.default, MessageType.reply]:
            return

        # Ignore messages from the bot itself
        if message.author == self.user:
            return

        print(
            f"Received message in channel {message.channel.name}:"
            f" {message.content}"
        )

        if self.user not in message.mentions:
            self._gemini.push_message(message)
            return

        try:
            async with message.channel.typing():
                answer = await self._gemini.send_message(self.user, message)

                # Send the generated response back to the channel
                if len(answer) < 2000:
                    await message.channel.send(answer)
                else:
                    file = File(StringIO(answer), filename="message.txt")
                    await message.channel.send(file=file)

        except Exception as e:
            logger.error(e, stack_info=True, exc_info=True)
            await message.channel.send(
                "Oops! Something went wrong just now... ( ᵔ ⩊ ᵔ )\n"
                f"```\n{e}\n```"
            )
