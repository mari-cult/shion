import logging

from discord import Client, Message, Intents

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

    def __init__(self, *, intents: Intents, **options):
        super().__init__(intents=intents, **options)
        self._settings = parse_settings()
        self._gemini = GeminiService(
            self._settings.GEMINI_TOKEN,
            self._settings.GEMINI_MODEL,
            self._settings.DISCORD_HISTORY_MAX_LEN,
        )

    async def on_ready(self):
        """Logs when the bot is ready and connected to Discord."""
        print(f"{self.user.name} has connected to Discord!")
        print("Bot is ready!")

    async def on_message(self, message: Message):
        # Ignore messages from the bot itself
        if message.author == self.user:
            return

        if self.user not in message.mentions:
            return

        print(
            f"Received message in channel {message.channel.name}:"
            f" {message.content}"
        )

        try:
            async with message.channel.typing():
                answer = await self._gemini.process_message(self.user, message)

                # Send the generated response back to the channel
                await message.channel.send(answer)

        except Exception as e:
            logger.error(e, stack_info=True, exc_info=True)
            await message.channel.send(
                "Oops! Something went wrong just now... ( ᵔ ⩊ ᵔ )"
            )
