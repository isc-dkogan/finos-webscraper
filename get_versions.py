import time
import csv
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--remote-allow-origins=*")  # Allow origins for ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

class VersionScraper:
    def __init__(self, url, csv_file="versions.csv"):
        """
        Initializes the scraper with the target URL and CSV file.

        :param url: The URL to scrape versions from.
        :param csv_file: The CSV file that contains the previously stored versions.
        """
        self.url = url
        self.csv_file = csv_file
        self.driver = setup_driver()
        self.versions = []  # List to hold scraped version strings

    def scrape_versions(self):
        """
        Loads the URL and iterates through all paginated pages,
        extracting version numbers from elements like:
        <div class="Versions_versionNumberCell__qW_RU" data-test="item-version">6.0.0-dev.96</div>
        """
        self.driver.get(self.url)
        while True:
            try:
                # Wait until the version elements are present on the page.
                version_elements = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//div[@data-test='item-version']"))
                )
                print(f"Found {len(version_elements)} version element(s) on this page.")

                # Extract text from each element and add it if not already in our list.
                for elem in version_elements:
                    version_text = elem.text.strip()
                    if version_text and version_text not in self.versions:
                        self.versions.append(version_text)
                        print(f"Added version: {version_text}")

                # Attempt to click the "Next" page button.
                next_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='goto next page']"))
                )
                # Check if the "Next" button is disabled (i.e., no more pages).
                if "disabled" in next_button.get_attribute("class"):
                    print("No more pages to navigate.")
                    break
                else:
                    print("Navigating to the next page.")
                    next_button.click()
                    time.sleep(2)  # Allow time for the next page to load.
            except Exception as e:
                # No more pages or an error occurred.
                print(f"Finished scraping or encountered an error: {e}")
                break

        self.driver.quit()
        return self.versions

    def compare_with_csv(self):
        """
        Reads versions from the CSV file and compares them with the scraped versions.
        Prints out any new versions (found on the website but not in CSV)
        and any missing versions (present in CSV but not scraped).
        """
        # Read versions from the CSV file.
        try:
            with open(self.csv_file, mode='r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                csv_versions = []
                # Skip header row.
                next(reader, None)
                for row in reader:
                    if row:
                        csv_versions.append(row[0].strip())
            print(f"Found {len(csv_versions)} version(s) in CSV file '{self.csv_file}'.")
        except FileNotFoundError:
            print(f"CSV file '{self.csv_file}' not found. Assuming no existing versions.")
            csv_versions = []
        except Exception as e:
            print(f"Error reading CSV file '{self.csv_file}': {e}")
            csv_versions = []

        # Convert lists to sets for comparison.
        scraped_set = set(self.versions)
        csv_set = set(csv_versions)

        # Determine new and missing versions.
        new_versions = scraped_set - csv_set
        missing_versions = csv_set - scraped_set

        if new_versions:
            print("\nNew versions found (present in scraped data but not in CSV):")
            for version in sorted(new_versions):
                print(f"  - {version}")
        else:
            print("\nNo new versions found compared to CSV.")

        if missing_versions:
            print("\nVersions missing (present in CSV but not in scraped data):")
            for version in sorted(missing_versions):
                print(f"  - {version}")
        else:
            print("\nNo versions are missing compared to CSV.")

        if not new_versions and not missing_versions:
            print("\nThe scraped versions and CSV versions are identical.")

    def run(self):
        """
        Runs the scraping process and then compares the scraped versions with the CSV file.
        """
        print("Starting version scraping...")
        self.scrape_versions()
        print("\nScraping complete. Now comparing with CSV file...")
        self.compare_with_csv()

if __name__ == "__main__":
    url = "https://central.sonatype.com/artifact/org.finos.cdm/cdm-json-schema/versions"
    scraper = VersionScraper(url)
    scraper.run()