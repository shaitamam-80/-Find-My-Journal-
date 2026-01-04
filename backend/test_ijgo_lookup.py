"""
Test direct OpenAlex lookup for IJGO.
Verify it exists and check its subfields.
"""
import pyalex
from pprint import pprint

print("=" * 80)
print("TESTING IJGO IN OPENALEX")
print("=" * 80)

# Direct search for IJGO
print("\n1. Searching for 'International Journal of Gynaecology and Obstetrics'...")
sources = pyalex.Sources().search("International Journal of Gynaecology and Obstetrics").get(per_page=5)

if sources:
    ijgo = sources[0]
    print(f"\nFOUND: {ijgo.get('display_name')}")
    print(f"ID: {ijgo.get('id')}")
    print(f"ISSN: {ijgo.get('issn')}")
    print(f"Works count: {ijgo.get('works_count')}")
    print(f"H-index: {ijgo.get('summary_stats', {}).get('h_index')}")
    print(f"2yr citedness: {ijgo.get('summary_stats', {}).get('2yr_mean_citedness')}")

    print("\nTopics:")
    for topic in ijgo.get('topics', [])[:5]:
        print(f"  - {topic.get('display_name')}")

    print("\nX-Concepts (for subfield matching):")
    for concept in ijgo.get('x_concepts', [])[:10]:
        print(f"  - {concept.get('display_name')} (level: {concept.get('level')}, score: {concept.get('score')})")

    # Check if it has works related to the query
    print("\n" + "=" * 80)
    print("2. Checking if IJGO has works on 'overactive bladder fibromyalgia'...")
    print("=" * 80)

    source_id = ijgo.get('id').split('/')[-1]

    # Search for works in IJGO about OAB and fibromyalgia
    works = pyalex.Works().filter(
        primary_location={"source": {"id": source_id}},
        type="article"
    ).get(per_page=5)

    print(f"\nTotal works in IJGO: {ijgo.get('works_count')}")
    print(f"Sample recent works:")
    for work in works[:3]:
        print(f"  - {work.get('title', 'No title')[:80]}")

    # Check for OAB-related works
    oab_works = pyalex.Works().filter(
        primary_location={"source": {"id": source_id}},
        keywords={"keyword": ["overactive bladder", "urinary incontinence"]}
    ).get(per_page=3)

    if oab_works:
        print(f"\nWorks in IJGO about OAB/urinary topics:")
        for work in oab_works:
            print(f"  - {work.get('title', 'No title')[:80]}")
    else:
        print("\nNo OAB-related works found with keyword filter")

else:
    print("IJGO NOT FOUND!")

print("\n" + "=" * 80)
print("3. Checking Obstetrics and Gynecology subfield...")
print("=" * 80)

# Search for top journals in Obstetrics and Gynecology subfield
print("\nSearching for journals in 'Obstetrics and Gynecology' subfield...")
obs_gyn_sources = pyalex.Sources().search("obstetrics gynecology").get(per_page=10)

print(f"\nTop Obstetrics & Gynecology journals:")
for i, source in enumerate(obs_gyn_sources[:10], 1):
    h_index = source.get('summary_stats', {}).get('h_index', 0)
    works = source.get('works_count', 0)
    print(f"{i}. {source.get('display_name')} (H-index: {h_index}, Works: {works})")
