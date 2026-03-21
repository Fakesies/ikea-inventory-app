import sys                     # allows us to read command line arguments
import json                    # used to read JSON files
from pymongo import MongoClient  # MongoDB driver


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
    # Expecting: python load_json.py <file.json> <port>
    if len(sys.argv) != 3:
        print("Usage: python load_json.py <file.json> <port>")
        return

    filename = sys.argv[1]  # JSON file name
    port = sys.argv[2]      # MongoDB port

    print(f"Loading file: {filename}")
    print(f"Using port: {port}")

    # -----------------------------
    # 2. CONNECT TO MONGODB
    # -----------------------------
    # Connect to local MongoDB server using provided port
    client = MongoClient(f"mongodb://localhost:{port}/")

    # Create/access database "291db"
    db = client["291db"]

    # -----------------------------
    # 3. CREATE COLLECTION
    # -----------------------------
    # If collection already exists, DROP it (assignment requirement)
    if "furniture" in db.list_collection_names():
        print("Collection already exists. Dropping it...")
        db.drop_collection("furniture")

    # Create new collection
    collection = db["furniture"]
    print("Created collection: furniture")

    # -----------------------------
    # 4. READ JSON FILE
    # -----------------------------
    try:
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)  # loads entire JSON file into memory
    except Exception as e:
        print("Error reading JSON file:", e)
        return

    print(f"Total items in file: {len(data)}")

    # -----------------------------
    # 5. PROCESS DATA IN BATCHES
    # -----------------------------
    batch_size = 100   # required: insert in small batches
    batch = []         # temporary list to store items before inserting

    for item in data:
        # -----------------------------
        # 6. CLEAN / FORMAT DATA
        # -----------------------------
        # Only keep required fields:
        # item_id, name, category, price, short_description, designer

        cleaned_item = {
            "item_id": item.get("item_id", None),
            "name": item.get("name", None),
            "category": item.get("category", None),
            "price": float(item.get("price", 0)) if item.get("price") else None,
            "short_description": item.get("short_description", None),
            "designer": item.get("designer", None),

            # Optional fields → set to None
            "old_price": float(item.get("old_price")) if item.get("old_price") else None,
            "sellable_online": item.get("sellable_online", None),
            "other_colors": item.get("other_colors", None),
            "depth": item.get("depth", None),
            "height": item.get("height", None),
            "width": item.get("width", None)
        }

        # Add cleaned item to batch
        batch.append(cleaned_item)

        # -----------------------------
        # 7. INSERT BATCH WHEN FULL
        # -----------------------------
        if len(batch) == batch_size:
            collection.insert_many(batch)
            print(f"Inserted batch of {batch_size} items")
            batch = []  # reset batch

    # -----------------------------
    # 8. INSERT REMAINING ITEMS
    # -----------------------------
    if batch:
        collection.insert_many(batch)
        print(f"Inserted final batch of {len(batch)} items")

    print("Finished loading data into MongoDB!")


# -----------------------------
# RUN PROGRAM
# -----------------------------
if __name__ == "__main__":
    main()