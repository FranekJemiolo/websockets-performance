import asyncio
import signal

import websockets


MESSAGE_SIZE = 100


async def send_indefinitely(websocket, path):
    params = await websocket.recv()
    random_message = "a" * MESSAGE_SIZE
    try:
        while True:
            await websocket.send(random_message)
    except websockets.exceptions.ConnectionClosed:
        raise
    except KeyboardInterrupt:
        return
    finally:
        return

async def run_server(stop_flag):
    async with websockets.serve(send_indefinitely, "0.0.0.0", 8765, close_timeout=1, ping_interval=None, ping_timeout=None):
        await stop_flag


loop = asyncio.get_event_loop()

stop = loop.create_future()
loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

loop.run_until_complete(run_server(stop))

