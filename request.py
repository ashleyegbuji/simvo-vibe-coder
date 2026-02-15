import httpx
import asyncio

GBIF_BASE = "https://api.gbif.org/v1"
IMG_LIMIT_DEFAULT = 10
REQ_TIMEOUT = 10

async def get_species_images(client: httpx.AsyncClient, species_key: int, image_limit: int = IMG_LIMIT_DEFAULT):
    url = f"{GBIF_BASE}/occurrence/search"
    params = {"taxonKey": species_key, "mediaType": "StillImage", "limit": image_limit}
    try:
        resp = await client.get(url, params=params, timeout=REQ_TIMEOUT)
        if resp.status_code != 200:
            return []
        images = []
        for occ in resp.json().get("results", []):
            for media in occ.get("media", []):
                ident = media.get("identifier")
                if ident:
                    images.append(ident)
        return images
    except httpx.RequestError:
        return []

async def fetch_species_data(search_term: str, image_limit: int = IMG_LIMIT_DEFAULT):
    async with httpx.AsyncClient(timeout=REQ_TIMEOUT) as client:
        # 1️⃣ Search species first
        search_url = f"{GBIF_BASE}/species/search"
        params = {"datasetKey": "d7dddbf4-2cf0-4f39-9b2a-bb099caae36c", "q": search_term}
        try:
            resp = await client.get(search_url, params=params)
            if resp.status_code != 200:
                return []
        except httpx.RequestError:
            return []

        results = resp.json().get("results", [])
        extracted = []

        # 2️⃣ Create tasks for image fetching but don’t block
        image_tasks = []

        for item in results:
            vernacular_name = None
            for vn in item.get("vernacularNames", []):
                if vn.get("language") == "eng":
                    vernacular_name = vn.get("vernacularName")
                    break
            if not vernacular_name and item.get("vernacularNames"):
                vernacular_name = item["vernacularNames"][0].get("vernacularName")

            if vernacular_name:
                key = item.get("key")
                extracted_item = {
                    "scientificName": item.get("scientificName", ""),
                    "authorship": item.get("authorship", ""),
                    "kingdom": item.get("kingdom", ""),
                    "habitats": item.get("habitats", []),
                    "threatStatuses": item.get("threatStatuses", []),
                    "extinct": item.get("extinct", False),
                    "vernacularName": vernacular_name,
                    "images": []  # will fill later asynchronously
                }
                extracted.append(extracted_item)

                if key:
                    # Start image fetch task but don’t await here
                    task = asyncio.create_task(get_species_images(client, key, image_limit))
                    image_tasks.append((len(extracted) - 1, task))

        # 3️⃣ Gather images concurrently
        if image_tasks:
            for idx, task in image_tasks:
                try:
                    extracted[idx]["images"] = await task
                except Exception:
                    extracted[idx]["images"] = []

        return extracted
