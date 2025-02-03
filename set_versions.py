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
    def __init__(self, url, output_csv="versions.csv"):
        """
        Initializes the scraper with the target URL and output CSV file name.
        """
        self.url = url
        self.output_csv = output_csv
        self.driver = setup_driver()
        self.versions = []  # List to hold version strings

    def scrape_versions(self):
        """
        Loads the URL and iterates through all paginated pages,
        extracting version numbers from elements like:
            <div class="Versions_versionNumberCell__qW_RU" data-test="item-version">6.0.0-dev.96</div>
        """
        self.driver.get(self.url)
        while True:
            try:
                # Wait until the version elements are present on the page
                version_elements = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//div[@data-test='item-version']"))
                )
                print(f"Found {len(version_elements)} version elements on this page.")

                # Extract text from each version element and add it to the list if not already present
                for elem in version_elements:
                    version_text = elem.text.strip()
                    if version_text and version_text not in self.versions:
                        self.versions.append(version_text)
                        print(f"Added version: {version_text}")

                # Attempt to click the "Next" page button
                next_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='goto next page']"))
                )
                # Check if the "Next" button is disabled (i.e., no more pages)
                if "disabled" in next_button.get_attribute("class"):
                    print("No more pages to navigate.")
                    break
                else:
                    print("Navigating to the next page.")
                    next_button.click()
                    time.sleep(2)  # Pause briefly to allow the next page to load

            except Exception as e:
                # Either there are no more pages or an error occurred.
                print(f"Finished or encountered an error: {e}")
                break

        # Quit the driver after scraping is complete
        self.driver.quit()
        return self.versions

    def write_versions_to_csv(self):
        """
        Writes the list of version strings to a CSV file.
        """
        try:
            with open(self.output_csv, mode='w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Version"])  # Write header row
                for version in self.versions:
                    writer.writerow([version])
            print(f"Successfully wrote {len(self.versions)} version(s) to '{self.output_csv}'.")
        except Exception as e:
            print(f"An error occurred while writing to CSV: {e}")

    def run(self):
        """
        Runs the full scraping process and writes the results to a CSV file.
        """
        self.scrape_versions()
        self.write_versions_to_csv()

if __name__ == "__main__":
    url = "https://central.sonatype.com/artifact/org.finos.cdm/cdm-json-schema/versions"
    scraper = VersionScraper(url)
    scraper.run()
