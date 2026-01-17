from internetarchive import search_items

def test_search(query_str):
    print(f"Searching for: {query_str}")
    search = search_items(query_str)
    
    count = 0
    for result in search:
        print(f"Found Item: {result['identifier']}")
        count += 1
        if count >= 3:
            break
            
    if count == 0:
        print("No results found.")

if __name__ == "__main__":
    test_search('title:(Sony) AND collection:manuals')