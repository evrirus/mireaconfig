import base64

from VFSNode import VFSNode


class VFSFile(VFSNode):
    def __init__(self, name: str, content_b64: str = "", owner: str = "root"):
        super().__init__(name, owner)
        self.content_b64 = content_b64  # base64 encoded content

    def is_file(self) -> bool:
        return True

    def read_bytes(self) -> bytes:
        if not self.content_b64:
            return b""
        try:
            return base64.b64decode(self.content_b64)
        except Exception as e:
            raise ValueError(f"Ошибка декодирования содержимого файла '{self.name}': {e}")

    def read_text(self, encoding="utf-8", errors="replace") -> str:
        return self.read_bytes().decode(encoding, errors)