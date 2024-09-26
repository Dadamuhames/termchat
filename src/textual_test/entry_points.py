from textual_test.database.create_tables import create_tables
from textual_test.main import MyApp


def main():
    create_tables()
    app = MyApp()

    app.run()
