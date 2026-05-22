"""Read-only dashboard for SysClean operations."""
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Static
from textual.containers import Horizontal, Vertical
from sqlalchemy.orm import Session
import sqlite3
import os
import sys

# Ensure python/ is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from queue.db import DB_PATH
from queue.models import QueueTask, RollbackRegistry

class SysCleanDashboard(App):
    """A textual dashboard to observe SysClean state."""

    CSS = """
    DataTable {
        height: 100%;
        border: solid green;
    }
    #title {
        text-align: center;
        text-style: bold;
        padding: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("SysClean Read-Only Dashboard", id="title")
        
        with Horizontal():
            with Vertical():
                yield Static("Queue State")
                yield DataTable(id="queue_table")
            with Vertical():
                yield Static("Rollback History")
                yield DataTable(id="rollback_table")
        
        yield Footer()

    def on_mount(self) -> None:
        queue_table = self.query_one("#queue_table", DataTable)
        queue_table.add_columns("ID", "Module", "Status", "Risk")
        
        rollback_table = self.query_one("#rollback_table", DataTable)
        rollback_table.add_columns("ID", "Module", "Type", "Date")
        
        self.update_tables()
        self.set_interval(2.0, self.update_tables)

    def update_tables(self) -> None:
        if not DB_PATH.exists():
            return
            
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Update Queue
            cursor.execute("SELECT operation_id, module, status, risk_level FROM queue ORDER BY id DESC LIMIT 20")
            rows = cursor.fetchall()
            
            queue_table = self.query_one("#queue_table", DataTable)
            queue_table.clear()
            for row in rows:
                queue_table.add_row(row[0][:8], row[1], row[2], row[3])
                
            # Update Rollbacks
            cursor.execute("SELECT rollback_id, module, rollback_type, created_at FROM rollback_registry ORDER BY id DESC LIMIT 20")
            rb_rows = cursor.fetchall()
            
            rollback_table = self.query_one("#rollback_table", DataTable)
            rollback_table.clear()
            for row in rb_rows:
                rollback_table.add_row(row[0][:8], row[1], row[2], row[3])
                
            conn.close()
        except Exception as e:
            pass

if __name__ == "__main__":
    app = SysCleanDashboard()
    app.run()
