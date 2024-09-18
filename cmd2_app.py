import cmd2
from cmd2 import Cmd2ArgumentParser, with_argparser
from pyfiglet import Figlet
import account
from getpass import getpass
from tinydb import TinyDB
from pathlib import Path
from rich import print
from loguru import logger
import encrypt


class BasicApp(cmd2.Cmd):
    CUSTOM_CATEGORY = "CloudGit Commands"

    def __init__(self):
        super().__init__()
        # Prints an intro banner once upon application startup
        f = Figlet()
        self.intro = f.renderText("CloudGit")

        # Show this as the prompt when asking for input
        self.prompt = "cloudgit> "

        # Set the default category name
        self.default_category = "Built-in Commands"

        home = Path.home()
        file = f"{home}/.cloudgit/cg.db"
        obj = Path(file)
        db = None

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
            db = TinyDB(file)
            self.passphrase = attempt2

            check_value = encrypt.encrypt_string(self.passphrase, "PRESENT")
            new_table = db.table("key_check")
            new_table.insert({"check_key": check_value})

        else:
            self.passphrase = getpass("Enter passphrase: ")
            print("Verifying passphrase...")

            db = TinyDB(file)
            table = db.table("key_check")
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


if __name__ == "__main__":
    app = BasicApp()
    app.cmdloop()
