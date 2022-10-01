import os
from scrape import fetch_formatted_data
from bot import send_message

CACHE_FILE = os.environ.get("CACHE_FILE", "cache.txt")


def has_changed(str):
    changed = False
    with open(CACHE_FILE, "r+") as f:
        prev = f.read()
        if str != prev:
            changed = True
            f.seek(0)
            f.write(str)
            f.truncate()
    return changed


def main():
    formatted_data = fetch_formatted_data() or "No hay cupos disponibles :("
    print(formatted_data)
    truncated = "\n".join(formatted_data.split("\n")[:-1])
    if has_changed(truncated):
        send_message(formatted_data)


if __name__ == "__main__":
    main()
