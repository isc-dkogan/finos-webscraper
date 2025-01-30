import time
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

def collect_browse_links(url):
    # Set up the WebDriver
    driver = setup_driver()
    driver.get(url)

    all_browse_links = []

    try:
        # Loop to go through all pages
        while True:
            # Wait for the "Browse" links to be present
            browse_links = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//a[@data-test='item-browse-link']"))
            )
            print(f"Found {len(browse_links)} 'Browse' links on this page.")

            # Collect all the 'Browse' links
            for link in browse_links:
                href = link.get_attribute('href')
                if href:
                    all_browse_links.append(href)
                    print(f"Added link: {href}")

            # After collecting the links, check for the "Next" page button
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='goto next page']"))
                )

                # Check if the "Next" button is enabled or disabled
                if "disabled" in next_button.get_attribute("class"):
                    print("No more pages to navigate.")
                    break  # Exit if there's no next page
                else:
                    print("Clicking on the 'Next' button to go to the next page.")
                    next_button.click()  # Click the "Next" button to go to the next page
                    time.sleep(2)  # Wait for the page to load

            except Exception as e:
                print(f"Error while trying to click the next page: {e}")
                break  # If there is an error or no next page, exit

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Close the driver after collecting all the links
        print(f"Collected {len(all_browse_links)} 'Browse' links.")
        driver.quit()

    return all_browse_links

def download_zip(driver, browse_link):
    driver.get(browse_link)
    time.sleep(2)  # Wait for the page to load

    try:
        # Get all the links in the file list that end with .zip
        file_links = driver.find_elements(By.XPATH, "//pre[@id='contents']//a[contains(@href, '.zip')]")

        if file_links:
            # Click on the first .zip link
            zip_link = file_links[0]
            href = zip_link.get_attribute('href')
            print(f"Downloading .zip file: {href}")
            driver.get(href)  # Click to download the .zip file
            time.sleep(3)  # Wait for download to start
        else:
            print("No .zip file found on this page.")
    except Exception as e:
        print(f"Error while trying to download .zip files: {e}")

def visit_browse_links(browse_links):
    # Set up the WebDriver
    driver = setup_driver()

    for idx, link in enumerate(browse_links, start=1):
        try:
            print(f"Visiting Browse link {idx}: {link}")
            download_zip(driver, link)

        except Exception as e:
            print(f"Error visiting {link}: {e}")

    # Close the driver after visiting all the links
    print("Finished downloading all 'Browse' links. Closing browser.")
    driver.quit()

if __name__ == "__main__":
    url = "https://central.sonatype.com/artifact/org.finos.cdm/cdm-json-schema/versions"

    # First, collect all the 'Browse' links
    browse_links = collect_browse_links(url)

    # Then, visit each of the collected links
    visit_browse_links(browse_links)
