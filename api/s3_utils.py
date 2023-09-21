import boto3
import os
import requests
import PyPDF2
import re
import logging

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    region_name=os.environ.get("AWS_REGION"),
)


def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename)


def update_files_in_s3(file_links, base_url, year_to_search):
    s3_bucket_name = os.environ.get("S3_BUCKET_NAME")

    # Get the list of existing files in the S3 bucket
    existing_files = []
    s3_objects = s3.list_objects_v2(Bucket=s3_bucket_name)
    if "Contents" in s3_objects:
        existing_files = [obj["Key"] for obj in s3_objects["Contents"]]

    # Loop through the file links and upload missing files to S3
    for link in file_links:
        try:
            file_url = link.get("href", "")
            last_part = file_url.split("\\")[-1]
            sanitized_name = sanitize_filename(last_part)

            # Check if the file already exists in the S3 bucket
            if sanitized_name not in existing_files:
                temp_file_path = f"/tmp/{sanitized_name}"
                with requests.get(file_url, stream=True) as r:
                    r.raise_for_status()
                    with open(temp_file_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)

                # Upload the file to the S3 bucket
                s3.upload_file(temp_file_path, s3_bucket_name, sanitized_name)
        except Exception as e:
            print(f"An error occurred: {e}")
            raise (e)


def search_name_in_pdf(s3_key, name_to_search):
    # Download the file from S3 to a temporary location
    s3_bucket_name = os.environ.get("S3_BUCKET_NAME")
    temp_file_path = f"/tmp/{s3_key}"
    s3.download_file(s3_bucket_name, s3_key, temp_file_path)

    # Open the temporary file and search for the name
    with open(temp_file_path, "rb") as pdf_stream:
        pdf_reader = PyPDF2.PdfReader(pdf_stream)
        num_pages = len(pdf_reader.pages)

        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            if name_to_search.lower() in text.lower():
                return True

    # Remove the temporary file if needed
    os.remove(temp_file_path)

    return False


def download_and_search_files(file_links, base_url, name_to_search, year_to_search):
    # Update the files in S3
    update_files_in_s3(file_links, base_url, year_to_search)
    # log how many file links to search
    name_found_files = []
    name_found_urls = []
    s3_bucket_name = os.environ.get("S3_BUCKET_NAME")
    for link in file_links:
        try:
            file_url = link.get("href", "")
            last_part = file_url.split("\\")[-1]
            sanitized_name = sanitize_filename(last_part)
            if search_name_in_pdf(sanitized_name, name_to_search):
                name_found_files.append(sanitized_name)
                name_found_urls.append(file_url)
        except Exception as e:
            print(f"An error occurred: {e}")

    return name_found_files, name_found_urls
