import requests
from collections import defaultdict

GBIF_SEARCH_URL = "https://api.gbif.org/v1/species/search"
GBIF_MEDIA_URL = "https://api.gbif.org/v1/species/{key}/media"

def safe_join(items):
    """Join list items safely"""
    if not items:
        return "N/A"
    return ", ".join(items)

def fetch_species(query: str, limit: int = 50):
    """
    Fetch species from GBIF API filtered to Animalia.
    Returns list of species with images and info.
    """
    params = {
        "q": query,
        "rank": "SPECIES",
        "limit": limit
    }

    try:
        resp = requests.get(GBIF_SEARCH_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

    results = []

    for item in data.get("results", []):
        # Only include animals
        if item.get("kingdom") != "Animalia":
            continue

        species_key = item.get("key")

        # Fetch images for this species
        try:
            media_resp = requests.get(GBIF_MEDIA_URL.format(key=species_key), timeout=10)
            media_resp.raise_for_status()
            media_data = media_resp.json()
            images = [m.get("identifier") for m in media_data.get("results", []) if m.get("type") == "StillImage"]
        except Exception:
            images = []

        # Skip species with no images
        if not images:
            continue

        results.append({
            "scientific_name": item.get("canonicalName"),
            "authorship": item.get("authorship") or item.get("rank"),
            "kingdom": item.get("kingdom") or "Animalia",
            "family": item.get("family") or "Unknown",
            "vernacular_name": item.get("vernacularName") or "N/A",
            "habitats": safe_join(item.get("habitats") or []),
            "threat_statuses": safe_join(item.get("threatened") or []),
            "extinct": item.get("taxonomicStatus") == "EXCLUDED",
            "image_urls": images
        })

    if not results:
        return {"error": "No animals found for this search."}

    # Group by family
    grouped = defaultdict(list)
    for sp in results:
        grouped[sp["family"]].append(sp)

    grouped_list = [{"family": fam, "species": sp_list} for fam, sp_list in grouped.items()]

    return {
        "query": query,
        "count": len(results),
        "groups": grouped_list
    }
