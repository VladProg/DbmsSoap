using System;
using System.Collections.Generic;
using System.Windows.Forms;

namespace DbmsSoapClient
{
    public partial class FormTable : Form
    {
        private readonly DbmsSoapServiceReference.ApplicationClient client;
        private readonly string dbName;
        public readonly DbmsSoapServiceReference.TableInfo TableInfo;

        public FormTable(DbmsSoapServiceReference.ApplicationClient client, string dbName, DbmsSoapServiceReference.TableInfo tableInfo)
        {
            InitializeComponent();
            this.client = client;
            this.dbName = dbName;
            TableInfo = tableInfo;
            Text = TableInfo.name;
            RefreshRows();
            if (TableInfo.left_table_idSpecified)
            {
                dataGridView.ReadOnly = true;
                dataGridView.AllowUserToDeleteRows = false;
                dataGridView.AllowUserToAddRows = false;
            }
        }

        public void RefreshRows()
        {
            dataGridView.Rows.Clear();
            dataGridView.Columns.Clear();
            var table = client.GetTable(new() { DbName=dbName, TableId=TableInfo.id }).GetTableResult;
            foreach (var column in table.columns)
                dataGridView.Columns.Add("", column.name + "\n" + column.type.to_str);
            foreach (DataGridViewColumn column in dataGridView.Columns)
                column.SortMode = DataGridViewColumnSortMode.NotSortable;
            foreach (var row in table.rows)
                dataGridView.Rows[dataGridView.Rows.Add(row.cells.ToArray())].Tag = row.id;
        }

        private void dataGridView_CellValidating(object sender, DataGridViewCellValidatingEventArgs e)
        {
            if (e.RowIndex == dataGridView.NewRowIndex || !dataGridView.Rows[e.RowIndex].Cells[e.ColumnIndex].IsInEditMode)
                return;
            try
            {
                client.ValidateCell(new() { DbName=dbName, TableId=TableInfo.id, ColumnId=e.ColumnIndex, Value=e.FormattedValue.ToString() });
            }
            catch (Exception ex)
            {
                e.Cancel = true;
                MessageBox.Show(ex.Message, "Invalid value", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void dataGridView_RowValidating(object sender, DataGridViewCellCancelEventArgs e)
        {
            if (e.RowIndex == dataGridView.NewRowIndex)
                return;
            try
            {
                for (int i = 0; i < dataGridView.Columns.Count; i++)
                    client.ValidateCell(new() {DbName= dbName, TableId=TableInfo.id, ColumnId=i, Value=dataGridView.Rows[e.RowIndex].Cells[i].Value?.ToString() ?? "" });
            }
            catch
            {
                e.Cancel = true;
                MessageBox.Show("Fill all cells to create row (or remove the entire row)", "Cannot create row", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void dataGridView_CellValueChanged(object sender, DataGridViewCellEventArgs e)
        {
            DataGridViewRow dgvRow = dataGridView.Rows[e.RowIndex];
            int? rowId = dgvRow.Tag as int?;
            if (rowId == null)
            {
                try
                {
                    string[] cells = new string[dataGridView.Columns.Count];
                    for (int i = 0; i < dataGridView.Columns.Count; i++)
                        cells[i] = dgvRow.Cells[i].Value?.ToString() ?? "";
                    dgvRow.Tag = client.AddRow(new() { DbName = dbName, TableId = TableInfo.id, Cells = cells }).AddRowResult;
                    if (Parent.FindForm() is FormDatabase parentForm)
                        parentForm.RefreshDifferences(TableInfo.id);
                }
                catch { }
            }
            else
            {
                DataGridViewCell dgvCell = dgvRow.Cells[e.ColumnIndex];
                client.UpdateCell(new() { DbName=dbName, TableId=TableInfo.id, RowId=rowId.Value, ColumnId=e.ColumnIndex, Value=dgvCell.Value?.ToString() ?? "" });
                if (Parent.FindForm() is FormDatabase parentForm)
                    parentForm.RefreshDifferences(TableInfo.id);
            }
        }

        private void dataGridView_UserDeletedRow(object sender, DataGridViewRowEventArgs e)
        {
            int? dbRow = e.Row.Tag as int?;
            if (dbRow == null)
                return;
            client.RemoveRow(new() { DbName=dbName, TableId=TableInfo.id, RowId=dbRow.Value });
            if (Parent.FindForm() is FormDatabase parentForm)
                parentForm.RefreshDifferences(TableInfo.id);
        }

        private void FormTable_FormClosed(object sender, FormClosedEventArgs e)
        {
            if (Parent.FindForm() is FormDatabase parentForm)
                parentForm.ListTables(TableInfo.id);
        }
    }
}
