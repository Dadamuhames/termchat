from termchat.database.create_tables import create_tables
from termchat.main import MyApp


def main():
    try:
        create_tables()
        app = MyApp()

        app.run()

    except ConnectionRefusedError:
        print("API error! Try to update your termchat version")

