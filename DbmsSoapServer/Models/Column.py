import Messages


class Column:
    def __init__(self, name: str, type):
        self.name = name
        self.type = type

    def to_message(self):
        return Messages.Column(name=self.name, type=self.type.to_message())
