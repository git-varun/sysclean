import sys
import os
from queue_engine.db import SessionLocal
from queue_engine.models import QueueTask
from rich.console import Console
from rich.table import Table

def main():
    console = Console()
    db = SessionLocal()
    try:
        tasks = db.query(QueueTask).order_by(QueueTask.id.desc()).limit(20).all()
        if not tasks:
            console.print("[bold yellow]No active queue tasks found.[/bold yellow]")
            return

        table = Table(title="SysClean Queue State", show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=6)
        table.add_column("Module", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Risk", style="yellow")
        table.add_column("Updated At", justify="right")

        for t in tasks:
            status_color = "green" if t.status == "COMPLETED" else "yellow" if t.status in ("PROPOSED", "APPROVED") else "red" if t.status == "FAILED" else "blue"
            table.add_row(
                str(t.id),
                t.module,
                f"[{status_color}]{t.status}[/{status_color}]",
                t.risk_level,
                t.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            )

        console.print(table)
    finally:
        db.close()

if __name__ == "__main__":
    main()
