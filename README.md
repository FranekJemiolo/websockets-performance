# Simple websocket performance tool in Python

## Building
```bash
./build.sh
```

## Running
First start up the server
```bash
./run_server.sh --random-message --compression GZIP --batch-size 100
```
then a corresponding client
```bash
./run_client.sh --compression GZIP --batch-size 100
```

`batch-size` and `compression` need to match between client and server.


## Example results
Tested on i5-8250U CPU (4 cores, 1.60GHZ) with 1000000 messages.

| Random message | Compression | Batch size | Result |
| --- | --- | --- | --- |
| true | GZIP | 100 | 120,000 msg/s |
| false | GZIP | 100 | 160,000 msg/s |
| true | None | 100 | 215,000 msg/s |
| false | None | 100 | 330,000 msg/s |
| true/false | GZIP | 1 | 14,200 msg/s |
| true/false | None | 1 | 42,000 msg/s |

Batching and no compression offers the best throughput when testing locally.
When network connection becomes an issue I would suspect compression would lead to better results.
Additionally, a faster compression algorithm could be chosen, as GZIP is known to be slow, however Python lacks proper built-in fast access to algorithms like ZSTD.

## Caveats
Given that the functions use only `await websocket.send()` multiple clients will not be able to stream data at the same time, unless the write buffer is full.
This is done deliberately to test the throughput without additional throttling. 
See: [https://websockets.readthedocs.io/en/stable/api.html#websockets.protocol.WebSocketCommonProtocol.send](https://websockets.readthedocs.io/en/stable/api.html#websockets.protocol.WebSocketCommonProtocol.send)

If you want to see the performance with multiple clients connected, just add `await asyncio.sleep(0)` to the `while True:` loop.
See: [https://github.com/python/asyncio/issues/284#issuecomment-154159149](https://github.com/python/asyncio/issues/284#issuecomment-154159149)
 
