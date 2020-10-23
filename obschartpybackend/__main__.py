from dotenv import load_dotenv

load_dotenv()

from obschart import ObschartClient, ApplicationRequestHandler
import os
import asyncio
from typing import List

from .sumo_squat_counter.__main__ import SumoSquatCounter  # type:ignore

token = os.environ["OBSCHART_APP_TOKEN"]
api_url = "https://api.obschart.com/"
client = ObschartClient(token, api_url=api_url)

requestHandlers: List[ApplicationRequestHandler] = [
SumoSquatCounter(ObschartClient("c796ce35-ecb9-42ca-997d-3246a6ec67a9", api_url=api_url)),
]

print("App server running...")


async def main():
    await asyncio.gather(
        *[
            requestHandler.client.run(requestHandler.on_request)
            for requestHandler in requestHandlers
        ]
    )


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
