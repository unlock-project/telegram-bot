class InTunnelData:
    role: str
    companion_chat_id: int

    def __init__(self, role: str, companion_chat_id: int):
        self.role = role
        self.companion_chat_id = companion_chat_id