# -----------------------------
# main.py
# -----------------------------
# This script provides an interactive menu for a furniture database.
# Features include:
# - Checking if an item is on discount
# - Searching furniture by keyword or category
# - Adding new furniture
# - Paginated display of items
# -----------------------------

import sys  # Access to command-line arguments
from pymongo import MongoClient  # MongoDB driver to interact with database


# -----------------------------
# Helper function: display items in pages
# -----------------------------
def display_paginated(items, page_size=5):
    """
    Display a list of items in pages of 'page_size'.
    Allows user to navigate Next/Previous.
    """
    if not items:  # check if the list is empty
        print("No items found.")
        return

    total = len(items)  # total number of items
    page = 0           # current page index (starts at 0)

    while True:  # loop until user quits
        start = page * page_size
        end = start + page_size
        # Display header for current page
        print(f"\n--- Showing items {start + 1} to {min(end, total)} of {total} ---")
        # Enumerate over items for this page
        for i, item in enumerate(items[start:end], start=1):
            # Display main info: name, category, price
            print(f"{start + i}. {item['name']} | {item['category']} | ${item['price']}")
            # Optional short description
            if 'short_description' in item:
                print(f"   {item['short_description']}")

        # Navigation input from user
        nav = input("\nEnter N for Next, P for Previous, or Q to Quit pagination: ").strip().upper()
        if nav == "N":
            if end >= total:
                print("Already on last page.")
            else:
                page += 1  # move to next page
        elif nav == "P":
            if page == 0:
                print("Already on first page.")
            else:
                page -= 1  # move to previous page
        elif nav == "Q":
            break  # exit pagination
        else:
            print("Invalid input.")


# -----------------------------
# Phase 2 Operations
# -----------------------------
def discount_check(collection):
    """
    Ask user for furniture name and check if it's on discount.
    """
    name = input("Enter furniture name to check discount: ").strip()
    # Search for items with exact name
    results = list(collection.find({"name": name}))

    if not results:
        print("No furniture found with that name.")
        return

    # If multiple items with same name, allow user to select by ID
    if len(results) > 1:
        print("Multiple items found:")
        for i, item in enumerate(results):
            print(f"{i + 1}: ID={item['item_id']}, Category={item['category']}, Price=${item['price']}")
        choice = int(input("Choose item number: ")) - 1
        item = results[choice]
    else:
        item = results[0]

    # Check if old_price exists and is greater than current price
    if item.get("old_price") and item["old_price"] > item["price"]:
        print(f"Name: {item['name']}")
        print(f"Category: {item['category']}")
        print(f"Price: ${item['price']}")
        print(f"Old Price: ${item['old_price']}")
    else:
        print("This furniture is not on discount.")


def keyword_search(collection):
    """
    Search furniture by keyword in name (case-sensitive).
    """
    keyword = input("Enter keyword to search in furniture names: ").strip()
    # MongoDB $regex performs pattern matching
    results = list(collection.find({"name": {"$regex": keyword}}))
    display_paginated(results)  # use helper function to show results in pages


def category_search(collection):
    """
    Search furniture by category and display items in descending price order.
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
    # Find all items in this category, sorted by price descending
    results = list(collection.find({"category": selected_category}).sort("price", -1))

    # Paginate results
    page_size = 5
    total = len(results)
    page = 0

    while True:
        start = page * page_size
        end = start + page_size
        print(f"\n--- {selected_category} items {start + 1} to {min(end, total)} of {total} ---")
        for i, item in enumerate(results[start:end], start=1):
            # Show name, ID, price for each item
            print(f"{start + i}. Name: {item['name']}, ID: {item['item_id']}, Price: ${item['price']}")

        # Navigation options
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
            # User can view full details of a specific item
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
    Add new furniture to the database.
    """
    print("\nEnter new furniture details:")

    item_id = input("Item ID: ").strip()
    # Check if item_id already exists (must be unique)
    if collection.find_one({"item_id": item_id}):
        print("Item ID already exists. Cannot add.")
        return

    # Prompt for other item details
    name = input("Name: ").strip()
    category = input("Category: ").strip()
    price = float(input("Price: ").strip())  # convert input to float
    short_description = input("Short Description: ").strip()
    designer = input("Designer: ").strip()

    # Construct new item dictionary
    new_item = {
        "item_id": item_id,
        "name": name,
        "category": category,
        "price": price,
        "short_description": short_description,
        "designer": designer,
        # Optional fields are set to None by default
        "old_price": None,
        "sellable_online": None,
        "other_colors": None,
        "depth": None,
        "height": None,
        "width": None
    }

    # Insert the new document into MongoDB collection
    collection.insert_one(new_item)
    print("Item successfully added!")


# -----------------------------
# MAIN PROGRAM
# -----------------------------
def main():
    """
    Main menu loop.
    Handles:
    - Connecting to MongoDB
    - Displaying interactive menu
    - Routing user choices to appropriate functions
    """
    if len(sys.argv) != 2:
        print("Usage: python main.py <port>")
        return

    port = sys.argv[1]
    # Connect to MongoDB
    client = MongoClient(f"mongodb://localhost:{port}/")
    db = client["291db"]  # Access database
    collection = db["furniture"]  # Access furniture collection

    while True:
        # Display menu options
        print("\n=== IKEA Furniture Database ===")
        print("1. Check Discount")
        print("2. Search by Keyword")
        print("3. Search by Category")
        print("4. Add New Item")
        print("5. Exit")

        choice = input("Choose an option: ").strip()

        # Route user input to corresponding function
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


# Run the main program only if this script is executed directly
if __name__ == "__main__":
    main()