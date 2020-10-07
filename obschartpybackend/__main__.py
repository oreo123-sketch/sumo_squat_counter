from dotenv import load_dotenv

load_dotenv()

from obschart import ObschartClient, ApplicationRequestHandler
import os
import asyncio
from typing import List

from .sumo_squat_counter.__main__ import SumoSquatCounter  # type:ignore

token = os.environ["OBSCHART_APP_TOKEN"]
api_url = "https://api.dashboard.justcoach.io/"
client = ObschartClient(token, api_url=api_url)

requestHandlers: List[ApplicationRequestHandler] = [
    SumoSquatCounter(ObschartClient("b0fe6221-0765-4f8d-bd1c-dd51edf3e329", api_url=api_url)),
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
