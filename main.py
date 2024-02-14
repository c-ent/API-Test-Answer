import json
import math
import requests

# API endpoint
API_ENDPOINT = "http://localhost:5000/update_properties"

def post_properties(properties):
    try:
        response = requests.post(API_ENDPOINT, json=properties)
        if response.status_code == 200:
            print("Properties successfully posted to the API.")
        else:
            print(f"Failed to post properties. Status code: {response.status_code}")
            print("Error message:", response.text)
    except Exception as e: 
        print("An error occurred while posting properties:", e)

# Define the function to normalize the address format
# Though its sepcially made for company B 
def normalize_address_format(properties):
    for property_data in properties:
        if 'street' in property_data and '#text' in property_data['street']:
            property_data['address'] = property_data['street']['#text']
    return properties


# Normalize the property data for company A
def normalize_property_company_a(property_data, company_name):
    def get_number_property(property_data, property_name):
        try:
            value = float(property_data.get(property_name) or "0")
            return int(value)
        except ValueError:
            return 0

    num_beds = get_number_property(property_data, "beds")
    num_baths = get_number_property(property_data, "baths")
    square_feet = get_number_property(property_data, "squareFootage")
    price = get_number_property(property_data, "rentAmount")

    normalized_property = {
        "address": property_data.get("address", "").lower(),
        "market": "",  # To be assigned later
        "subMarket": "", # To be assigned later
        "state": property_data.get("state", "").lower(),
        "zipCode": str(property_data.get("zip", "")),
        "company": company_name,
        "numBeds": num_beds,
        "numBaths": num_baths,
        "squareFeet": square_feet,
        "price": price,
        "description": property_data.get("description", ""),
        "images": property_data.get("photos", []),
        "latitude": float(property_data.get("latitude", 0)),
        "longitude": float(property_data.get("longitude", 0)),
        "dateAdded": property_data.get("dateAvailable", "") 
    }
    return normalized_property

# Normalize the property data for company B
def normalize_property_company_b(property_data, company_name):
    def get_number_property(property_data, property_name):
        try:
            value = float(property_data.get(property_name) or "0")
            return int(value)
        except ValueError:
            return 0

    numBedrooms = get_number_property(property_data, "numBedrooms")
    numFullBaths = get_number_property(property_data, "numFullBaths")
    squareFeet = get_number_property(property_data, "squareFeet")
    price = get_number_property(property_data, "price")

    normalized_property = {
        "address": property_data.get("street", {}).get("#text", "").lower(),
        "market": "",  # To be assigned later
        "subMarket": "",# To be assigned later
        "state": property_data.get("state", "").lower(),
        "zipCode": str(property_data.get("zip", "")),
        "company": company_name,
        "numBeds": numBedrooms,
        "numBaths": numFullBaths,
        "squareFeet": squareFeet,
        "price": price,
        "description": property_data.get("description", ""),
        "images": [photo["@_source"] for photo in property_data.get("ListingPhoto", [])],
        "latitude": float(property_data.get("latitude", 0)),
        "longitude": float(property_data.get("longitude", 0)),
        "dateAdded": property_data.get("dateAvailable", "")  
    }
    return normalized_property

# Normalize the property data for company C
def normalize_property_company_c(property_data, company_name):
    def get_number_property(property_data, property_name):
        try:
            value = float(property_data.get(property_name) or "0")
            return int(value)
        except ValueError:
            return 0

    numBeds = get_number_property(property_data, "numBeds")
    numBaths = get_number_property(property_data, "numBaths")
    squareFeet = get_number_property(property_data, "squareFeet")
    price = get_number_property(property_data, "price")

    normalized_property = {
        "address": property_data.get("address", "").lower(),
        "market": "",  # To be assigned later
        "subMarket": "",# To be assigned later
        "state": property_data.get("state", "").lower(),
        "zipCode": str(property_data.get("zip", "")),
        "company": company_name,
        "numBeds": numBeds,
        "numBaths": numBaths,
        "squareFeet": squareFeet,
        "price": price,
        "description": property_data.get("description", ""),
        "images": [photo["Url"] for photo in property_data.get("images", [])],
        "latitude": float(property_data.get("latitude", 0)),
        "longitude": float(property_data.get("longitude", 0)),
        "dateAdded": "" 
    }
    return normalized_property

# Load and normalize the properties
def load_and_normalize_properties(file_path, company_name):
    with open(file_path) as f:
        properties_data = json.load(f)
    if company_name == 'company_a':
        normalize_func = normalize_property_company_a
    elif company_name == 'company_b':
        normalize_func = normalize_property_company_b
    elif company_name == 'company_c':
        normalize_func = normalize_property_company_c
    else:
        raise ValueError("Invalid company name")
    normalized_properties = [normalize_func(property_data, company_name) for property_data in properties_data]
    return normalized_properties

# Load the properties for each company
def get_company_data_feeds_for_day(day):
    properties_company_a = load_and_normalize_properties(f"data/company_feeds/day_{day}/company_a.json", "company_a")
    properties_company_b = load_and_normalize_properties(f"data/company_feeds/day_{day}/company_b.json", "company_b")
    properties_company_c = load_and_normalize_properties(f"data/company_feeds/day_{day}/company_c.json", "company_c")

    return properties_company_a, properties_company_b, properties_company_c

def generate_snapshot_for_day(day, properties_company_a, properties_company_b, properties_company_c, off_market_properties=None):
    if off_market_properties is None:
        off_market_properties = []
    properties_for_day = properties_company_a + properties_company_b + properties_company_c + off_market_properties
    properties_json = json.dumps(properties_for_day, indent = 4)
    with open(f"data/snapshots/day_{day}.json", 'w') as f:
        f.write(properties_json)


def get_markets_data():
    with open("data/markets.json") as f:
        return json.load(f)


markets_data = get_markets_data()

def remove_duplicates(properties_a, properties_b, properties_c):
    address_set = set()
    for properties in [properties_a, properties_b, properties_c]:
        properties[:] = [property for property in properties if not (property['address'] in address_set or address_set.add(property['address']))]


def calculate_distance(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    R = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Calculate the differences
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    # Haversine formula to calculate distance
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Distance in kilometers
    distance = R * c

    return distance

def find_closest_market(property_location, markets_data):
    closest_market = None
    closest_distance = float('inf')
    
    # Calculate distance to each market
    for market_data in markets_data:
        market_location = (market_data["latitude"], market_data["longitude"])
        distance = calculate_distance(property_location[0], property_location[1], market_location[0], market_location[1])
        if distance < closest_distance:
            closest_distance = distance
            closest_market = market_data["market"]

    return closest_market

def load_previous_day_snapshot(day):
    if day == 0:
        return []
    with open(f"data/snapshots/day_{day - 1}.json", 'r') as f:
        return json.load(f)

def set_property_status_and_market(property, current_day_addresses, previous_day_addresses, markets_data):
    if 'address' in property:
        if property['address'] in current_day_addresses or property['address'] not in previous_day_addresses:
            property['status'] = 'actively_listed'
        # Set the market for the property
        if 'market' in property and any(market['market'] == property['market'] for market in markets_data):
            # If the market attribute exists and its value is in the Simple List markets, use it directly
            pass
        else:
            # Otherwise, determine the closest market by geodistance
            property_location = (property["latitude"], property["longitude"])
            property["market"] = find_closest_market(property_location, markets_data)
        # Set the subMarket for the property
        property["subMarket"] = property["market"].lower()


def update_status_based_on_previous_day(day, *company_properties):
    previous_day_snapshot = load_previous_day_snapshot(day)
    previous_day_addresses = {property['address']: property for property in previous_day_snapshot} if previous_day_snapshot else {}
    current_day_addresses = {property['address'] for properties in company_properties for property in properties}

    for properties in company_properties:
        for property in properties:
            set_property_status_and_market(property, current_day_addresses, previous_day_addresses, markets_data)

    off_market_properties = [data for data in previous_day_snapshot if data['address'] not in current_day_addresses]
    for property in off_market_properties:
        property['status'] = 'off_market'

    return off_market_properties


if __name__ == "__main__":

    CURRENT_DAY = 0
    # ----------***** DAY 0 *****----------

    properties_company_a, properties_company_b, properties_company_c = get_company_data_feeds_for_day(CURRENT_DAY)
    
    properties_company_a = normalize_address_format(properties_company_a)
    properties_company_b = normalize_address_format(properties_company_b)
    properties_company_c = normalize_address_format(properties_company_c)

    update_status_based_on_previous_day(CURRENT_DAY, properties_company_a, properties_company_b, properties_company_c)

    remove_duplicates(properties_company_a, properties_company_b, properties_company_c)  # Add this line to remove duplicates

    post_properties(properties_company_a + properties_company_b + properties_company_c)

    generate_snapshot_for_day(CURRENT_DAY, properties_company_a, properties_company_b, properties_company_c)
    CURRENT_DAY += 1

    # ----------***** DAY 1 *****----------
    properties_company_a, properties_company_b, properties_company_c = get_company_data_feeds_for_day(CURRENT_DAY)

    properties_company_a = normalize_address_format(properties_company_a)
    properties_company_b = normalize_address_format(properties_company_b)
    properties_company_c = normalize_address_format(properties_company_c)

    update_status_based_on_previous_day(CURRENT_DAY, properties_company_a, properties_company_b, properties_company_c)
    
    remove_duplicates(properties_company_a, properties_company_b, properties_company_c)  # To remove duplicates

    off_market_properties = update_status_based_on_previous_day(CURRENT_DAY, properties_company_a, properties_company_b, properties_company_c)
    
    post_properties(properties_company_a + properties_company_b + properties_company_c + off_market_properties)

    generate_snapshot_for_day(CURRENT_DAY, properties_company_a, properties_company_b, properties_company_c, off_market_properties)

    CURRENT_DAY += 1


    # # ----------***** DAY 2 *****----------

    properties_company_a, properties_company_b, properties_company_c = get_company_data_feeds_for_day(CURRENT_DAY)

    properties_company_a = normalize_address_format(properties_company_a)
    properties_company_b = normalize_address_format(properties_company_b)
    properties_company_c = normalize_address_format(properties_company_c)
    
    update_status_based_on_previous_day(CURRENT_DAY, properties_company_a, properties_company_b, properties_company_c)
    remove_duplicates(properties_company_a, properties_company_b, properties_company_c)  # To remove duplicates
    off_market_properties = update_status_based_on_previous_day(CURRENT_DAY, properties_company_a, properties_company_b, properties_company_c)
    
    post_properties(properties_company_a + properties_company_b + properties_company_c + off_market_properties)

    generate_snapshot_for_day(CURRENT_DAY, properties_company_a, properties_company_b, properties_company_c, off_market_properties)
    
    CURRENT_DAY += 1

