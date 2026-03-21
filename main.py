import sys
from pymongo import MongoClient

# -----------------------------
# Helper function: display items in pages
# -----------------------------
def display_paginated(items, page_size=5):
    """
    Display a list of items in pages of 'page_size'.
    Allows user to navigate Next/Previous.
    """
    if not items:
        print("No items found.")
        return

    total = len(items)
    page = 0

    while True:
        start = page * page_size
        end = start + page_size
        print(f"\n--- Showing items {start + 1} to {min(end, total)} of {total} ---")
        for i, item in enumerate(items[start:end], start=1):
            print(f"{start + i}. {item['name']} | {item['category']} | ${item['price']}")
            if 'short_description' in item:
                print(f"   {item['short_description']}")

        # Navigation
        nav = input("\nEnter N for Next, P for Previous, or Q to Quit pagination: ").strip().upper()
        if nav == "N":
            if end >= total:
                print("Already on last page.")
            else:
                page += 1
        elif nav == "P":
            if page == 0:
                print("Already on first page.")
            else:
                page -= 1
        elif nav == "Q":
            break
        else:
            print("Invalid input.")


# -----------------------------
# Phase 2 Operations
# -----------------------------
def discount_check(collection):
    """
    Ask user for furniture name and check if it's on discount
    """
    name = input("Enter furniture name to check discount: ").strip()
    results = list(collection.find({"name": name}))

    if not results:
        print("No furniture found with that name.")
        return

    # If multiple items with same name, allow user to choose by ID
    if len(results) > 1:
        print("Multiple items found:")
        for i, item in enumerate(results):
            print(f"{i + 1}: ID={item['item_id']}, Category={item['category']}, Price=${item['price']}")
        choice = int(input("Choose item number: ")) - 1
        item = results[choice]
    else:
        item = results[0]

    # Check discount
    if item.get("old_price") and item["old_price"] > item["price"]:
        print(f"Name: {item['name']}")
        print(f"Category: {item['category']}")
        print(f"Price: ${item['price']}")
        print(f"Old Price: ${item['old_price']}")
    else:
        print("This furniture is not on discount.")


def keyword_search(collection):
    """
    Search furniture by keyword in name (case-sensitive)
    """
    keyword = input("Enter keyword to search in furniture names: ").strip()
    results = list(collection.find({"name": {"$regex": keyword}}))
    display_paginated(results)


def category_search(collection):
    """
    Search furniture by category (display names and IDs in descending price order)
    """
    # Get list of unique categories
    categories = collection.distinct("category")
    print("\nAvailable categories:")
    for i, cat in enumerate(categories, start=1):
        print(f"{i}. {cat}")

    choice = int(input("Choose category number: ")) - 1
    if choice < 0 or choice >= len(categories):
        print("Invalid choice")
        return

    selected_category = categories[choice]
    results = list(collection.find({"category": selected_category}).sort("price", -1))

    # Display paginated list of names and IDs
    page_size = 5
    total = len(results)
    page = 0

    while True:
        start = page * page_size
        end = start + page_size
        print(f"\n--- {selected_category} items {start + 1} to {min(end, total)} of {total} ---")
        for i, item in enumerate(results[start:end], start=1):
            print(f"{start + i}. Name: {item['name']}, ID: {item['item_id']}, Price: ${item['price']}")

        nav = input("Enter N for Next, P for Previous, S to select item, Q to quit: ").strip().upper()
        if nav == "N":
            if end >= total:
                print("Already on last page.")
            else:
                page += 1
        elif nav == "P":
            if page == 0:
                print("Already on first page.")
            else:
                page -= 1
        elif nav == "S":
            item_id = input("Enter item_id to view full details: ").strip()
            item = collection.find_one({"item_id": item_id})
            if item:
                print("\n--- Item Details ---")
                print(f"Name: {item['name']}")
                print(f"Category: {item['category']}")
                print(f"Price: ${item['price']}")
                print(f"Short Description: {item['short_description']}")
                print(f"Designer: {item['designer']}")
            else:
                print("Item not found.")
        elif nav == "Q":
            break
        else:
            print("Invalid input.")


def add_item(collection):
    """
    Add new furniture to the database
    """
    print("\nEnter new furniture details:")

    item_id = input("Item ID: ").strip()
    # Check uniqueness
    if collection.find_one({"item_id": item_id}):
        print("Item ID already exists. Cannot add.")
        return

    name = input("Name: ").strip()
    category = input("Category: ").strip()
    price = float(input("Price: ").strip())
    short_description = input("Short Description: ").strip()
    designer = input("Designer: ").strip()

    new_item = {
        "item_id": item_id,
        "name": name,
        "category": category,
        "price": price,
        "short_description": short_description,
        "designer": designer,
        "old_price": None,
        "sellable_online": None,
        "other_colors": None,
        "depth": None,
        "height": None,
        "width": None
    }

    collection.insert_one(new_item)
    print("Item successfully added!")


# -----------------------------
# MAIN PROGRAM
# -----------------------------
def main():
    """
    Main menu loop
    """
    if len(sys.argv) != 2:
        print("Usage: python main.py <port>")
        return

    port = sys.argv[1]
    client = MongoClient(f"mongodb://localhost:{port}/")
    db = client["291db"]
    collection = db["furniture"]

    while True:
        print("\n=== IKEA Furniture Database ===")
        print("1. Check Discount")
        print("2. Search by Keyword")
        print("3. Search by Category")
        print("4. Add New Item")
        print("5. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            discount_check(collection)
        elif choice == "2":
            keyword_search(collection)
        elif choice == "3":
            category_search(collection)
        elif choice == "4":
            add_item(collection)
        elif choice == "5":
            print("Exiting program.")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()