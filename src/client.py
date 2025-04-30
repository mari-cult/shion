from discord import Client, Message, Intents
import google.genai as genai
from google.genai.types import Part

from .history import ChatHistory
from .settings import parse_settings


class Shion(Client):
    """
    Discord client that processes user messages and responds using
    Gemini API
    """

    def __init__(self, *, intents: Intents, **options):
        super().__init__(intents=intents, **options)
        self._settings = parse_settings()
        self._chat_history = ChatHistory(
            self._settings.DISCORD_HISTORY_MAX_LEN
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

        channel_id = message.channel.id
        self._chat_history.append(
            channel_id, "user", [Part(text=message.content)]
        )

        try:
            async with message.channel.typing():
                genai_client = genai.Client(
                    api_key=self._settings.GEMINI_TOKEN
                )
                chat = genai_client.chats.create(
                    model="gemini-2.0-flash",
                    history=self._chat_history.history(channel_id),
                )

                # Generate a response based on the message and history
                response = chat.send_message(message.content)

                # Add the bot's response to the history
                self._chat_history.append(
                    channel_id, "model", [Part(text=response.text)]
                )

                # Send the generated response back to the channel
                await message.channel.send(response.text)

        except Exception as e:
            print(f"An error occurred: {e}")
            await message.channel.send(
                "Sorry, I encountered an error while processing your request."
            )
