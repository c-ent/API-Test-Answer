### PS Code Challenge 1
Setup
Install dependencies: npm install
Start the server: node server.js
Run the main script: python main.py
Output
The daily property list is saved in data/snapshots/day_{day}.json.

### Normalization
The data from company_a, company_b, and company_c is normalized to the following schema:

address: Street name and number (lowercase)
market: Closest market to the property (camel-case & lowercase)
subMarket: City of the property (camel-case & lowercase)
state: One of the 50 US state abbreviations (lowercase)
zipCode: Zip code of the property, in 5 or 9 digit format
company: Name of the company that owns the property
numBeds: Number of beds
numBaths: Number of baths
squareFeet: Square footage of the property
price: Monthly rental price
description: Description of the property
images: List of image URLs of the property
latitude: Latitude of the property
longitude: Longitude of the property
dateAdded: Timestamp of when the property was first added

### Property Status
Each property is assigned a status of 'actively_listing' if it's new or hasn't been removed since the previous day. Duplicates are removed and properties not listed on the next day are marked as 'off_market'.

### Market and Submarket
The market and submarket data are set using the markets.json file, based on the latitude and longitude of each property.

### Bonus Feature
To fetch all properties in the Simple List system within a 65-mile radius, use the GET endpoint:

http://localhost:5000/properties_within_radius?latitude={latitude}&longitude={longitude}

Replace {latitude} and {longitude} with your desired coordinates.