from rich.console import Console
from rich.table import Table

def account_details(account_name: str, repo_name: str, api_key: str, redacted: bool) -> None:
    table = Table(title=account_name)

    table.add_column("Account NAme", justify="right", style="cyan", no_wrap=True)
    table.add_column("Repo Name", style="magenta")

    if redacted:
        table.add_column("API Key", justify="left", style="green")

    if not redacted:
        table.add_column("API Key", justify="left", style="red")

    table.add_row(account_name, repo_name, api_key)

    console = Console()
    console.print(table)