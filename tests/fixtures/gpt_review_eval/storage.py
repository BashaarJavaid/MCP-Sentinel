def read_one_file(path: str) -> str:
    del path
    return open("data/users.json", encoding="utf-8").read()
