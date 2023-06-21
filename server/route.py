class Route:
    method: str
    path: str
    func: callable

    def __init__(self, method: str, path: str, func: callable):
        self.method = method
        self.path = path
        self.func = func