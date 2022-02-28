import httpx
import os
import json
import random
from async_lru import alru_cache


async def module(word = ["", None]):
    try:
        result = await without_id(word[1])
    except ReadTimeout:
        return ["Timeout"]

    return result

@alru_cache(maxsize=30)
async def without_id(word):
    token = os.environ['GOOGLE_KEY']
    start_page = str(random.randint(1,30))
    query = [word, "cat"][word == None]
    link = "https://customsearch.googleapis.com/customsearch/" +\
           f"v1?searchType=image&key={ token }&q={ query }" +\
           f"&num=1&start={ start_page }"
    request = (await httpx.AsyncClient().get(link, timeout=10.0)).json()
    if "items" in request.keys():
        return [request["items"][0]["link"], True]
    return ["Nothing's finded"]
