import requests
import json

INATURALIST_URL = "https://api.inaturalist.org/v1/taxa"

params = {
    "q": "kangaroo",
    "rank": "species",
    "per_page": 20
}


def extract_images(taxon):
    """Extract image URLs from iNaturalist taxon"""
    photo = taxon.get("default_photo")
    if not photo:
        return []

    return [url for url in [photo.get("medium_url"), photo.get("large_url")] if url]


def safe_join(items):
    """Safely join a list of strings, handle None."""
    if not items:
        return None
    return ", ".join(items)


def main():
    try:
        response = requests.get(INATURALIST_URL, params=params, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return

    try:
        data = response.json()
    except ValueError:
        print("Error: Response is not valid JSON.")
        return

    filtered = []

    for item in data.get("results", []):
        images = extract_images(item)
        
        filtered.append({
            "gbif_key": item.get("id", ""),
            "scientific_name": item.get("name"),
            "authorship": item.get("rank"),
            "kingdom": "Animalia",
            "habitats": safe_join(item.get("habitats") or []),
            "threat_statuses": safe_join(item.get("threatened") or []),
            "vernacular_name": item.get("preferred_common_name"),
            "image_urls": images
        })

    print("Filtered Results:\n")
    for r in filtered:
        print(json.dumps(r, ensure_ascii=False, indent=2))

    print(f"\nTotal records found: {len(filtered)}")


if __name__ == "__main__":
    main()