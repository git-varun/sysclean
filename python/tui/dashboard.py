"""Read-only dashboard for SysClean operations."""
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Static
from textual.containers import Grid, Vertical
import sqlite3
import os
import sys
import json

import pathlib

DB_PATH = pathlib.Path.home() / ".local/share/sysclean/sysclean.db"

class SysCleanDashboard(App):
    """A textual dashboard to observe SysClean state."""

    CSS = """
    Grid {
        grid-size: 2;
        grid-columns: 1fr 1fr;
        grid-rows: 1fr 1fr;
    }
    
    .panel {
        height: 100%;
        border: solid green;
        padding: 1;
    }
    
    DataTable {
        height: 100%;
    }
    
    #title {
        text-align: center;
        text-style: bold;
        padding: 1;
    }
    
    #storage_value {
        text-align: center;
        text-style: bold;
        color: cyan;
        padding: 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("SysClean Read-Only Dashboard", id="title")
        
        with Grid():
            with Vertical(classes="panel"):
                yield Static("Queue State (Recent)")
                yield DataTable(id="queue_table")
            with Vertical(classes="panel"):
                yield Static("Active Executions")
                yield DataTable(id="active_table")
            with Vertical(classes="panel"):
                yield Static("Rollback History")
                yield DataTable(id="rollback_table")
            with Vertical(classes="panel"):
                yield Static("Reclaimable Storage")
                yield Static("0.0 B", id="storage_value")
        
        yield Footer()

    def on_mount(self) -> None:
        queue_table = self.query_one("#queue_table", DataTable)
        queue_table.add_columns("ID", "Module", "Status", "Risk")
        
        active_table = self.query_one("#active_table", DataTable)
        active_table.add_columns("ID", "Module", "Status")
        
        rollback_table = self.query_one("#rollback_table", DataTable)
        rollback_table.add_columns("ID", "Module", "Type", "Date")
        
        self.update_tables()
        self.set_interval(2.0, self.update_tables)

    def format_bytes(self, size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:3.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"

    def update_tables(self) -> None:
        if not DB_PATH.exists():
            return
            
        try:
            # We connect securely in read-only mode if possible, but standard is fine
            conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
            cursor = conn.cursor()
            
            # Update Queue
            cursor.execute("SELECT operation_id, module, status, risk_level FROM queue ORDER BY id DESC LIMIT 20")
            rows = cursor.fetchall()
            queue_table = self.query_one("#queue_table", DataTable)
            queue_table.clear()
            for row in rows:
                queue_table.add_row(row[0][:8], row[1], row[2], row[3])
                
            # Update Active Executions
            cursor.execute("SELECT operation_id, module, status FROM queue WHERE status IN ('EXECUTING', 'VERIFYING') ORDER BY id DESC")
            active_rows = cursor.fetchall()
            active_table = self.query_one("#active_table", DataTable)
            active_table.clear()
            for row in active_rows:
                active_table.add_row(row[0][:8], row[1], row[2])
                
            # Update Rollbacks
            cursor.execute("SELECT rollback_id, module, rollback_type, created_at FROM rollback_registry ORDER BY id DESC LIMIT 20")
            rb_rows = cursor.fetchall()
            rollback_table = self.query_one("#rollback_table", DataTable)
            rollback_table.clear()
            for row in rb_rows:
                rollback_table.add_row(row[0][:8], row[1], row[2], row[3])
                
            # Reclaimable Storage (Aggregate estimated_bytes from PROPOSED, APPROVED, EXECUTING)
            cursor.execute("SELECT payload_json FROM queue WHERE status IN ('PROPOSED', 'APPROVED', 'EXECUTING')")
            payloads = cursor.fetchall()
            total_reclaimable = 0
            for (payload_str,) in payloads:
                if payload_str:
                    try:
                        data = json.loads(payload_str)
                        total_reclaimable += data.get("estimated_bytes", 0)
                    except json.JSONDecodeError:
                        pass
            
            storage_widget = self.query_one("#storage_value", Static)
            storage_widget.update(self.format_bytes(total_reclaimable))
                
            conn.close()
        except Exception as e:
            # Ignore read errors to avoid crashing dashboard
            pass

if __name__ == "__main__":
    app = SysCleanDashboard()
    app.run()
