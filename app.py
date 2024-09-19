from getpass import getpass
from pathlib import Path

import cmd2
from cmd2 import Cmd2ArgumentParser, with_argparser
from loguru import logger
from pyfiglet import Figlet
from rich import print
from tinydb import Query, TinyDB

import account
import encrypt
from build import main as build


class AccountApp(cmd2.Cmd):
    CUSTOM_CATEGORY = "Deployment Manager"

    def __init__(self, db: TinyDB, passphrase: str, account_name: str):
        super().__init__()
        # Show this as the prompt when asking for input
        self.prompt = f"⭐⭐  {account_name}: "
        self.db = db
        self.passphrase = passphrase
        self.account_name = account_name

        # Set the default category name
        self.default_category = "Built-in Commands"

    argparser = Cmd2ArgumentParser(description="build new runner")
    argparser.add_argument("--logs", help="watch logs", action="store_true")

    @with_argparser(argparser)
    @cmd2.with_category(CUSTOM_CATEGORY)
    def do_build(self, arg):
        table = self.db.table("account_details")
        account = Query()
        details = table.get(account.account_name == self.account_name)

        repo = details.get("repo_name")
        key = encrypt.decrypt_string(self.passphrase, details.get("api_key"))
        build(key, self.account_name, repo, self.db)


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
        account.new_account(self.passphrase)

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
        account.view_account(account_name, self.passphrase, unsafe)

    argparser = Cmd2ArgumentParser(description="delete account")
    argparser.add_argument("account_name", help="name of account")

    @with_argparser(argparser)
    @cmd2.with_category(CUSTOM_CATEGORY)
    def do_delete_account(self, arg):
        account_name = arg.account_name
        account.delete_account(account_name)

    argparser = Cmd2ArgumentParser(description="list all accounts")

    @with_argparser(argparser)
    @cmd2.with_category(CUSTOM_CATEGORY)
    def do_list_accounts(self, arg):
        account.list_accounts()

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
