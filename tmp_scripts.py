def main():
    import json
    with open("races.json", "r") as file:
        data = json.load(file)
        for record in data:
            name = record.get("name")
            print(f"{name.upper()} = '{name}'")


if __name__ == "__main__":
    main()