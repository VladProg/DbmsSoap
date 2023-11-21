import Messages


class Row:
    def __init__(self, id, cells):
        self.id = id
        self.cells = cells

    def __eq__(self, other):
        if not isinstance(other, Row):
            return False
        return self.cells == other.cells

    def to_message(self):
        return Messages.Row(id=self.id, cells=[str(cell) for cell in self.cells])
