from collections import deque

from google.genai.types import Content, Part


class ChatHistory:
    def __init__(self, max_size: int):
        self._history: dict[int, deque[Content]] = dict()
        self._max_size = max_size

    def append(self, chat_id: int, role: str, parts: list[Part]):
        if chat_id not in self._history:
            self._history[chat_id] = deque([], maxlen=self._max_size)

        self._history[chat_id].append(Content(role=role, parts=parts))

    def history(self, chat_id: int) -> list[Content]:
        return list(self._history[chat_id])
