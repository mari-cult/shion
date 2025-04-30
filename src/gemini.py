from typing import Optional
from io import BytesIO

from google.genai import Client
from google.genai.types import (
    File,
    UploadFileConfig,
    Part,
    Content,
    GenerateContentConfig,
)

from discord import Message, User

from .history import ChatHistory, Entry


def assemble_message(
    user_id: int,
    user_name: str,
    text: Optional[str],
    files: list[File],
) -> list[Part]:
    parts: list[Part] = [
        Part.from_text(text=f"user(name={user_name}, id={user_id})"),
    ]
    if text:
        parts.append(Part.from_text(text=text))
    return parts + [
        Part.from_uri(file_uri=file.uri, mime_type=file.mime_type)
        for file in files
    ]


class GeminiService:
    def __init__(self, token: str, model: str, prompt: str, chat_max_len: int):
        self._model = model
        self._prompt = prompt
        self._gemini = Client(api_key=token)
        self._chat_history = ChatHistory(chat_max_len)

    async def _generate_response(
        self, channel_id: int, msg: list[Part]
    ) -> str:
        chat = self._gemini.aio.chats.create(
            model=self._model,
            history=self._chat_history.history(channel_id),
        )
        response = await chat.send_message(
            msg, GenerateContentConfig(system_instruction=self._prompt)
        )
        return response.text

    async def _record_message(
        self, channel_id: int, role: str, parts: list[Part], files: list[File]
    ):
        content = Content(role=role, parts=parts)
        entry = Entry(content=content, files=files)
        trimmed = self._chat_history.put(channel_id, entry)
        if trimmed:
            for file in trimmed.files:
                await self._gemini.aio.files.delete(name=file.name)

    async def _process_message(
        self, msg: Message
    ) -> tuple[list[Part], list[File]]:
        files: list[File] = list()
        for attachment in msg.attachments:
            data = await attachment.read()
            data_io = BytesIO(data)
            file = await self._gemini.aio.files.upload(
                file=data_io,
                config=UploadFileConfig(
                    display_name=attachment.filename,
                    name=str(attachment.id),
                    mime_type=attachment.content_type,
                ),
            )
            files.append(file)
        parts = assemble_message(
            msg.author.id, msg.author.display_name, msg.content, files
        )
        return parts, files

    async def push_message(self, msg: Message):
        parts, files = await self._process_message(msg)
        await self._record_message(msg.channel.id, "user", parts, files)

    async def send_message(self, user: User, msg: Message) -> str:
        user_parts, user_files = await self._process_message(msg)
        answer = await self._generate_response(msg.channel.id, user_parts)
        model_parts = assemble_message(user.id, user.display_name, answer, [])
        await self._record_message(
            msg.channel.id, "user", user_parts, user_files
        )
        await self._record_message(msg.channel.id, "model", model_parts, [])
        return answer
