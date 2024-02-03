import requests
import json
import logging
import sys

# Setup logging to write actions to a log file and stdout
logging.basicConfig(filename='crawler_log.txt', level=logging.INFO,
                    format='%(message)s', filemode='w')
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(message)s')
stdout_handler.setFormatter(formatter)
logging.getLogger().addHandler(stdout_handler)

# Function to perform GET request and log results
def crawl_and_log(url, num):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            logging.info(f"OK-{response.status_code}-{num}")
            return url
        else:
            logging.info(f"Failed{response.status_code}-{url}")
    except Exception as e:
        logging.error(f"Error-{num}: {str(e)}")
    return None

# Main function to iterate through URLs and store valid ones in a JSON file
def main():
    base_url = "https://prod-usercontent.azureedge.net/Content/UserContent/Documents/"
    result_file = "valid_endpoints.json"
    valid_endpoints = []

    for number in range(1000000):
        six_digit_number = str(number).zfill(6)
        url = f"{base_url}{six_digit_number}.pdf"

        valid_url = crawl_and_log(url, number)

        if valid_url:
            valid_endpoints.append(valid_url)

    # Save valid endpoints to a JSON file
    with open(result_file, 'w') as json_file:
        json.dump(valid_endpoints, json_file, indent=4)

if __name__ == "__main__":
    main()
