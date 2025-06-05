import os
import zipfile
from io import BytesIO
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BTH_CITIES = [
    "Beijing",
    "Tianjin",
    "Shijiazhuang", "Tangshan", "Qinhuangdao", "Handan", "Xingtai",
    "Baoding", "Zhangjiakou", "Chengde", "Cangzhou", "Langfang",
    "Hengshui"
]

# Latest CEADs city-level emissions data (1997-2019)
BASE_URL = "https://www.ceads.net"
CITY_PAGE = f"{BASE_URL}/data/city/"


def get_latest_dataset_url() -> str:
    """Scrape CEADs city data page and return the first zip link."""
    print(f"Fetching dataset list from {CITY_PAGE}...")
    resp = requests.get(CITY_PAGE)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    for a in soup.select("a[href]"):
        href = a.get("href", "")
        if "city_CO2" in href and href.lower().endswith(".zip"):
            return urljoin(BASE_URL, href)
    raise RuntimeError("Could not find dataset URL on page")



def download_dataset(url: str) -> BytesIO:
    """Download dataset and return bytes buffer."""
    print(f"Downloading data from {url}...")
    resp = requests.get(url)
    resp.raise_for_status()
    return BytesIO(resp.content)


def load_city_data(zipped_data: BytesIO) -> pd.DataFrame:
    """Load city emissions data from zipped csv."""
    with zipfile.ZipFile(zipped_data) as zf:
        # assumes there is only one csv in the zip
        for name in zf.namelist():
            if name.lower().endswith('.csv'):
                with zf.open(name) as f:
                    df = pd.read_csv(f)
                break
        else:
            raise ValueError("No CSV file found in zip archive")
    return df


def filter_bth_last_decade(df: pd.DataFrame) -> pd.DataFrame:
    """Filter for BTH cities and last 10 years."""
    current_year = pd.Timestamp.now().year
    decade_start = current_year - 10
    mask_city = df['City'].isin(BTH_CITIES)
    mask_year = df['Year'] >= decade_start
    return df.loc[mask_city & mask_year]


def main():
    try:
        data_url = get_latest_dataset_url()
    except Exception as e:
        print(f"Warning: failed to scrape latest dataset URL ({e}). Falling back to default.")
        data_url = f"{BASE_URL}/data/CEADs_city_CO2_1997-2019_v2022.zip"

    zip_buffer = download_dataset(data_url)
    df = load_city_data(zip_buffer)
    result = filter_bth_last_decade(df)
    result.to_csv('bth_emissions_last_decade.csv', index=False)
    print('Saved filtered data to bth_emissions_last_decade.csv')


if __name__ == '__main__':
    main()
