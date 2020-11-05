docker run -it --rm --network host --entrypoint "python" websockets_performance:1.0.0 -mwebsockets_server "${@:1}"
