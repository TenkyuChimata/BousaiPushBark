# -*- coding: utf-8 -*-
import json
import time
import aiohttp
import asyncio
import websockets

keys = [ # Bark Keys
    "XXXXXXX",
    "AAAAAAA",
    "bbbbbbb",
]

async def fetch(session, key, content):
    url = f"https://api.day.app/{key}/{content}"
    async with session.get(url) as response:
        return await response.text()

async def push(content):
    async with aiohttp.ClientSession() as session:
        tasks = [await fetch(session, key, content) for key in keys]

async def websocket_client():
    global first
    while True:
        try:
            async with websockets.connect("wss://ws-api.wolfx.jp/all_eew") as websocket:
                while True:
                    data = json.loads(await websocket.recv())
                    if data["type"] != "heartbeat":
                        if data["type"] == "jma_eew":
                            title = f"{data['Title']}"
                            serial = f"第{data['Serial']}報" if not data["isFinal"] else "最終報"
                            text = f"{serial} {data['OriginTime'].replace('/', '-')} {data['Hypocenter']} M{data['Magunitude']} 深さ{data['Depth']}km 最大震度{data['MaxIntensity']}"
                            await push(f"{title}/{text}")
                        elif data["type"] == "jma_eqlist":
                            title = "地震情報（気象庁）"
                            text = f"{data['No1']['time_full'].replace('/', '-')} {data['No1']['location']} M{data['No1']['magnitude']} 深さ{data['No1']['depth']} 最大震度{data['No1']['shindo']}"
                            await push(f"{title}/{text}")
                        elif data["type"] == "sc_eew":
                            title = "地震预警（四川地震局）"
                            text = f"第{data['ReportNum']}报 {data['OriginTime']} {data['HypoCenter']} M{data['Magunitude']} 最大烈度{data['MaxIntensity']}"
                            await push(f"{title}/{text}")
                        elif data["type"] == "fj_eew":
                            title = "地震预警（福建地震局）"
                            text = f"第{data['ReportNum']}报 {data['OriginTime']} {data['HypoCenter']} M{data['Magunitude']}"
                            await push(f"{title}/{text}")
                        elif data["type"] == "cenc_eqlist":
                            title = "地震速报（中国地震台网）"
                            text = f"{data['No1']['time']} {data['No1']['location']} M{data['No1']['magnitude']} 深度{data['No1']['depth']}km 最大烈度{data['No1']['intensity']}"
                            await push(f"{title}/{text}")
        except Exception as e:
            print(e)
            time.sleep(1)
            continue

if __name__ == "__main__":
    asyncio.run(websocket_client())