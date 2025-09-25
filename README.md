# Job Scraping Emilia-Romagna

This repository contains a set of Python scripts developed as a final project for a university course.  
The project focuses on scraping job vacancies from the official portal of the *Agenzia del Lavoro* in Emilia-Romagna (NUTS2 Italian region), processing the data, and visualising the spatial distribution of vacancies on an interactive map.

## Workflow

The repository includes five scripts, to be used in sequence:

1. **Web scraping**  
   - Collects job postings from the portal.  
2. **Dictionary of municipalities**  
   - Builds a reference dictionary of Emilia-Romagna municipalities.  
   - Provides the basis for linking postings to specific locations.  
3. **Merge with main dataset**  
   - Integrates the municipality dictionary with the scraped dataset.  
   - Produces a structured dataset where vacancies are linked to local units.  
4. **Map plotting (part I)**  
   - Generates a first version of an interactive map.  
5. **Map plotting (part II)**  
   - Produces an improved/alternative visualisation of the vacancies.  
