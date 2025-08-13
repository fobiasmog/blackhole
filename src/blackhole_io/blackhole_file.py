### BlackholeFile
# Object of this class represents the information about uploaded/downloaded file

class BlackholeFile:
    def __init__(self):
        self.filename: str = ""
        self.content_type: str = ""
        self.size: int = 0

    def blob(self) -> bytes:
        return b""


