# Claire

This repository contains a simple web-based game and a Python script for scraping city-level carbon emission data.

## Scripts

- `bth_emission_scraper.py`: Scrapes the CEADs city data page for the latest dataset link, downloads it (falling back to a known URL if scraping fails), filters for Beijing–Tianjin–Hebei cities over the last ten years, and saves the result to `bth_emissions_last_decade.csv`.
