import aiohttp
import asyncio
import json
import os
from requests.exceptions import HTTPError
import time
start_time = time.time()

from aiohttp import ClientSession


GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes?q=isbn:"
LIST_ISBN = [
    '9780002005883',
    '9780002238304',
    '9780002261982',
    '9780006163831',
    '9780006178736',
    '9780006280897',
    '9780006280934',
    '9780006353287',
    '9780006380832',
    '9780006470229',
]


BOOKS = []

class Book():
    def __init__(self, isbn):
        self.isbn = isbn

    def __str__(self):
        return self.isbn

    def add_data(self, d):
        self.data = d

    def read(self):
        return self.isbn, self.data

def extract_fields_from_response(response):
    """Extract fields from API's response"""
    item = response.get("items", [{}])[0]
    volume_info = item.get("volumeInfo", {})
    title = volume_info.get("title", None)
    subtitle = volume_info.get("subtitle", None)
    description = volume_info.get("description", None)
    published_date = volume_info.get("publishedDate", None)
    return (
        title,
        subtitle,
        description,
        published_date,
    )


async def get_book_details_async(isbn, session):
    """Get book details using Google Books API (asynchronously)"""
    url = GOOGLE_BOOKS_URL + isbn
    try:
        response = await session.request(method='GET', url=url)
        response.raise_for_status()
        print(f"Response status ({url}): {response.status}")
    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error ocurred: {err}")
    response_json = await response.json()
    return response_json


async def run_program(isbn, session):
    """Wrapper for running program in an asynchronous manner"""
    BOOKS.append(Book(isbn))
    try:
        response = await get_book_details_async(isbn, session)
        parsed_response = extract_fields_from_response(response)
        [b.add_data(parsed_response) for b in BOOKS if getattr(b, "isbn") == isbn]
        print(f"Response: {json.dumps(parsed_response, indent=2)}")
    except Exception as err:
        print(f"Exception occured: {err}")
        pass

async def run():
    async with ClientSession() as session:
        await asyncio.gather(*[run_program(isbn, session) for isbn in LIST_ISBN])

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
    for b in BOOKS:
        print(b.read())


if __name__ == '__main__':
    main()

print("--- %s seconds ---" % (time.time() - start_time))