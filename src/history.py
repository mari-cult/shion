from typing import Optional

from pydantic import BaseModel
from google.genai.types import Content, File


class Entry(BaseModel):
    content: Content
    files: list[File]


class ChatHistory:
    def __init__(self, max_size: int):
        self._history: dict[int, list[Entry]] = dict()
        self._max_size = max_size

    def _trim(self, channel_id: int) -> Optional[Entry]:
        if channel_id not in self._history:
            return None

        if len(self._history[channel_id]) < self._max_size:
            return None

        return self._history[channel_id].pop(0)

    def put(self, channel_id: int, entry: Entry) -> Optional[Entry]:
        if channel_id not in self._history:
            self._history[channel_id] = list()

        trimmed_entry = self._trim(channel_id)
        self._history[channel_id].append(entry)
        return trimmed_entry

    def history(self, channel_id: int) -> list[Content]:
        if channel_id not in self._history:
            return list()

        return [entry.content for entry in self._history[channel_id]]
