"""
The Main File
"""

import asyncio
import aiohttp


print("What is the vocadb artist id?\nEx: 100054 -> https://vocadb.net/Ar/100054")
ARTIST_ID = input()
print("how many results do you want? (Leave empty for 100)")
MAX_RESULTS = input()
if not MAX_RESULTS:
    MAX_RESULTS = 100

url = (
    "https://vocadb.net/api/songs"
    "?start=0&"
    "getTotalCount=true"
    f"&maxResults={MAX_RESULTS}"
    "&fields=AdditionalNames%2CMainPicture"
    "&lang=Default&nameMatchMode=Auto"
    "&sort=Name"
    "&childTags=false"
    f"&artistId%5B%5D={ARTIST_ID}"
    "&artistParticipationStatus=Everything"
    "&onlyWithPvs=false"
)
yt_links = []
nico_links = []


async def get_songs():
    "Gets list of songs through vocadb given the artist id"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            json_dict = await resp.json()
    songs = json_dict["items"]
    song_id_list = [song["id"] for song in songs]
    tasks = [get_url(i) for i in song_id_list]
    await asyncio.gather(*tasks)
    nl = "\n"
    print(f"YT URLS:\n{nl.join(yt_links)}")
    print(f"NICO URLS:\n{nl.join(nico_links)}")


async def get_url(song_id):
    "Gives the youtube url or niconico url of a song id"
    song_api_url = f"https://vocadb.net/api/songs/{song_id}/details"
    async with aiohttp.ClientSession() as session:
        async with session.get(song_api_url) as resp:
            json_dict = await resp.json()
    pvs = json_dict["pvs"]
    song_url = [pv["url"] for pv in pvs if pv["service"] == "Youtube"]
    if not song_url:
        song_url = [pv["url"] for pv in pvs if pv["service"] == "NicoNicoDouga"]
        nico_links.extend(song_url)
    else:
        yt_links.extend(song_url)


asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(get_songs())
