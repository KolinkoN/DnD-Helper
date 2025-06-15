def main():
    import json
    with open("spells.json", "r", encoding="utf-8") as file:
        data = json.load(file)
        
        types = set()
        for record in data:

            damage_type = data[record].get("damage_type")
            types.add(damage_type)
        for type in types:
            if not type:
                continue
            print(f"{type.upper()} = '{type.lower()}'")


if __name__ == "__main__":
    main()