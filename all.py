import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin  # Add this import statement
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

def download_assets_with_selenium(url, output_folder):
    # Set up Selenium options to run in headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")

    # Create a Service object with the path to your Chromedriver executable
    chromedriver_path = 'chromedriver_win32 (1)\chromedriver.exe'
    service = Service(executable_path=chromedriver_path)

    # Use the Service object to create the Chrome WebDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Open the webpage in the headless browser
        driver.get(url)

        # Give some time for the JavaScript on the page to execute
        time.sleep(5)  # Adjust this wait time as needed

        # Get the network requests made by the page
        requests = driver.execute_script("return performance.getEntriesByType('resource');")

        # Download the assets from the network requests
        for request in requests:
            asset_url = request['name']
            if asset_url.endswith(".js") or asset_url.endswith(".css"):
                download_file(asset_url, output_folder)

        # Extract HTML file URLs from the webpage
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        html_urls = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith(".html")]

        # Download and save each HTML file
        for html_url in html_urls:
            html_url = urljoin(url, html_url)  # Fix: Add urljoin to join base url with relative url
            download_file(html_url, output_folder)

        print("Assets and HTML files downloaded and saved successfully.")
    except Exception as e:
        print(f"Failed to download assets and HTML files: {e}")
    finally:
        # Close the headless browser
        driver.quit()

def download_file(url, output_folder):
    try:
        response = requests.get(url)
        response.raise_for_status()

        # Get the filename from the URL and join it with the output folder path
        filename = os.path.join(output_folder, os.path.basename(url))

        # Save the content of the file to the specified output folder
        with open(filename, 'wb') as file:
            file.write(response.content)

        print(f"Downloaded: {url}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {url}: {e}")
    except OSError as e:
        print(f"Failed to save {url}: {e}")

if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=AiFqApeurqI"  # Replace with the URL of the webpage you want to access
    output_folder = "output"  # Choose a folder name where you want to save the downloaded files
    os.makedirs(output_folder, exist_ok=True)

    download_assets_with_selenium(url, output_folder)
