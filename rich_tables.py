from rich.console import Console
from rich.table import Table


def account_details(
    account_name: str, repo_name: str, api_key: str, redacted: bool
) -> None:
    table = Table(title=account_name)

    table.add_column("Account Name", justify="right", style="cyan", no_wrap=True)
    table.add_column("Repo Name", style="magenta")

    if redacted:
        table.add_column("API Key", justify="left", style="green")

    if not redacted:
        table.add_column("API Key", justify="left", style="red")

    table.add_row(account_name, repo_name, api_key)

    console = Console()
    console.print(table)


def deployment_details(
    account_name: str, deploy_id: str, workflow_id: str, status: str
) -> None:
    table = Table(title=account_name)

    table.add_column("Account Name", justify="right", style="cyan", no_wrap=True)
    table.add_column("Deployment ID", style="white")
    table.add_column("Workflow ID", style="magenta")
    if "fail" in status.lower() or "cancel" in status.lower():
        table.add_column("Status", style="red")
    else:
        table.add_column("Status", style="green")

    table.add_row(account_name, str(deploy_id), str(workflow_id), status)

    console = Console()
    console.print(table)
