from scrape import fetch_formatted_data
from bot import send_message


def main():
    msg = fetch_formatted_data()
    send_message(msg)


if __name__ == "__main__":
    main()
