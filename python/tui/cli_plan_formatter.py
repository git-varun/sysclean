import sys
import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

def main():
    if len(sys.argv) < 2:
        return
        
    try:
        plan = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        return

    console = Console()
    module = plan.get("module", "unknown")
    estimated_bytes = plan.get("estimated_bytes", 0)
    mb_saved = estimated_bytes / (1024 * 1024)
    command = plan.get("command", "N/A")
    risk_level = plan.get("risk_level", "unknown")

    table = Table(show_header=False, box=None)
    table.add_column("Key", style="bold cyan")
    table.add_column("Value")
    
    table.add_row("Module", module)
    table.add_row("Risk Level", f"[bold {'red' if risk_level == 'aggressive' else 'yellow' if risk_level == 'balanced' else 'green'}]{risk_level}[/]")
    table.add_row("Estimated Savings", f"{mb_saved:.2f} MB")
    table.add_row("Execution Command", f"[dim]{command}[/dim]")
    
    panel = Panel(
        table,
        title=f"Plan generated for [bold magenta]{module}[/bold magenta]",
        border_style="blue",
        expand=False
    )
    
    console.print(panel)

if __name__ == "__main__":
    main()
