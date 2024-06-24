import sys, sqlite3


def main(args):

    con = sqlite3.connect("comics.sqlite")

    with open("sqldump.sql", "r", encoding="utf-8") as f:
        con.executescript(f.read())


if __name__ == "__main__":
    main(sys.argv)
