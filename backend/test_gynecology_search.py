"""
Test if gynecology subfield search is working properly.
Check what journals are returned for "Obstetrics and Gynecology" subfield.
"""
import pyalex
from app.services.openalex.search import find_journals_by_subfield

print("=" * 80)
print("TESTING GYNECOLOGY SUBFIELD SEARCH")
print("=" * 80)

# Test 1: Direct OpenAlex query for Obstetrics and Gynecology
print("\n1. Direct OpenAlex query for 'Obstetrics and Gynecology' journals...")

# Try to find works in this subfield
works = pyalex.Works().filter(
    topics={"subfield": {"id": "Obstetrics and Gynecology"}},
    type="article",
    from_publication_date="2019-01-01"
).group_by("primary_location.source.id").get(per_page=25)

print(f"\nFound {len(works)} journal groups")
print("\nTop journals by work count:")
for i, group in enumerate(works[:15], 1):
    source_id = group.get("key_display_name", "Unknown")
    count = group.get("count", 0)
    print(f"{i}. {source_id} ({count} works)")
    if "gynec" in source_id.lower() and "international" in source_id.lower():
        print(f"   ^^^ IJGO FOUND! ^^^")

# Test 2: Using our search function
print("\n" + "=" * 80)
print("2. Testing our find_journals_by_subfield function...")
print("=" * 80)

result = find_journals_by_subfield("Obstetrics and Gynecology", [])
print(f"\nOur function returned {len(result)} journals")

# Check if IJGO is in the results
ijgo_found = False
for source_id, data in result.items():
    if "gynec" in source_id.lower() and ("international" in source_id.lower() or "S4210216427" in source_id):
        print(f"\nIJGO FOUND in our search!")
        print(f"  Source ID: {source_id}")
        print(f"  Data: {data}")
        ijgo_found = True

if not ijgo_found:
    print("\nIJGO NOT FOUND in our search results")
    print("\nFirst 10 results from our function:")
    for i, (source_id, data) in enumerate(list(result.items())[:10], 1):
        print(f"{i}. {source_id}: {data}")
