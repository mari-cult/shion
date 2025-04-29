import discord
import google.genai as genai
from google.genai.types import Part, Content
import os
from collections import deque

# --- Configuration ---
# Get your Discord bot token and Gemini API key from environment variables
# It's recommended to use environment variables for sensitive information
PROXY = os.getenv("https_proxy")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Set up intents - required for accessing message content
# Make sure to enable the "Message Content Intent" in your bot's settings on the Discord Developer Portal
intents = discord.Intents.default()
intents.message_content = True

# Initialize the bot with a command prefix and intents
client = discord.Client(intents=intents, proxy=PROXY)

# Dictionary to store conversation history for each channel
# Using deque with a maxlen to automatically remove old messages
# The key will be the channel ID, and the value will be a deque of messages
conversation_history = {}
HISTORY_SIZE = (
    10  # Number of messages to remember per channel (5 user + 5 bot)
)

# --- Bot Events ---


@client.event
async def on_ready():
    """Logs when the bot is ready and connected to Discord."""
    print(f"{client.user.name} has connected to Discord!")
    print("Bot is ready!")


@client.event
async def on_message(message):
    """Processes messages received by the bot."""
    # Ignore messages from the bot itself
    if message.author == client.user:
        return

    # Ignore messages that start with the command prefix, so commands are handled separately
    # if message.content.startswith(client.command_prefix):
    #     await client.process_commands(message)
    #     return

    # Get the conversation history for the channel, or create a new one if it doesn't exist
    channel_id = message.channel.id
    if channel_id not in conversation_history:
        # Initialize with a system instruction if desired, or leave empty
        # conversation_history[channel_id] = deque([{"role": "user", "parts": ["System: You are a helpful AI assistant."]}], maxlen=HISTORY_SIZE)
        conversation_history[channel_id] = deque(maxlen=HISTORY_SIZE)

    # Add the user's message to the history
    conversation_history[channel_id].append(
        Content(role="user", parts=[Part(text=message.content)])
    )

    print(
        f"Received message in channel {message.channel.name}: {message.content}"
    )
    # print(f"Current history for channel {channel_id}: {list(conversation_history[channel_id])}") # Optional: for debugging history

    try:
        # Show the "Bot is typing..." indicator
        async with message.channel.typing():
            # Create a GenerativeModel instance
            # You can specify a model like 'gemini-pro'
            genai_client = genai.Client(api_key=GEMINI_API_KEY)
            chat = genai_client.chats.create(
                model="gemini-2.0-flash",
                history=list(conversation_history[channel_id]),
            )

            # Generate a response based on the message and history
            response = chat.send_message(message.content)

            # Add the bot's response to the history
            conversation_history[channel_id].append(
                Content(role="model", parts=[Part(text=response.text)])
            )

            # Send the generated response back to the channel
            await message.channel.send(response.text)

    except Exception as e:
        print(f"An error occurred: {e}")
        await message.channel.send(
            "Sorry, I encountered an error while processing your request."
        )
        # Remove the last user message if an error occurred, to avoid adding it without a bot response
        if (
            conversation_history[channel_id]
            and conversation_history[channel_id][-1].role == "user"
        ):
            conversation_history[channel_id].pop()

    # Process commands after handling the message if it wasn't a command
    # (This line is technically redundant because of the check at the beginning of the function,
    # but it's good practice if you were to remove that check)
    # await bot.process_commands(message)


# --- Run the bot ---
# Ensure your environment variables DISCORD_TOKEN and GEMINI_API_KEY are set
if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("Error: DISCORD_TOKEN environment variable not set.")
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY environment variable not set.")
    if DISCORD_TOKEN and GEMINI_API_KEY:
        client.run(DISCORD_TOKEN)
    else:
        print(
            "Please set both DISCORD_TOKEN and GEMINI_API_KEY environment variables."
        )
