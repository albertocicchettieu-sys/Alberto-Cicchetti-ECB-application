#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 03:01:48 2024

@author: albertocicchetti
"""

import pandas as pd
from geopy.geocoders import Nominatim
import time

# Load the job offers dataset
df_jobs = pd.read_csv("/Users/albertocicchetti/job_offers_tot.csv")  # Replace with your actual path

# Load the geocoded comuni dataset
df_comuni = pd.read_csv("/Users/albertocicchetti/Desktop/comuni_coordinates.csv")  # Replace with your actual path

# Convert comuni DataFrame to a dictionary for faster lookup
comuni_dict = dict(zip(df_comuni['Comune'], zip(df_comuni['Latitude'], df_comuni['Longitude'])))

# Initialize Nominatim API
geolocator = Nominatim(user_agent="job_offer_geocoder")

# Cache for geocoded results
location_cache = {}

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

# Function to clean and extract comune name
def extract_comune(luogo):
    # Standard cleanup: remove province codes, parentheses, etc.
    luogo = luogo.split('(')[0].strip().lower()
    luogo = luogo.replace("comune di", "").replace("comune", "").strip()
    
    # Split by spaces to handle the description
    words = luogo.split()

    # If the description is short (3 words or fewer), return it as-is
    if len(words) <= 3:
        return luogo.title()

    # For longer descriptions, check each word to see if it matches a comune in the dictionary
    for word in words:
        if word.title() in comuni_dict:
            return word.title()
    
    # If no valid comune is found, return None
    return None

# Function to geocode a location using Nominatim API with caching
def geocode_address(address):
    if address in location_cache:
        return location_cache[address]
    
    try:
        location = geolocator.geocode(address, timeout=10)
        if location and is_within_emilia_romagna(location.latitude, location.longitude):
            location_cache[address] = (location.latitude, location.longitude)
            return (location.latitude, location.longitude)
        else:
            location_cache[address] = (None, None)
            return (None, None)
    except Exception as e:
        print(f"Error geocoding address '{address}': {e}")
        location_cache[address] = (None, None)
        return (None, None)

# Apply the cleaning and geocoding logic
def get_coordinates(luogo):
    comune = extract_comune(luogo)
    
    # Check if the comune is in the precomputed dictionary
    if comune in comuni_dict:
        lat, lon = comuni_dict[comune]
        if is_within_emilia_romagna(lat, lon):
            return lat, lon
        else:
            return (None, None)
    
    # If not found, fallback to geocoding
    if comune:
        latitude, longitude = geocode_address(comune)
        if latitude and longitude:
            return (latitude, longitude)
    
    # If still not found or no valid comune detected, return None
    return (None, None)

# Start timing the process
start_time = time.time()

# Initialize counters for monitoring
total_requests = 0
cache_hits = 0
dictionary_hits = 0
api_calls = 0

# Add Latitude and Longitude columns to the jobs DataFrame
latitudes = []
longitudes = []

for i, luogo in enumerate(df_jobs['Luogo di lavoro']):
    lat, lon = get_coordinates(luogo)
    latitudes.append(lat)
    longitudes.append(lon)
    
    # Update counters
    total_requests += 1
    if extract_comune(luogo) in comuni_dict:
        dictionary_hits += 1
    elif luogo in location_cache:
        cache_hits += 1
    else:
        api_calls += 1

    # Print progress every 500 entries
    if i % 500 == 0:
        print(f"Processed {i+1}/{len(df_jobs)} entries")
        print(f"Dictionary Hits: {dictionary_hits}, Cache Hits: {cache_hits}, API Calls: {api_calls}")

# Add the latitude and longitude to the dataframe
df_jobs.loc[:, 'Latitude'] = latitudes
df_jobs.loc[:, 'Longitude'] = longitudes

# End timing the process
end_time = time.time()
elapsed_time = end_time - start_time

# Save the updated dataset
df_jobs.to_csv("/Users/albertocicchetti/job_offers_geocoded_full.csv", index=False)  # Replace with your desired path

# Print summary of the process
print(f"Geocoding completed for {len(df_jobs)} job offers in {elapsed_time} seconds.")
print(f"Total Requests: {total_requests}, Dictionary Hits: {dictionary_hits}, Cache Hits: {cache_hits}, API Calls: {api_calls}")

# Load the geocoded dataset
df = pd.read_csv("/Users/albertocicchetti/job_offers_geocoded_full.csv")  # Replace with your actual path
# Check for missing values in the Latitude and Longitude columns
missing_values = df[df['Latitude'].isnull() | df['Longitude'].isnull()]

# Display the number of missing values
print(f"Number of missing values in Latitude and Longitude: {len(missing_values)}")

# Optionally, display the rows with missing values
print(missing_values)
