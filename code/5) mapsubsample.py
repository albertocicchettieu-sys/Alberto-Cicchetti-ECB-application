#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 29 03:18:24 2024

@author: albertocicchetti
"""

import pandas as pd
import folium

# Load the dataset
df = pd.read_csv("/Users/albertocicchetti/job_offers_geocoded_full.csv")  # Replace with your actual path

# Drop rows with missing latitude or longitude
df_cleaned = df.dropna(subset=['Latitude', 'Longitude'])

# Take a sample of the data 
df_sample = df_cleaned.sample(n=4000, random_state=42)

# Check if the sample is not empty
print(f"Number of valid locations in sample: {len(df_sample)}")

if len(df_sample) == 0:
    print("No valid locations found in the sample. Exiting.")
else:
    # Create a map centered around Emilia-Romagna
    m = folium.Map(location=[44.4949, 11.3426], zoom_start=8)

    # Add markers to the map
    for _, row in df_sample.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"Job Title: {row['Title']}\nLocation: {row['Luogo di lavoro']}",
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)

    # Save the map as an HTML file
    m.save("/Users/albertocicchetti/job_offers_map_sample.html")  # Replace with your desired output path

    print("Map has been generated and saved as 'job_offers_map_sample.html'.")
