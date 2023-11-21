import spyne
import Models
import Messages
from spyne.application import Application
from spyne.protocol.soap import Soap11
from spyne.service import ServiceBase
from spyne.server.wsgi import WsgiApplication


databases = {}


def _get_full_database(dbName):
    if dbName not in databases:
        raise spyne.Fault(faultcode="Client", faultstring=f"Cannot find database '{dbName}'")
    return databases[dbName]


def _get_full_table(dbName, tableId):
    ids = Models.TableDifference.parse_id(tableId)
    if ids is not None:
        return _get_full_table_difference(dbName, ids[0], ids[1])
    database = _get_full_database(dbName)
    if tableId not in database.tables:
        raise spyne.Fault(faultcode="Client", faultstring=f"Database '{dbName}' doesn't contain table #{tableId}")
    return database.tables[tableId]


def _get_full_table_difference(dbName, leftTableId, rightTableId):
    leftTable = _get_full_table(dbName, leftTableId)
    rightTable = _get_full_table(dbName, rightTableId)
    difference = Models.TableDifference.create(leftTable, rightTable)
    difference.calculate()
    return difference


class DbmsSoapService(ServiceBase):

    @spyne.rpc(
        spyne.String(nillable=False, min_occurs=1)
    )
    def CreateDatabase(self, DbName):
        if DbName in databases:
            raise spyne.Fault(faultcode="Client", faultstring=f"Database '{DbName}' already exists")
        else:
            databases[DbName] = Models.Database()

    @spyne.rpc(
        spyne.String(nillable=False, min_occurs=1),
        _returns=Messages.DatabaseInfo.customize(nillable=False, min_occurs=1)
    )
    def GetDatabase(self, DbName):
        return _get_full_database(DbName).to_message_info()

    @spyne.rpc(
        spyne.String(nillable=False, min_occurs=1)
    )
    def DeleteDatabase(self, DbName):
        if DbName in databases:
            del databases[DbName]
        else:
            raise spyne.Fault(faultcode="Client", faultstring=f"Cannot find database '{DbName}'")

    @spyne.rpc(
        spyne.String(nillable=False, min_occurs=1),
        spyne.String(nillable=False, min_occurs=1),
        spyne.Array(Messages.Column.customize(nillable=False, min_occurs=1), nillable=False, min_occurs=1),
        _returns=spyne.Integer32
    )
    def AddTable(self, DbName, TableName, Columns):
        database = _get_full_database(DbName)
        columns = [Models.Column(column.name, Models.Types.Type.from_message(column.type)) for column in Columns]
        return database.add_table(TableName, columns).id

    @spyne.rpc(
        spyne.String(nillable=False, min_occurs=1),
        spyne.Integer32(nillable=False, min_occurs=1)
    )
    def RemoveTable(self, DbName, TableId):
        database = _get_full_database(DbName)
        database.remove_table(TableId)

    @spyne.rpc(
        spyne.String(nillable=False, min_occurs=1),
        spyne.Integer32(nillable=False, min_occurs=1),
        _returns=Messages.Table.customize(nillable=False, min_occurs=1)
    )
    def GetTable(self, DbName, TableId):
        return _get_full_table(DbName, TableId).to_message()

    @spyne.rpc(
        spyne.String(nillable=False, min_occurs=1),
        spyne.Integer32(nillable=False, min_occurs=1),
        spyne.Array(spyne.String(nillable=False, min_occurs=1), nillable=False, min_occurs=1),
        _returns=spyne.Integer32(nillable=False, min_occurs=1)
    )
    def AddRow(self, DbName, TableId, Cells):
        table = _get_full_table(DbName, TableId)
        if len(Cells) != len(table.columns):
            raise spyne.Fault(faultcode="Client", faultstring="Row length must be the same as number of columns")
        values = []
        try:
            for i in range(len(Cells)):
                values.append(table.columns[i].type.parse(Cells[i]))
            return table.add_row(values).id
        except Exception as e:
            raise spyne.Fault(faultcode="Client", faultstring=str(e))

    @spyne.rpc(
        spyne.String(nillable=False, min_occurs=1),
        spyne.Integer32(nillable=False, min_occurs=1),
        spyne.Integer32(nillable=False, min_occurs=1)
    )
    def RemoveRow(self, DbName, TableId, RowId):
        table = _get_full_table(DbName, TableId)
        try:
            table.remove_row(RowId)
        except Exception as e:
            raise spyne.Fault(faultcode="Client", faultstring=str(e))

    @spyne.rpc(
        spyne.String(nillable=False, min_occurs=1),
        spyne.Integer32(nillable=False, min_occurs=1),
        spyne.Integer32(nillable=False, min_occurs=1),
        spyne.String(nillable=False, min_occurs=1)
    )
    def ValidateCell(self, DbName, TableId, ColumnId, Value):
        table = _get_full_table(DbName, TableId)
        try:
            table.columns[ColumnId].type.parse(Value)
        except Exception as e:
            raise spyne.Fault(faultcode="Client", faultstring=str(e))

    @spyne.rpc(
        spyne.String(nillable=False, min_occurs=1),
        spyne.Integer32(nillable=False, min_occurs=1),
        spyne.Integer32(nillable=False, min_occurs=1),
        spyne.Integer32(nillable=False, min_occurs=1),
        spyne.String(nillable=False, min_occurs=1)
    )
    def UpdateCell(self, DbName, TableId, RowId, ColumnId, Value):
        table = _get_full_table(DbName, TableId)
        try:
            table.rows[RowId].cells[ColumnId] = table.columns[ColumnId].type.parse(Value)
        except Exception as e:
            raise spyne.Fault(faultcode="Client", faultstring=str(e))

    @spyne.rpc(
        spyne.String(nillable=False, min_occurs=1),
        spyne.Integer32(nillable=False, min_occurs=1),
        spyne.Integer32(nillable=False, min_occurs=1),
        _returns=Messages.Table.customize(nillable=False, min_occurs=1)
    )
    def GetTableDifference(self, DbName, LeftTableId, RightTableId):
        try:
            return _get_full_table_difference(DbName, LeftTableId, RightTableId).to_message()
        except Exception as e:
            raise spyne.Fault(faultcode="Client", faultstring=str(e))

    @spyne.rpc(
        spyne.String(nillable=False, min_occurs=1),
        spyne.Integer32(nillable=False, min_occurs=1),
        _returns=spyne.Boolean(nillable=False, min_occurs=1)
    )
    def TableExists(self, DbName, TableId):
        try:
            _get_full_table(DbName, TableId)
            return True
        except:
            return False


application = Application([DbmsSoapService],
                          tns='DbmsSoap',
                          in_protocol=Soap11(validator='lxml'),
                          out_protocol=Soap11())

if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    server = make_server('127.0.0.1', 8000, WsgiApplication(application))
    server.serve_forever()
