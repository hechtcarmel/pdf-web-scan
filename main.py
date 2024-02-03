import requests
import json
import logging
import asyncio
import aiohttp

# Constants
BASE_URL = "https://prod-usercontent.azureedge.net/Content/UserContent/Documents/"
RESULT_FILE = "valid_endpoints.json"
LOG_FILE = "crawler_log3.txt"
CHECKPOINT_FILE = "checkpoint.txt"
CONCURRENCY_LIMIT = 100
BATCH_SIZE = 100

# Setup logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(message)s', filemode='w')
stdout_handler = logging.StreamHandler()
stdout_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(message)s')
stdout_handler.setFormatter(formatter)
logging.getLogger().addHandler(stdout_handler)

# Function to save valid endpoints to a JSON file
def save_valid_endpoints(valid_endpoints):
    with open(RESULT_FILE, 'w') as json_file:
        json.dump(valid_endpoints, json_file, indent=4)

# Function to save the last processed number to the checkpoint file
def save_checkpoint(last_processed_number):
    with open(CHECKPOINT_FILE, 'w') as checkpoint_file:
        checkpoint_file.write(str(last_processed_number))

# Function to perform GET request and log results
async def crawl_and_log(url, session, results, semaphore):
    async with semaphore:
        try:
            async with session.head(url, timeout=30) as response:
                status_code = response.status
                if 200 <= status_code < 300:
                    logging.info(f"OK-{status_code}-{url}")
                    results.append(url)
                else:
                    logging.info(f"Failed-{status_code}-{url}")
        except Exception as e:
            logging.exception(f"Error-{url}: {str(e)}")

# Main asynchronous function to iterate through URLs and store valid ones in a JSON file
async def main():
    valid_endpoints = []
    tasks = []

    # Read the last processed number from the checkpoint file
    try:
        with open(CHECKPOINT_FILE, 'r') as checkpoint_file:
            last_processed_number = int(checkpoint_file.read().strip())
    except (FileNotFoundError, ValueError):
        last_processed_number = -1

    async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)

        for number in range(last_processed_number + 1, 1000000):
            six_digit_number = str(number).zfill(6)
            url = f"{BASE_URL}{six_digit_number}.pdf"
            task = asyncio.create_task(crawl_and_log(url, session, valid_endpoints, semaphore))
            tasks.append(task)

            if len(tasks) >= BATCH_SIZE:
                await asyncio.gather(*tasks)
                tasks = []
                save_valid_endpoints(valid_endpoints)
                save_checkpoint(number)

    # Final save (if any tasks were left uncompleted)
    if tasks:
        await asyncio.gather(*tasks)
    save_valid_endpoints(valid_endpoints)
    save_checkpoint(number)

if __name__ == "__main__":
    asyncio.run(main())
