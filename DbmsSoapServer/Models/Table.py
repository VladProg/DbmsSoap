import spyne

from Models.Row import Row
import Messages


class Table:
    def __init__(self, id, name, columns):
        self.id = id
        self.name = name
        self.columns = columns
        self.rows = {}
        self._next_id = 0

    def add_row(self, cells):
        if len(cells) != len(self.columns):
            raise spyne.Fault(faultcode="Client", faultstring="Row length must be the same as number of columns")
        for i in range(len(self.columns)):
            if cells[i].type != self.columns[i].type:
                raise spyne.Fault(faultcode="Client", faultstring="Cell type doesn't match corresponding column type")
        row = Row(self._next_id, cells)
        self.rows[self._next_id] = row
        self._next_id += 1
        return row

    def remove_row(self, id):
        if id in self.rows:
            del self.rows[id]

    def contains_row(self, row):
        return any(row == value for value in self.rows.values())

    def clear_rows(self):
        self.rows.clear()

    def to_message_info(self):
        return Messages.TableInfo(id=self.id, name=self.name)

    def to_message(self):
        return Messages.Table(
            id=self.id,
            name=self.name,
            columns=[column.to_message() for column in self.columns],
            rows=[value.to_message() for key, value in self.rows.items()],
            is_table_difference=False
        )
