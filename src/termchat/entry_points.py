from termchat.database.create_tables import create_tables
from termchat.main import MyApp


def main():
    create_tables()
    app = MyApp()

    app.run()
