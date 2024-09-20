import random
import string
from getpass import getpass
from pathlib import Path

import cmd2
from cmd2 import Cmd2ArgumentParser, with_argparser
from loguru import logger
from pyfiglet import Figlet
from rich import print
from tinydb import Query, TinyDB

import encrypt
from account import (
    delete_account,
    deployment_info,
    list_accounts,
    list_deployments,
    new_account,
    view_account,
)
from build import main as build
from githubmesh import Workflow


class AccountApp(cmd2.Cmd):
    CUSTOM_CATEGORY = "Deployment Manager"

    def __init__(self, db: TinyDB, passphrase: str, account_name: str):
        super().__init__()
        # Show this as the prompt when asking for input
        self.prompt = f"⭐⭐ {account_name}: "
        self.db = db
        self.passphrase = passphrase
        self.account_name = account_name
        table = self.db.table("account_details")
        account = Query()
        details = table.get(account.account_name == self.account_name)

        self.repo = details.get("repo_name")
        self.key = encrypt.decrypt_string(self.passphrase, details.get("api_key"))

        self.wf = Workflow(self.key, self.account_name, self.repo)
        # Set the default category name
        self.default_category = "Built-in Commands"

    argparser = Cmd2ArgumentParser(
        description="""
        Deploy a new runner. A deployment ID will be assigned and all deployment
        details will be stored in the database.
        """
    )

    @with_argparser(argparser)
    @cmd2.with_category(CUSTOM_CATEGORY)
    def do_deploy(self, arg):
        build_id = "".join(
            random.choice(string.ascii_lowercase + string.digits) for _ in range(8)
        )
        try:
            build(self.wf, self.account_name, self.db, build_id)
            print("Deployment complete: ✅")
        except Exception as e:
            logger.error(e)
            print("Deployment failed: ❌")

    argparser = Cmd2ArgumentParser(description="list user deployments")
    argparser.add_argument(
        "--id",
        type=str,
        help="provide deploy ID to see all details",
        required=False,
    )
    argparser.add_argument(
        "--config",
        help="view wireguard config",
        required=False,
        action="store_true",
    )

    @with_argparser(argparser)
    @cmd2.with_category(CUSTOM_CATEGORY)
    def do_info(self, arg):
        if arg.config and not arg.id:
            print("Error: --id is required when --config is provided.")
            return
        if arg.id and arg.config:
            deployment_info(self.account_name, arg.id, arg.config, self.wf)

        if arg.id and not arg.config:
            deployment_info(self.account_name, arg.id, arg.config, self.wf)

        if not arg.id and not arg.config:
            list_deployments(self.account_name)

    argparser = Cmd2ArgumentParser(description="teardown deployment")
    argparser.add_argument(
        "workflow_id", help="provide workflow ID from deployment details"
    )

    @with_argparser(argparser)
    @cmd2.with_category(CUSTOM_CATEGORY)
    def do_teardown(self, arg):
        workflow_id = arg.workflow_id
        self.wf.cancel_workflow(workflow_id)


class HomepageApp(cmd2.Cmd):
    CUSTOM_CATEGORY = "Account Management"
    DEPLOYMENTS = "Deployment Management"

    def __init__(self):
        super().__init__()
        # Prints an intro banner once upon application startup
        f = Figlet()
        self.intro = f.renderText("Cloud Git")

        # Show this as the prompt when asking for input
        self.prompt = "👽 cloudgit: "

        # Set the default category name
        self.default_category = "Built-in Commands"

        home = Path.home()
        file = f"{home}/.cloudgit/cg.db"
        obj = Path(file)
        self.db = None
        self.sport_item_strs = ["Bat", "Basket", "Basketball", "Football", "Space Ball"]

        if not obj.exists():
            try:
                db_dir = Path(f"{home}/.cloudgit")
                db_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger(e)

            print("Choose a passphrase...dont forget it\n")
            attempt1 = getpass("Passphrase: ")
            attempt2 = getpass("Confirm passphrase: ")
            if attempt1 != attempt2:
                print("Entries did not match. Try again")
                quit()

            print("Initializing database...\n")
            self.db = TinyDB(file)
            self.passphrase = attempt2

            check_value = encrypt.encrypt_string(self.passphrase, "PRESENT")
            new_table = self.db.table("key_check")
            new_table.insert({"check_key": check_value})

        else:
            self.passphrase = getpass("Enter passphrase: ")
            print("Verifying passphrase...")

            self.db = TinyDB(file)
            table = self.db.table("key_check")
            details = table.all()
            value = details[0].get("check_key")
            try:
                encrypt.decrypt_string(self.passphrase, value)
                pass
            except Exception:
                print("Passphrase incorrect")
                quit()

    argparser = Cmd2ArgumentParser(description="add account details")

    @with_argparser(argparser)
    @cmd2.with_category(CUSTOM_CATEGORY)
    def do_new_account(self, _):
        new_account(self.passphrase)

    argparser = Cmd2ArgumentParser(description="view account details")
    argparser.add_argument("account_name", help="name of account")
    argparser.add_argument(
        "--unsafe", help="show plaintext API key", action="store_true"
    )

    @with_argparser(argparser)
    @cmd2.with_category(CUSTOM_CATEGORY)
    def do_view_account(self, arg):
        account_name = arg.account_name
        unsafe = arg.unsafe
        view_account(account_name, self.passphrase, unsafe)

    argparser = Cmd2ArgumentParser(description="delete account")
    argparser.add_argument("account_name", help="name of account")

    @with_argparser(argparser)
    @cmd2.with_category(CUSTOM_CATEGORY)
    def do_delete_account(self, arg):
        account_name = arg.account_name
        delete_account(account_name)

    argparser = Cmd2ArgumentParser(description="list all accounts")

    @with_argparser(argparser)
    @cmd2.with_category(CUSTOM_CATEGORY)
    def do_list_accounts(self, arg):
        list_accounts()

    argparser = Cmd2ArgumentParser(description="manage deployments")
    argparser.add_argument("account_name", help="name of account")

    @with_argparser(argparser)
    @cmd2.with_category(DEPLOYMENTS)
    def do_deployments(self, arg):
        table = self.db.table("account_details")
        accounts = []
        for account_name in table.all():
            accounts.append(account_name.get("account_name"))

        if arg.account_name not in accounts:
            print("Invalid account")
        else:
            app_one = AccountApp(self.db, self.passphrase, arg.account_name)
            app_one.cmdloop()


if __name__ == "__main__":
    app = HomepageApp()
    app.cmdloop()
