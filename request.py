import requests
import json

url = "https://api.gbif.org/v1/species/search"

params = {
    "datasetKey": "d7dddbf4-2cf0-4f39-9b2a-bb099caae36c",
    "q": "kangaroo"
}

headers = {
    "Accept": "application/json"
}


def get_vernacular_name(vernacular_list):
    if not vernacular_list:
        return None
    # Try to find first with language == 'eng'
    for name_obj in vernacular_list:
        if name_obj.get("language") == "eng":
            return name_obj.get("vernacularName")
    # Fallback: return first name available
    return vernacular_list[0].get("vernacularName")


def safe_join(list_like):
    if not list_like:
        return None
    return ", ".join(list_like)


def main():
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"Request URL: {response.url}")
        response.raise_for_status()
    except requests.exceptions.Timeout:
        print("Request timed out. Try increasing the timeout or check network connectivity.")
        return
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)
        return

    try:
        data = response.json()
    except ValueError:
        print("Response is not valid JSON. Raw body:")
        print(response.text)
        return

    filtered = []
    if vernacular_names := data.get("vernacularNames"):
        print("Vernacular Names found at root level:")
        for name in vernacular_names:
            print(f"- {name.get('vernacularName')} ({name.get('language')})")       
    for item in data.get("results", []):
        filtered.append({
            "scientific_name": item.get("scientificName"),
            "authorship": item.get("authorship"),
            "kingdom": item.get("kingdom"),
            "habitats": safe_join(item.get("habitats") or []),
            "threat_statuses": safe_join(item.get("threatStatuses") or []),
            "vernacular_name": get_vernacular_name(item.get("vernacularNames") or [])
        })

    for animal in filtered:
        print(json.dumps(animal, ensure_ascii=False))

    print(f"Total records found: {data.get('count', 0)}")


if __name__ == "__main__":
    main()