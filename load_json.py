# -----------------------------
# load_json.py
# -----------------------------
# This script reads a JSON file and loads its data into a MongoDB collection.
# It demonstrates:
# - Reading command line arguments
# - Handling files and JSON
# - Connecting to MongoDB
# - Data cleaning
# - Batch insertion for efficiency
# -----------------------------

import sys                     # Provides access to command-line arguments via sys.argv
import json                    # Provides functions to parse JSON files into Python dictionaries/lists
from pymongo import MongoClient  # MongoDB driver to connect and operate on MongoDB databases


def main():
    """
    Entry point of the program.
    Handles:
    - reading command line arguments
    - connecting to MongoDB
    - creating database + collection
    - loading JSON data in batches
    """

    # -----------------------------
    # 1. HANDLE COMMAND LINE INPUT
    # -----------------------------
    # sys.argv is a list where:
    # sys.argv[0] = script name ("load_json.py")
    # sys.argv[1] = first argument (JSON file path)
    # sys.argv[2] = second argument (MongoDB port)
    # We require exactly 2 arguments besides the script name.
    if len(sys.argv) != 3:
        print("Usage: python load_json.py <file.json> <port>")
        return  # exit the program if arguments are missing

    filename = sys.argv[1]  # JSON file path provided by the user
    port = sys.argv[2]      # MongoDB port provided by the user (as string)

    print(f"Loading file: {filename}")
    print(f"Using port: {port}")

    # -----------------------------
    # 2. CONNECT TO MONGODB
    # -----------------------------
    # MongoClient establishes a connection to the MongoDB server.
    # Format of URI: "mongodb://<host>:<port>/"
    # Default host is localhost (running on the same machine)
    client = MongoClient(f"mongodb://localhost:{port}/")

    # Access or create database named "291db"
    # If the database doesn't exist yet, MongoDB will create it automatically
    db = client["291db"]

    # -----------------------------
    # 3. CREATE COLLECTION
    # -----------------------------
    # Collections are like tables in relational databases
    # Assignment requirement: drop the collection if it already exists
    if "furniture" in db.list_collection_names():
        print("Collection already exists. Dropping it...")
        db.drop_collection("furniture")  # completely removes the collection

    # Create a new collection called "furniture"
    # Accessing it via db["furniture"] also creates it if it doesn't exist
    collection = db["furniture"]
    print("Created collection: furniture")

    # -----------------------------
    # 4. READ JSON FILE
    # -----------------------------
    try:
        # Open the file in read mode with UTF-8 encoding
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)  # Parse JSON into Python list/dictionary
            # json.load converts JSON arrays → Python lists, JSON objects → Python dicts
    except Exception as e:
        print("Error reading JSON file:", e)
        return  # exit program if file read fails

    print(f"Total items in file: {len(data)}")  # show number of items loaded

    # -----------------------------
    # 5. PROCESS DATA IN BATCHES
    # -----------------------------
    batch_size = 100   # Number of documents to insert at once (improves performance)
    batch = []         # Temporary list to hold items before inserting

    # Loop over each item (dictionary) in the JSON file
    for item in data:

        # -----------------------------
        # 6. CLEAN / FORMAT DATA
        # -----------------------------
        # Only keep the required fields for insertion
        # Use item.get("field", default) to avoid KeyError if field is missing
        # Convert numeric fields to float when needed
        cleaned_item = {
            "item_id": item.get("item_id", None),           # unique identifier
            "name": item.get("name", None),                 # product name
            "category": item.get("category", None),         # furniture category
            "price": float(item.get("price", 0)) if item.get("price") else None,  # convert price to float
            "short_description": item.get("short_description", None),
            "designer": item.get("designer", None),

            # Optional fields (some may not exist in JSON)
            "old_price": float(item.get("old_price")) if item.get("old_price") else None,
            "sellable_online": item.get("sellable_online", None),
            "other_colors": item.get("other_colors", None),
            "depth": item.get("depth", None),
            "height": item.get("height", None),
            "width": item.get("width", None)
        }

        # Add cleaned item to the batch
        batch.append(cleaned_item)

        # -----------------------------
        # 7. INSERT BATCH WHEN FULL
        # -----------------------------
        # Only insert to MongoDB once batch_size items are collected
        if len(batch) == batch_size:
            collection.insert_many(batch)  # insert list of documents
            print(f"Inserted batch of {batch_size} items")
            batch = []  # reset batch to collect next items

    # -----------------------------
    # 8. INSERT REMAINING ITEMS
    # -----------------------------
    # If there are leftover items not filling a full batch, insert them too
    if batch:
        collection.insert_many(batch)
        print(f"Inserted final batch of {len(batch)} items")

    print("Finished loading data into MongoDB!")


# -----------------------------
# RUN PROGRAM
# -----------------------------
# This ensures main() runs only when the script is executed directly,
# not when it is imported as a module in another script
if __name__ == "__main__":
    main()