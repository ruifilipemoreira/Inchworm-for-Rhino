MAX_ENTRIES = 5


class SessionHistory:

    def __init__(self):
        self._entries = []

    def add(self, entry):
        if entry in self._entries:
            self._entries.remove(entry)
        self._entries.insert(0, entry)
        if len(self._entries) > MAX_ENTRIES:
            self._entries.pop()

    @property
    def entries(self):
        return list(self._entries)