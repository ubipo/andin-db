from parser_types import OsmMeta, Address
from typing import List, Dict
import requests
import json

def match_osm_meta_with_nominatim_res(nominatim: object, osm_metas: List[OsmMeta]):
    try:
        matching = next(m for m in osm_metas if nominatim["osm_type"] == m.osm_type and nominatim["osm_id"] == m.osm_id)
    except StopIteration:
        raise(Exception(f'No matching osm meta object found for nominatim result ("{matching}"), nominatim API might be acting up'))
    
    return matching

def lookup(osm_metas: List[OsmMeta]):
    nominatim_ids = [f"{m.osm_type.upper()[0]}{m.osm_id}" for m in osm_metas]
    query = f"osm_ids={','.join(nominatim_ids)}&format=json"
    url = f"https://nominatim.openstreetmap.org/lookup?{query}"
    req = requests.get(url)
    res = json.loads(req.content)
    addressmap = {}
    for nominatim_res in res:
        osm_meta = match_osm_meta_with_nominatim_res(res[0], osm_metas)
        a: Dict[str, str] = nominatim_res["address"]
        country = a["country_code"]
        postcode = a["postcode"] if "postcode" in a else None
        region = a["state"] if "state" in a else a["country"]
        locality = a["town"] if "town" in a else a["city"] if "city" in a else a["county"] if "county" in a else region
        street_addr = f'{a["road"]} {a["house_number"]}' if "house_number" in a else a["road"] if "road" in a else None
        district = a.get("city_district") if a.get("city_district") != locality else None
        free_els = [a.get("house_name"), street_addr,  a.get("village"), district]
        free_els = [e for e in free_els if e is not None]
        address = Address(", ".join(free_els), locality, region, postcode, country)
        addressmap[osm_meta] = address
    
    addresslist = [addressmap.get(meta) for meta in osm_metas] # List with None's if no address was returned
    return addresslist