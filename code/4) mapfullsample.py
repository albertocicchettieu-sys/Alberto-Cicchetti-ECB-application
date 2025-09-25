#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 12:54:30 2024

@author: albertocicchetti
"""

import pandas as pd
import folium
from folium.plugins import MarkerCluster
import numpy as np

# Load the geocoded dataset
df = pd.read_csv("/Users/albertocicchetti/job_offers_geocoded_full.csv")

# Filter out rows with missing or invalid coordinates
df = df.dropna(subset=['Latitude', 'Longitude'])

# Create a map centered around Emilia-Romagna (adjust the coordinates as needed)
map_center = [44.4949, 11.3426]  # Centered on Bologna, Emilia-Romagna
mymap = folium.Map(location=map_center, zoom_start=8)

# Create a marker cluster
marker_cluster = MarkerCluster().add_to(mymap)

# Add markers to the cluster with a slightly larger random offset
for idx, row in df.iterrows():
    # Apply a larger random offset to each marker to prevent overlap
    offset_lat = np.random.uniform(-0.0005, 0.0005)  # Increased offset
    offset_lon = np.random.uniform(-0.0005, 0.0005)  # Increased offset
    
    lat = row['Latitude'] + offset_lat
    lon = row['Longitude'] + offset_lon
    
    folium.Marker(
        location=[lat, lon],
        popup=f"Title: {row['Title']}\nLocation: {row['Luogo di lavoro']}",  # Adjust based on your actual column names
    ).add_to(marker_cluster)

# Save the map as an HTML file
mymap.save("/Users/albertocicchetti/job_offers_map_clustered_offset.html")

print("Map has been generated and saved as 'job_offers_map_clustered_offset.html'.")
