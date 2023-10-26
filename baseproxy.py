import os
import json
import time
import csv

from dotenv import load_dotenv
from browsermobproxy import Server
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from tqdm import tqdm
load_dotenv()


MAX_TIME_WAIT = 10
BROWSERMOB_PATH = os.getenv('BROWSERMOB_PATH', default=None)
CHROMEDRIVER_PATH = os.getenv('CHROMEDRIVER_PATH', default=None)

if not BROWSERMOB_PATH:
    print('BROWSERMOB_PATH is required')
    exit(1)


if not CHROMEDRIVER_PATH:
    print('CHROMEDRIVER_PATH is required')
    exit(1)


def get_headers():
    return [
        'pdpUrlType', 'propertyType', 'location', 'personCapacity', 'reviewCount', 'starRating', 'listingId', 'listingLat', 'listingLng',
        'homeTier', 'roomType', 'pictureCount', 'accuracyRating', 'checkinRating', 'cleanlinessRating',
        'communicationRating', 'locationRating', 'valueRating', 'guestSatisfactionOverall', 'visibleReviewCount', 'namenities',
        'price', 'total_amenities', 'amenities'
    ]



def parse_json_structure(data):
    """Take the JSON response for StaysPdpSections url to get some data"""

    row_parsed = []
    metadata = data['data']['presentation']['stayProductDetailPage']['sections']['metadata']
    row_parsed.append(
        metadata.get('pdpUrlType', 0) # "pdpUrlType":"ROOMS",
    )
    # sharingConfig
    row_parsed.append(
        metadata['sharingConfig'].get('propertyType', 0) # "propertyType":"Entire home",
    )
    row_parsed.append(
        metadata['sharingConfig'].get('location', 0) # "propertyType":"Yanahuara",
    )
    row_parsed.append(
        metadata['sharingConfig'].get('personCapacity', 0) # "personCapacity":12,
    )
    row_parsed.append(
        metadata['sharingConfig'].get('reviewCount', 0) # "reviewCount":34,
    )
    row_parsed.append(
        metadata['sharingConfig'].get('starRating', 0) # "starRating":4.68
    )

    # loggingContext['eventDataLogging]
    row_parsed.append(
        metadata['loggingContext']['eventDataLogging'].get('listingId', 0) #  "listingId":"744448169774736865",
    )
    row_parsed.append(
        metadata['loggingContext']['eventDataLogging'].get('listingLat', 0) #  "listingLat":-16.38535,
    )
    row_parsed.append(
        metadata['loggingContext']['eventDataLogging'].get('listingLng', 0) #  "listingLng":-71.5398,
    )
    row_parsed.append(
        metadata['loggingContext']['eventDataLogging'].get('homeTier', 0) #  "homeTier":1,
    )
    row_parsed.append(
        metadata['loggingContext']['eventDataLogging'].get('roomType', 0) # "roomType":"Entire home/apt",
    )
    row_parsed.append(
        metadata['loggingContext']['eventDataLogging'].get('pictureCount', 0) # "pictureCount":43,
    )
    row_parsed.append(
        metadata['loggingContext']['eventDataLogging'].get('accuracyRating', 0) # "accuracyRating":4.68,
    )
    row_parsed.append(
        metadata['loggingContext']['eventDataLogging'].get('checkinRating', 0) # "checkinRating":4.88,
    )
    row_parsed.append(
        metadata['loggingContext']['eventDataLogging'].get('cleanlinessRating', 0) # "cleanlinessRating":4.53,
    )
    row_parsed.append(
        metadata['loggingContext']['eventDataLogging'].get('communicationRating', 0) # "communicationRating":4.85,
    )
    row_parsed.append(
        metadata['loggingContext']['eventDataLogging'].get('locationRating', 0) # "locationRating":4.88,
    )
    row_parsed.append(
        metadata['loggingContext']['eventDataLogging'].get('valueRating', 0) # "valueRating":4.65,
    )
    row_parsed.append(
        metadata['loggingContext']['eventDataLogging'].get('guestSatisfactionOverall', 0) # "guestSatisfactionOverall":4.68,
    )
    row_parsed.append(
        metadata['loggingContext']['eventDataLogging'].get('visibleReviewCount', 0) # "visibleReviewCount":"34"
    )
    row_parsed.append(
        len(metadata['loggingContext']['eventDataLogging']['amenities']) # "amenities": []
    )

    sections = data['data']['presentation']['stayProductDetailPage']['sections']['sections']
    for section in sections:
        if section.get('section', None): 
            if section['section'].get('structuredDisplayPrice', None):
                price = section['section']['structuredDisplayPrice']['primaryLine'].get('price', 0) # "price":"S/280",
                if price is None:
                    price = section['section']['structuredDisplayPrice']['primaryLine'].get('originalPrice', 0) # "originalPrice":"S/97", "discountedPrice":"S/87",
                row_parsed.append(price)
                break
    # row_parsed.append(
    #     sections[0]['section'].get('petsAllowed', None) # "petsAllowed":true,
    # )
    return row_parsed


server = Server(BROWSERMOB_PATH)
server.start()
proxy = server.create_proxy(params={'trustAllServers':'true'})
database = []
database.append(get_headers())
# proxy.new_har(options={'captureContent': True})

option = webdriver.ChromeOptions()
option.add_argument("--window-size=1920,1080")
option.add_argument('--ignore-certificate-errors')
option.add_argument("--headless")
option.add_argument('--proxy-server=%s' % proxy.proxy)
service = Service(executable_path=CHROMEDRIVER_PATH)
browser = webdriver.Chrome(service=service, options=option)
proxy.new_har(options={'captureHeaders': True, 'captureContent': True, 'captureBinaryContent': True})

continue_scraping = True
next_xpath = "//a[@aria-label='Next']"
base_div = '//*[@id="site-content"]/div/div[2]/div/div/div/div/div[1]/div'
link_div = '/div/div[2]/div/div/div/div/a'

# browser.get("https://www.airbnb.com/s/Arequipa--Peru/homes")
# browser.get('https://www.airbnb.com/s/Cerro-Colorado--Arequipa--Peru/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2023-11-01&monthly_length=3&price_filter_input_type=0&price_filter_num_nights=3&channel=EXPLORE&query=Cerro%20Colorado%2C%20Arequipa&date_picker_type=calendar&checkin=2023-11-13&checkout=2023-11-16&source=structured_search_input_header&search_type=user_map_move&zoom_level=15.229714687670123&place_id=ChIJtWT8JAw2QpER_-Scas3UB2Y&ne_lat=-16.366922141506357&ne_lng=-71.55483784171383&sw_lat=-16.407792036589974&sw_lng=-71.60095177152255&zoom=15.229714687670123&search_by_map=true')
browser.get('https://www.airbnb.com/s/Jacobo-Hunter--Arequipa--Peru/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2023-11-01&monthly_length=3&price_filter_input_type=0&price_filter_num_nights=5&channel=EXPLORE&query=Jacobo%20Hunter%2C%20Arequipa&place_id=ChIJRyRrc6tKQpERSXUjC4fenis&date_picker_type=calendar&source=structured_search_input_header&search_type=filter_change&ne_lat=-16.42857697915527&ne_lng=-71.56113968482674&sw_lat=-16.462285150218907&sw_lng=-71.59918183768528&zoom=15.508462953795625&zoom_level=15&search_by_map=true&checkin=2023-12-10&checkout=2023-12-12')


pages_counter = 1
error_counts = 0

while continue_scraping:
    time.sleep(1)
    
    print('PAGE NUMBER:', pages_counter)
    elements = browser.find_elements("xpath", base_div)
    for item in tqdm(range(len(elements))):
        parsed = []
        wait = WebDriverWait(browser, MAX_TIME_WAIT)
        try:
            path_link = base_div + '[' + str(item+1) + ']' + link_div
            element = wait.until(EC.presence_of_element_located((By.XPATH, path_link)))
            browser.execute_script("arguments[0].click();", element)

        except TimeoutException:
            error_counts += 1
            continue

        time.sleep(3)
        window_handles = browser.window_handles
        browser.switch_to.window(window_handles[-1])
        no_base_data = False
        for e in proxy.har['log']['entries']:
            if 'StaysPdpSections' in e['request']['url']:
                try:
                    response = json.loads(e['response']['content'].get('text'))
                    parsed = parse_json_structure(response)
                except Exception as excep:
                    no_base_data = True
                    print('error:', str(excep))

        if no_base_data:
            error_counts += 1
            browser.close()
            browser.switch_to.window(window_handles[0])
            continue
        
        wait = WebDriverWait(browser, 2)
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, "//h1[text()='Translation on']")))
            close_button = browser.find_element("xpath", "//button[@aria-label='Close']")
            # browser.execute_script("arguments[0].click();", close_button)
            close_button.click()
            time.sleep(2)
        except TimeoutException:
            pass

        # Get amenities
        try:
            path_button = "//button[@type='button' and contains(text(), 'amenities')]"
            modal_button = wait.until(EC.presence_of_element_located((By.XPATH, path_button)))
            modal_button.click()
            time.sleep(2)

            amenities_divs = browser.find_elements("xpath", "//*[contains(@id, 'pdp_v3_')]/div/div[2]/div[1]")
            amenities = []
            for amnd in amenities_divs:
                amenities.append(amnd.text)

            parsed.append(len(amenities))
            parsed.append(amenities)
            database.append(parsed)
        except Exception as excep:
            parsed.append(0)
            parsed.append([])
            database.append(parsed)
        
        browser.close()
        browser.switch_to.window(window_handles[0])
        
    pagination_next = browser.find_elements("xpath", next_xpath)

    print(pagination_next)
    if len(pagination_next) == 0:
        continue_scraping = False
    else:
        print('loading new page')
        pagination_next[0].click()

    pages_counter += 1

print('---------------------------')
print('Error counts:', error_counts)

server.stop()
browser.quit()



csv_file = "firt_search.csv"

# Write data to the CSV file with ';' as the delimiter
with open(csv_file, "w", newline="") as file:
    writer = csv.writer(file, delimiter=";")
    writer.writerows(database)

print(f"CSV file '{csv_file}' has been created with ';' as the delimiter.")