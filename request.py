import requests

INATURALIST_URL = "https://api.inaturalist.org/v1/taxa"


def extract_images(taxon):
    """Extract image URLs from iNaturalist taxon"""
    photo = taxon.get("default_photo")
    if not photo:
        return []

    return [
        url for url in
        [photo.get("medium_url"), photo.get("large_url")]
        if url
    ]


def safe_join(items):
    """Safely join a list of strings, handle None."""
    if not items:
        return None
    return ", ".join(items)


def fetch_species(query: str, per_page: int = 20):
    params = {
        "q": query,
        "rank": "species",
        "per_page": per_page
    }

    try:
        response = requests.get(INATURALIST_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

    filtered = []

    for item in data.get("results", []):
        filtered.append({
            "gbif_key": item.get("id", ""),
            "scientific_name": item.get("name"),
            "authorship": item.get("rank"),
            "kingdom": "Animalia",
            "habitats": safe_join(item.get("habitats") or []),
            "threat_statuses": safe_join(item.get("threatened") or []),
            "vernacular_name": item.get("preferred_common_name"),
            "image_urls": extract_images(item)
        })

    return {
        "query": query,
        "count": len(filtered),
        "results": filtered
    }
