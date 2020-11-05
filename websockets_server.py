import asyncio
import base64
import gzip
import json
import random
import signal
import string
from functools import partial

import click
import websockets


async def basic_handler(websocket, path, handler=None, **kwargs):
    params = await websocket.recv()
    try:
        await handler(websocket, path, params, **kwargs)
    except websockets.exceptions.ConnectionClosed:
        raise
    except KeyboardInterrupt:
        return
    finally:
        return


# Deliberately implement copy-paste like functions to avoid if statements that could slow down the code
# no compile time :(

async def send_indefinitely_one(websocket, path, params, message_size=100, **kwargs):
    random_message = "a" * message_size
    while True:
        await websocket.send(random_message)


async def send_indefinitely_one_gzip(websocket, path, params, message_size=100, **kwargs):
    random_message = "a" * message_size
    while True:
        await websocket.send(gzip.compress(random_message))


async def send_indefinitely_one_random(websocket, path, params, message_size=100, **kwargs):
    random.seed(42)
    while True:
        random_message = ''.join(random.choice(string.ascii_lowercase) for i in range(message_size))
        await websocket.send(random_message)


async def send_indefinitely_one_random_gzip(websocket, path, params, message_size=100, **kwargs):
    random.seed(42)
    while True:
        random_message = ''.join(random.choice(string.ascii_lowercase) for i in range(message_size))
        await websocket.send(gzip.compress(random_message))


async def send_indefinitely_batch(websocket, path, params, batch_size=100, message_size=100, **kwargs):
    random_message = "a" * message_size
    counter = 0
    batch = []
    while True:
        batch.append(base64.standard_b64encode(random_message))
        counter += 1
        if counter == batch_size:
            await websocket.send(json.dumps(batch))
            batch = []
            counter = 0


async def send_indefinitely_batch_gzip(websocket, path, params, batch_size=100, message_size=100, **kwargs):
    random_message = "a" * message_size
    counter = 0
    batch = []
    while True:
        batch.append(base64.standard_b64encode(random_message))
        counter += 1
        if counter == batch_size:
            await websocket.send(gzip.compress(json.dumps(batch)))
            batch = []
            counter = 0


async def send_indefinitely_batch_random(websocket, path, params, batch_size=100, message_size=100, **kwargs):
    random.seed(42)
    counter = 0
    batch = []
    while True:
        random_message = ''.join(random.choice(string.ascii_lowercase) for i in range(message_size))
        batch.append(base64.standard_b64encode(random_message))
        counter += 1
        if counter == batch_size:
            await websocket.send(json.dumps(batch))
            batch = []
            counter = 0


async def send_indefinitely_batch_random_gzip(websocket, path, params, batch_size=100, message_size=100, **kwargs):
    random.seed(42)
    counter = 0
    batch = []
    while True:
        random_message = ''.join(random.choice(string.ascii_lowercase) for i in range(message_size))
        batch.append(base64.standard_b64encode(random_message))
        counter += 1
        if counter == batch_size:
            await websocket.send(gzip.compress(json.dumps(batch)))
            batch = []
            counter = 0


def get_handler_function(message_size, batch_size, random_message, compression):
    if batch_size == 1:
        if compression == "GZIP":
            if random_message:
                return partial(basic_handler, handler=send_indefinitely_one_random_gzip, batch_size=batch_size,
                               message_size=message_size)
            else:
                return partial(basic_handler, handler=send_indefinitely_one_gzip, batch_size=batch_size,
                               message_size=message_size)
        elif compression == "None":
            if random_message:
                return partial(basic_handler, handler=send_indefinitely_one_random, batch_size=batch_size,
                               message_size=message_size)
            else:
                return partial(basic_handler, handler=send_indefinitely_one, batch_size=batch_size,
                               message_size=message_size)
    elif batch_size > 1:
        if compression == "GZIP":
            if random_message:
                return partial(basic_handler, handler=send_indefinitely_batch_random_gzip, batch_size=batch_size,
                               message_size=message_size)
            else:
                return partial(basic_handler, handler=send_indefinitely_batch_gzip, batch_size=batch_size,
                               message_size=message_size)
        elif compression == "None":
            if random_message:
                return partial(basic_handler, handler=send_indefinitely_batch_random, batch_size=batch_size,
                               message_size=message_size)
            else:
                return partial(basic_handler, handler=send_indefinitely_batch, batch_size=batch_size,
                               message_size=message_size)


async def run_server(stop_flag, message_size, batch_size, random_message, compression):
    async with websockets.serve(get_handler_function(message_size, batch_size, random_message, compression),
                                "0.0.0.0", 8765, close_timeout=1, ping_interval=None, ping_timeout=None):
        await stop_flag


@click.command()
@click.option("--message-size",
              help="Set the single message size",
              default=100)
@click.option("--batch-size",
              help="Set the number of messages sent in one request",
              default=1)
@click.option("--random-message",
              help="If you want to use randomly generated messages",
              is_flag=True)
@click.option("--compression",
              help="Choose the type of compression for the message",
              type=click.Choice(["None", "GZIP"], case_sensitive=False))
def main(message_size, batch_size, random_message, compression):
    loop = asyncio.get_event_loop()

    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

    loop.run_until_complete(run_server(stop, message_size, batch_size, random_message, compression))


if __name__ == "__main__":
    main()
