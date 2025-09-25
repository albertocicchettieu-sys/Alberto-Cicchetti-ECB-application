#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 13:09:59 2024

@author: albertocicchetti
"""


import requests
import random
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from requests.adapters import HTTPAdapter, Retry

# List of user agents to rotate
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.2 Safari/605.1.15",
]

# Function to generate job offer URLs
def generate_urls(start_num, end_num):
    base_url = "https://lavoroperte.regione.emilia-romagna.it/welcomepage/vacancy/view/"
    return [f"{base_url}{i}" for i in range(start_num, end_num + 1)]

# Function to scrape job offer details
def scrape_job_offer(url, session):
    headers = {
        "User-Agent": random.choice(user_agents)
    }

    try:
        response = session.get(url, timeout=60, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        
        job_data = {}
        
        # Extract the job title
        title_section = soup.find("h3", class_="white-heading uppercase")
        job_data['Title'] = title_section.get_text(strip=True) if title_section else None
        
        # Extract the Rif. offerta number
        rif_offerta = soup.find("div", class_="right-heading pull-right")
        job_data['Rif. Offerta'] = rif_offerta.get_text(strip=True).replace("Rif. offerta", "").strip() if rif_offerta else None
        
        # Extract the description
        description_section = soup.find("p", class_="job-description")
        job_data['Description'] = description_section.get_text(strip=True) if description_section else None
        
        # Extract the grey highlighted fields (e.g., Qualifica ISTAT, Contratto, Luogo di lavoro, etc.)
        grey_section = soup.find("div", class_="job-info m-t-50 m-b-50")
        if (grey_section):
            rows = grey_section.find_all("div", class_="row")
            for row in rows:
                label_element = row.find("div", class_="col-md-4").find("span")
                value_element = row.find("div", class_="col-md-8")
                
                if label_element and value_element:
                    label = label_element.get_text(strip=True)
                    
                    # Special case for "Conoscenze linguistiche"
                    if label == "Conoscenze linguistiche":
                        language_sections = value_element.find_all("span", recursive=False)
                        language_details = []
                        for language_section in language_sections:
                            language_name = language_section.find("strong").get_text(strip=True)
                            skills = language_section.find_all("li")
                            skill_details = "; ".join([skill.get_text(strip=True) for skill in skills])
                            language_details.append(f"{language_name}: {skill_details}")
                        job_data[label] = "; ".join(language_details)
                    
                    # Special case for "Esperienza richiesta"
                    elif label == "Esperienza richiesta":
                        spans = value_element.find_all("span")
                        experience_value = spans[-1].get_text(strip=True) if spans else None
                        job_data[label] = experience_value
                    
                    else:
                        value = value_element.get_text(strip=True)
                        # Handle duplicate labels by choosing the longest one
                        if label in job_data:
                            if len(value) > len(job_data[label]):
                                job_data[label] = value
                        else:
                            job_data[label] = value
        
        # Extract "Titolo di studio"
        titolo_di_studio = soup.find("h4", class_="m-t-50 inner-title", string="Titolo di studio")
        if titolo_di_studio:
            titolo_di_studio_value = titolo_di_studio.find_next("p", class_="inner-desc").get_text(strip=True)
            job_data["Titolo di studio"] = titolo_di_studio_value
        
        # Extract "Patenti"
        patenti = soup.find("h4", class_="m-t-50 inner-title", string="Patenti")
        if patenti:
            patenti_value = patenti.find_next("ul").get_text(strip=True)
            job_data["Patenti"] = patenti_value
        
        # Extract "Sintesi" section
        sintesi_section = soup.find("dl", class_="info-dl")
        if sintesi_section:
            sintesi_items = sintesi_section.find_all("dt")
            for item in sintesi_items:
                label = item.get_text(strip=True)
                value_element = item.find_next("dd")

                if label and value_element:
                    # Special handling for "Requisiti" since it might be a list
                    if label == "Requisiti":
                        requisiti_list = value_element.find_all("li")
                        requisiti = "; ".join([req.get_text(strip=True) for req in requisiti_list])
                        job_data[label] = requisiti
                    else:
                        value = value_element.get_text(strip=True)
                        # Handle duplicate labels by choosing the longest one
                        if label in job_data:
                            if len(value) > len(job_data[label]):
                                job_data[label] = value
                        else:
                            job_data[label] = value
        
        # Extract "Company Card" information
        company_card = soup.find("div", class_="company-card-data")
        if company_card:
            company_items = company_card.find_all("dt")
            for item in company_items:
                label = item.get_text(strip=True)
                value_element = item.find_next("dd")
                
                if label and value_element:
                    value = value_element.get_text(strip=True)
                    # Handle duplicate labels by choosing the longest one
                    if label in job_data:
                        if len(value) > len(job_data[label]):
                            job_data[label] = value
                    else:
                        job_data[label] = value

        # Extract "Job Overview" section
        job_overview_section = soup.find("div", class_="job-overview-sec m-b-50")
        if job_overview_section:
            overview_items = job_overview_section.find_all("li")
            for item in overview_items:
                label_element = item.find("span")
                value_element = item.find("p")
                
                if label_element and value_element:
                    label = label_element.get_text(strip=True)
                    
                    if label == "Data di pubblicazione":
                        time_element = value_element.find("time")
                        if time_element:
                            # Extract the date part only and reformat it
                            date_str = time_element.get("datetime", "").strip().split("T")[0]
                            job_data["Data di pubblicazione"] = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d-%m-%Y")
                        else:
                            job_data["Data di pubblicazione"] = value_element.get_text(strip=True)
                    elif label == "Scade il":
                        # Strip extra spaces and parentheses
                        job_data["Scade il"] = value_element.get_text(strip=True).replace("(", "").replace(")", "").strip()
                    else:
                        value = value_element.get_text(strip=True)
                        # Handle duplicate labels by choosing the longest one
                        if label in job_data:
                            if len(value) > len(job_data[label]):
                                job_data[label] = value
                        else:
                            job_data[label] = value

        return job_data
    
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

# Parallel processing of URLs
def process_urls_in_parallel(urls, num_workers=8):
    session = requests.Session()
    retries = Retry(total=10, backoff_factor=2, status_forcelist=[500, 502, 503, 504], 
                    allowed_methods=["HEAD", "GET", "OPTIONS"], raise_on_status=False)
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('https://', adapter)
    session.mount('http://', adapter)

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        results = list(executor.map(lambda url: scrape_job_offer(url, session), urls))
    
    return [result for result in results if result is not None]

# Generate URLs for testing
urls_to_check = generate_urls(430000, 493999)  # Checking URLs from 430000 to 434999

# Run the URL check and data extraction in parallel
extracted_data = process_urls_in_parallel(urls_to_check, num_workers=8)

# Convert to DataFrame
df = pd.DataFrame(extracted_data)

# Remove rows where all elements are None or NaN
df_cleaned = df.dropna(how='all')

print(df_cleaned)

# Save to CSV
df_cleaned.to_csv("job_offers_tot.csv", index=False)
