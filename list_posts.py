from app.queue_service import list_posts


def main():
    rows = list_posts(limit=20)
    for row in rows:
        print(row)


if __name__ == "__main__":
    main()
