"""
The Main File
"""

import asyncio
import math
import sys
import aiohttp


print("What is the vocadb artist id?\nEx: 100054 -> https://vocadb.net/Ar/100054")
ARTIST_ID = input()
print("how many results do you want? (Leave empty for 100)")
MAX_RESULTS = input()
if not MAX_RESULTS:
    MAX_RESULTS = 100

if int(MAX_RESULTS) > 100:
    times = math.floor(int(MAX_RESULTS) / 100)
    remaining = int(MAX_RESULTS) - (100 * times)
    num_results = times * [100]
    if remaining:
        num_results.append(remaining)
    offsets = []
    for idx, i in enumerate(num_results):
        num2 = i
        if idx == 0:
            num1 = 0
        else:
            num1 = sum(num_results[:idx])
        offsets.append([num1, num2])
    print(f"Can only do 100 at a time, so i'm splitting it into {len(offsets)} parts")
else:
    offsets = [[0, int(MAX_RESULTS)]]


yt_links = []
nico_links = []
songs = {}



async def get_100(session, idx, nums):
    "gets the songs in batches of 100"
    url = (
        "https://vocadb.net/api/songs"
        f"?start={nums[0]}&"
        "getTotalCount=true"
        f"&maxResults={nums[1]}"
        "&fields=AdditionalNames%2CMainPicture"
        "&lang=Default&nameMatchMode=Auto"
        "&sort=Name"
        "&childTags=false"
        f"&artistId%5B%5D={ARTIST_ID}"
        "&artistParticipationStatus=Everything"
        "&onlyWithPvs=false"
    )
    async with session.get(url) as resp:
        json_dict = await resp.json()
    songs[idx] = json_dict["items"]


async def get_songs(offsets):
    "Gets list of songs through vocadb given the artist id"
    async with aiohttp.ClientSession() as session:
        tasks = [get_100(session, idx, i) for idx, i in enumerate(offsets)]
        await asyncio.gather(*tasks)
    song_id_list = []
    for idx, _ in enumerate(songs): #can't use "_", it won't be in the right order
        for song in songs[idx]:
            song_id_list.append(song["id"])
    async with aiohttp.ClientSession() as session:
        tasks = [get_url(session, i) for i in song_id_list]
        await asyncio.gather(*tasks)
    yt_count = len(yt_links)
    nico_count = len(nico_links)
    total_count = len(song_id_list)
    found_count = total_count - FAILED_COUNT
    with open("yt.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(yt_links))
    with open("nico.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(nico_links))
    print(
        f"\nYT URLS: {yt_count}\n"
        f"NICO URLS: {nico_count}\n"
        f"With links: {found_count}\n"
        f"No links: {FAILED_COUNT}\n"
        f"Total: {total_count}\n\n"
        "You can find the list of urls inside 'yt.txt' and 'nico.txt'"
    )


FAILED_COUNT = 0


async def get_url(session, song_id):
    "Gives the youtube url or niconico url of a song id"
    global FAILED_COUNT
    # print(f"Doing {song_id}...")
    song_api_url = f"https://vocadb.net/api/songs/{song_id}/details"
    async with session.get(song_api_url) as resp:
        json_dict = await resp.json()
    pvs = json_dict["pvs"]
    yt_song_urls = [pv["url"] for pv in pvs if pv["service"] == "Youtube"]
    nico_song_urls = [pv["url"] for pv in pvs if pv["service"] == "NicoNicoDouga"]
    if yt_song_urls:
        yt_links.append(yt_song_urls[0])
    elif nico_song_urls:
        nico_links.append(nico_song_urls[0])
    else:
        print(f"Could not get URL for {song_id}")
        FAILED_COUNT += 1


if sys.platform == "win32":
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(get_songs((offsets)))
