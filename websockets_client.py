import asyncio
import json
import time

import websockets
from tqdm import tqdm


NUM_TEST_MESSAGES = 1000000


async def performance_test():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri, close_timeout=1, ping_interval=None, ping_timeout=None) as websocket:
        params = {"num_messages": 1000}
        params_str = json.dumps(params)
        await websocket.send(params_str)
        for i in tqdm(range(NUM_TEST_MESSAGES)):
            message = await websocket.recv()


async def performance_test_no_tqdm():
    uri = "ws://localhost:8765"
    print("No tqdm test")
    async with websockets.connect(uri, close_timeout=1, ping_interval=None, ping_timeout=None) as websocket:
        params = {"num_messages": 1000}
        params_str = json.dumps(params)
        await websocket.send(params_str)
        before = time.time()
        for i in range(NUM_TEST_MESSAGES):
            message = await websocket.recv()
        after = time.time()
        print(f"Took {after - before} seconds to process {NUM_TEST_MESSAGES}")


def main():
    asyncio.get_event_loop().run_until_complete(performance_test())
    asyncio.get_event_loop().run_until_complete(performance_test_no_tqdm())


if __name__ == "__main__":
    main()

