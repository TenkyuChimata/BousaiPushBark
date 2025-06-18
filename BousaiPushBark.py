# -*- coding: utf-8 -*-

#
#  Bousai Push Bark
#  Current version 1.0.2
#  Code Python version 3.12
#
#  API Source: https://api.wolfx.jp
#  Bark: https://github.com/finb/bark
#  Github: https://github.com/TenkyuChimata/BousaiPushBark
#
# ####

import json
import aiohttp
import asyncio
import datetime
import websockets

first = True

keys = [  # Bark Keys
    "XXXXXXX",
    "AAAAAAA",
    "bbbbbbb",
]


def getTime():
    return datetime.datetime.now().strftime("%H:%M:%S")


async def fetch(session, key, content):
    url = f"https://api.day.app/{key}/{content}"
    async with session.get(url) as response:
        return await response.text()


async def push(content):
    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(fetch(session, key, content)) for key in keys]
        await asyncio.gather(*tasks)


async def websocket_client():
    global first
    while True:
        try:
            async with websockets.connect("wss://ws-api.wolfx.jp/all_eew") as websocket:
                print(f"[{getTime()}] Connected to WebSocket API.")
                while True:
                    data = json.loads(await websocket.recv())
                    if data["type"] != "heartbeat":
                        if data["type"] == "jma_eew":
                            title = f"{data['Title']}"
                            serial = (
                                f"第{data['Serial']}報"
                                if not data["isFinal"]
                                else "最終報"
                            )
                            text = f"{serial} {data['OriginTime'].replace('/', '-')} {data['Hypocenter']} M{data['Magunitude']} 深さ{data['Depth']}km 最大震度{data['MaxIntensity']}"
                            print(f"[{getTime()}] [{title}] {text}")
                            await push(f"{title}/{text}")
                        elif data["type"] == "jma_eqlist":
                            title = "地震情報（気象庁）"
                            text = f"{data['No1']['time_full'].replace('/', '-')} {data['No1']['location']} M{data['No1']['magnitude']} 深さ{data['No1']['depth']} 最大震度{data['No1']['shindo']}"
                            print(f"[{getTime()}] [{title}] {text}")
                            await push(f"{title}/{text}")
                        elif data["type"] == "sc_eew":
                            title = "地震预警（四川地震局）"
                            text = f"第{data['ReportNum']}报 {data['OriginTime']} {data['HypoCenter']} M{data['Magunitude']} 最大烈度{data['MaxIntensity']}"
                            print(f"[{getTime()}] [{title}] {text}")
                            await push(f"{title}/{text}")
                        elif data["type"] == "fj_eew":
                            title = "地震预警（福建地震局）"
                            text = f"第{data['ReportNum']}报 {data['OriginTime']} {data['HypoCenter']} M{data['Magunitude']}"
                            print(f"[{getTime()}] [{title}] {text}")
                            await push(f"{title}/{text}")
                        elif data["type"] == "cenc_eqlist":
                            title = "地震速报（中国地震台网）"
                            text = f"{data['No1']['time']} {data['No1']['location']} M{data['No1']['magnitude']} 深度{data['No1']['depth']}km 最大烈度{data['No1']['intensity']}"
                            print(f"[{getTime()}] [{title}] {text}")
                            await push(f"{title}/{text}")
                    else:
                        if not first:
                            print(
                                f"[{getTime()}] Received WebSocket API heartbeat, acknowledged."
                            )
                            await websocket.send("ping")
                        else:
                            first = False
        except Exception as e:
            print(e)
            await asyncio.sleep(1)
            continue


if __name__ == "__main__":
    asyncio.run(websocket_client())
