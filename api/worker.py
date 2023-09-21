import logging
from queue import Queue
import threading
from s3_utils import download_and_search_files
import requests
import os
from bs4 import BeautifulSoup
import resend
from enum import Enum

logging.basicConfig(level=logging.INFO)
task_queue = Queue()
resend.api_key = os.environ.get("RESEND_API_KEY")
base_url = os.environ.get("BASE_URL")


class GAZETTE_TYPE(Enum):
    EXTRAORDINARY = "extraordinary"
    OFFICIAL = "official"


def worker():
    while True:
        task = task_queue.get()
        if task is None:
            break

        name_to_search, year_to_search, email = task

        logging.log(
            logging.INFO,
            f"Worker is searching for {name_to_search} in {year_to_search}",
        )

        response = requests.get(base_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        file_links = soup.select(".mod-articles-category-introtext a")

        filtered_links = []

        for link in file_links:
            file_url = link.get("href", "")
            if (
                year_to_search in file_url
                and GAZETTE_TYPE.OFFICIAL.value in file_url.lower()
            ):
                filtered_links.append(link)

        name_found_files, name_found_urls = download_and_search_files(
            filtered_links, base_url, name_to_search, year_to_search
        )

        if len(name_found_files) > 0:
            logging.info(f"The name {name_to_search} was found in the following files:")
            for file in name_found_files:
                logging.info(file)

            # Send an email indicating that the name was found
            email_content = f"""
            <h1>Gazette Search GY</h1>
            <p>Hello,</p>
            <p>We are pleased to inform you that the name <strong>{name_to_search}</strong> was found in the following files:</p>
            <ul>
            """
            for url in name_found_urls:
                email_content += f"<li><a href='{url}'>{url}</a></li>"
            email_content += """
            </ul>
            <p>Thank you for using Gazette Search GY!</p>
            """

            r = resend.Emails.send(
                {
                    "from": os.environ.get("SENDER_EMAIL"),
                    "to": email,
                    "subject": "Name Found",
                    "html": email_content,
                },
            )
        else:
            logging.info(f"The name {name_to_search} was not found in any file.")

            # Send an email indicating that the name was not found
            email_content = f"""
            <h1>Gazette Search GY</h1>
            <p>Hello,</p>
            <p>We are pleased to inform you that the name <strong>{name_to_search}</strong> was not found in any file for the year {year_to_search}.</p>
            <p>Thank you for using Gazette Search GY!</p>
            """

            r = resend.Emails.send(
                {
                    "from": os.environ.get("SENDER_EMAIL"),
                    "to": email,
                    "subject": "Name Not Found",
                    "html": email_content,
                }
            )

        task_queue.task_done()


threading.Thread(target=worker).start()
