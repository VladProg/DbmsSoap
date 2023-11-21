import spyne


TypeEnum = spyne.Enum('Char', 'Color', 'ColorInvl', 'Integer', 'Real', 'String', type_name='TypeEnum')


class Type(spyne.ComplexModel):
    type_enum = TypeEnum.customize(min_occurs=1, nillable=False)
    r1 = r2 = g1 = g2 = b1 = b2 = spyne.Integer32(min_occurs=0, max_value=255, nillable=False)
    to_str = spyne.String(min_occurs=0, nillable=False)

    def validate(self):
        if self.type_enum == TypeEnum.COLOR_INVL:
            if any(x is None for x in (self.r1, self.r2, self.g1, self.g2, self.b1, self.b2)):
                raise spyne.Fault(faultcode="Client", faultstring='ColorInvl type must have r1, r2, g1, g2, b1, b2 fields')
        else:
            if any(x is not None for x in (self.r1, self.r2, self.g1, self.g2, self.b1, self.b2)):
                raise spyne.Fault(faultcode="Client", faultstring='All types except ColorInvl must not have r1, r2, g1, g2, b1, b2 fields')


class Column(spyne.ComplexModel):
    name = spyne.String(min_occurs=1, nillable=False)
    type = Type.customize(min_occurs=1, nillable=False)


class Row(spyne.ComplexModel):
    id = spyne.Integer32(min_occurs=1, nillable=False)
    cells = spyne.Array(spyne.String(min_occurs=1, nillable=False), min_occurs=1, nillable=False)


class TableInfo(spyne.ComplexModel):
    id = spyne.Integer32(min_occurs=1, nillable=False)
    name = spyne.String(min_occurs=1, nillable=False)
    left_table_id = right_table_id = spyne.Integer32(min_occurs=0, nillable=False)


class Table(spyne.ComplexModel):
    id = spyne.Integer32(min_occurs=1, nillable=False)
    name = spyne.String(min_occurs=1, nillable=False)
    columns = spyne.Array(Column.customize(min_occurs=1, nillable=False), min_occurs=1, nillable=False)
    rows = spyne.Array(Row.customize(min_occurs=1, nillable=False), min_occurs=1, nillable=False)
    is_table_difference = spyne.Boolean(min_occurs=1, nillable=False)


class DatabaseInfo(spyne.ComplexModel):
    tables = table_differences = spyne.Array(TableInfo.customize(min_occurs=1, nillable=False), min_occurs=1, nillable=False)
