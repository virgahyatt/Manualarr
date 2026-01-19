from internetarchive import get_item

def inspect_item(identifier):
    print(f"Inspecting item: {identifier}")
    item = get_item(identifier)
    print(f"Title: {item.metadata.get('title')}")
    print(f"Mediatype: {item.metadata.get('mediatype')}")
    print(f"Collection: {item.metadata.get('collection')}")
    print("Files:")
    for file in item.files:
        if file['name'].lower().endswith('.pdf'):
            print(f" - PDF: {file['name']}")

if __name__ == "__main__":
    inspect_item("brotherax110usermanual")