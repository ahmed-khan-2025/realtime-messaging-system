from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:

    def __init__(self):

        self.connections = defaultdict(set)


    async def connect(
        self,
        room_id: int,
        websocket: WebSocket
    ):

        await websocket.accept()

        self.connections[
            room_id
        ].add(websocket)


    def disconnect(
        self,
        room_id: int,
        websocket: WebSocket
    ):

        self.connections[
            room_id
        ].discard(websocket)

        if not self.connections[
            room_id
        ]:

            self.connections.pop(
                room_id,
                None
            )


    async def broadcast(
        self,
        room_id: int,
        payload: dict
    ):

        dead_connections = []

        for websocket in list(
            self.connections.get(
                room_id,
                set()
            )
        ):

            try:

                await websocket.send_json(
                    payload
                )

            except Exception:

                dead_connections.append(
                    websocket
                )

        for websocket in dead_connections:

            self.disconnect(
                room_id,
                websocket
            )


manager = ConnectionManager()