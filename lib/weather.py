import httpx
import os
import json


async def module(sity):
    if sity == None:
        sity = "Moscow"
    key = os.environ["WEATHER_KEY"]
    link = f"https://api.openweathermap.org/data/2.5/find?q={ sity }&appid={ key }"
    request = (await httpx.AsyncClient().get(link)).json()
    data = ""
    if len(request.get("list",""))>0:
        for i in request["list"][0].keys():
            data += f"{ i } - { request['list'][0][i] }\n"
        return [data]
    return ["Nothing's finded"]
