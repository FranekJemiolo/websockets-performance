import asyncio
import base64
import json
import gzip
import math
from functools import partial

import click
import websockets
from tqdm import tqdm


NUM_TEST_MESSAGES = 1000000


async def base_performance_test(handler):
    uri = "ws://localhost:8765"
    async with websockets.connect(uri, close_timeout=1, ping_interval=None, ping_timeout=None) as websocket:
        params = {"num_messages": 1000}
        params_str = json.dumps(params)
        await websocket.send(params_str)
        await handler(websocket)


async def single_message_handler(websocket, num_messages=1000000, **kwargs):
    for i in tqdm(range(num_messages)):
        message = await websocket.recv()


async def single_message_handler_gzip(websocket, num_messages=1000000, **kwargs):
    for i in tqdm(range(num_messages)):
        raw_message = await websocket.recv()
        message = gzip.decompress(raw_message)


async def batch_message_handler(websocket, num_messages=1000000, batch_size=100, **kwargs):
    t = tqdm(total=num_messages)
    for i in range(math.ceil(float(num_messages) / batch_size)):
        raw_batch = await websocket.recv()
        batch = json.loads(raw_batch)
        messages = [base64.standard_b64decode(raw_message) for raw_message in batch]
        t.update(n=batch_size)
    t.close()


async def batch_message_handler_gzip(websocket, num_messages=1000000, batch_size=100, **kwargs):
    t = tqdm(total=num_messages)
    for i in range(math.ceil(float(num_messages) / batch_size)):
        raw_batch = await websocket.recv()
        batch = json.loads(gzip.decompress(raw_batch))
        messages = [base64.standard_b64decode(raw_message) for raw_message in batch]
        t.update(n=batch_size)
    t.close()


async def performance_test(batch_size, compression, num_messages):
    if batch_size == 1:
        if compression == "GZIP":
            await base_performance_test(partial(single_message_handler_gzip, num_messages=num_messages))
        elif compression == "None":
            await base_performance_test(partial(single_message_handler, num_messages=num_messages))
    elif batch_size > 1:
        if compression == "GZIP":
            await base_performance_test(partial(batch_message_handler_gzip, num_messages=num_messages,
                                                batch_size=batch_size))
        elif compression == "None":
            await base_performance_test(partial(batch_message_handler, num_messages=num_messages,
                                                batch_size=batch_size))


@click.command()
@click.option("--batch-size",
              help="Set the number of messages sent in one request",
              default=1)
@click.option("--compression",
              help="Choose the type of compression for the message",
              type=click.Choice(["None", "GZIP"], case_sensitive=False),
              required=True)
@click.option("--num-messages",
              help="Number of messages on which you want to test the client",
              default=1000000)
def main(batch_size, compression, num_messages):
    asyncio.get_event_loop().run_until_complete(performance_test(batch_size, compression, num_messages))


if __name__ == "__main__":
    main()

