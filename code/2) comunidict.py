#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 02:18:45 2024

@author: albertocicchetti
"""
# Load the text file and process the list of comuni
comuni_list = []

# Replace the path below with the path to your .txt file
with open("/Users/albertocicchetti/Desktop/listacomuni.txt", "r", encoding="ISO-8859-1") as file:
    for line in file:
        # Clean each line by removing "Comune di" and stripping any extra spaces
        comune = line.replace("Comune di ", "").strip()
        
        # Correct the "I accentata" for Forlì and Forlì-Cesena
        comune = comune.replace("Forl\x93", "Forlì")
        comune = comune.replace("Forl\x93-Cesena", "Forlì-Cesena")
        
        if comune:  # Check if the line is not empty
            comuni_list.append(comune)

# Display the first few comuni to check if the cleanup worked
print(comuni_list[:10])

# Save the cleaned list to a new text file if needed
with open("/Users/albertocicchetti/Desktop/cleaned_comuni_list.txt", "w", encoding="utf-8") as file:
    for comune in comuni_list:
        file.write(comune + "\n")


import time
from geopy.geocoders import Nominatim

# Initialize Nominatim API
geolocator = Nominatim(user_agent="emilia_romagna_geocoder")

# Dictionary to store the coordinates
comuni_coordinates = {}

# Define bounding box for Emilia-Romagna
emilia_romagna_bbox = {
    "north": 45.3,  # Northern latitude
    "south": 43.5,  # Southern latitude
    "east": 13.0,   # Eastern longitude
    "west": 8.8     # Western longitude
}

# Function to check if coordinates are within Emilia-Romagna
def is_within_emilia_romagna(lat, lon):
    return (
        emilia_romagna_bbox["south"] <= lat <= emilia_romagna_bbox["north"] and
        emilia_romagna_bbox["west"] <= lon <= emilia_romagna_bbox["east"]
    )

# Fetch coordinates for each comune
for comune in comuni_list:
    try:
        location = geolocator.geocode(comune, timeout=10)
        if location:
            if is_within_emilia_romagna(location.latitude, location.longitude):
                comuni_coordinates[comune] = (location.latitude, location.longitude)
            else:
                comuni_coordinates[comune] = (None, None)
                print(f"Coordinates for {comune} are outside Emilia-Romagna: {(location.latitude, location.longitude)}")
        else:
            comuni_coordinates[comune] = (None, None)
        time.sleep(1)  # Adding delay to avoid hitting API limits
    except Exception as e:
        comuni_coordinates[comune] = (None, None)
        print(f"Error fetching data for {comune}: {e}")

# Output the result
print(comuni_coordinates)

# Save the result to a CSV file
import pandas as pd

# Convert the dictionary to a DataFrame
comuni_df = pd.DataFrame(comuni_coordinates.items(), columns=['Comune', 'Coordinates'])

# Split the Coordinates into Latitude and Longitude
comuni_df[['Latitude', 'Longitude']] = pd.DataFrame(comuni_df['Coordinates'].tolist(), index=comuni_df.index)

# Drop the Coordinates column as it is now split
comuni_df.drop(columns=['Coordinates'], inplace=True)

# Save the DataFrame to a CSV file
comuni_df.to_csv("/Users/albertocicchetti/Desktop/comuni_coordinates.csv", index=False)

print("Coordinates saved to comuni_coordinates.csv")
