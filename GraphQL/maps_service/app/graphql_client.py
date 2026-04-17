from __future__ import annotations

import json
import logging
from typing import Any, AsyncIterator, Dict, Optional

import httpx
import websockets

logger = logging.getLogger("maps-service.graphql-client")

STOPS_QUERY = """
query {
  stops {
    id
    name
    lat
    lon
  }
}
"""

STOP_ROUTES_QUERY = """
query StopRoutes($stopId: String!) {
  stopRoutes(stopId: $stopId) {
    id
    number
    kind
    displayName
  }
}
"""

ROUTE_DETAILS_QUERY = """
query RouteDetails($routeId: String!) {
  routeDetails(routeId: $routeId) {
    route {
      id
      number
      kind
      displayName
    }
    schedule {
      stopId
      arrivalHhmm
      destination
    }
    geometry {
      seq
      startLat
      startLon
      endLat
      endLon
    }
  }
}
"""

VEHICLE_POSITIONS_SUBSCRIPTION = """
subscription VehiclePositions($routeId: String!) {
  vehiclePositions(routeId: $routeId) {
    vehicleId
    routeId
    lat
    lon
    bearingDeg
    timestampUnix
  }
}
"""


class TransportGraphQLClient:
    def __init__(self, http_url: str, ws_url: str) -> None:
        self._http_url = http_url
        self._ws_url = ws_url
        self._http_client: httpx.AsyncClient | None = None

    async def connect(self) -> None:
        self._http_client = httpx.AsyncClient()

    async def close(self) -> None:
        if self._http_client is not None:
            await self._http_client.aclose()
            self._http_client = None

    async def _query(
        self, query: str, variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if self._http_client is None:
            raise RuntimeError("GraphQL client is not connected")

        payload: Dict[str, Any] = {"query": query}
        if variables:
            payload["variables"] = variables

        resp = await self._http_client.post(self._http_url, json=payload)
        resp.raise_for_status()
        body = resp.json()

        if "errors" in body and body["errors"]:
            raise GraphQLError(body["errors"])

        return body["data"]

    async def get_stops(self) -> list[dict]:
        data = await self._query(STOPS_QUERY)
        return data["stops"]

    async def get_stop_routes(self, stop_id: str) -> list[dict] | None:
        data = await self._query(STOP_ROUTES_QUERY, {"stopId": stop_id})
        return data["stopRoutes"]

    async def get_route_details(self, route_id: str) -> dict | None:
        data = await self._query(ROUTE_DETAILS_QUERY, {"routeId": route_id})
        return data["routeDetails"]

    async def stream_vehicle_positions(
        self, route_id: str
    ) -> AsyncIterator[list[dict]]:
        async for connection in websockets.connect(
            self._ws_url, subprotocols=["graphql-transport-ws"]
        ):
            try:
                await connection.send(json.dumps({"type": "connection_init"}))
                ack = json.loads(await connection.recv())
                if ack.get("type") != "connection_ack":
                    raise RuntimeError(f"Unexpected WS ack: {ack}")

                await connection.send(
                    json.dumps(
                        {
                            "id": "1",
                            "type": "subscribe",
                            "payload": {
                                "query": VEHICLE_POSITIONS_SUBSCRIPTION,
                                "variables": {"routeId": route_id},
                            },
                        }
                    )
                )

                async for raw in connection:
                    msg = json.loads(raw)
                    print(msg)
                    if msg["type"] == "next":
                        yield msg["payload"]["data"]["vehiclePositions"]
                    elif msg["type"] == "error":
                        errors = msg.get("payload", [])
                        raise GraphQLError(errors)
                    elif msg["type"] == "complete":
                        return
            except websockets.ConnectionClosed:
                logger.warning("WebSocket closed, reconnecting...")
                continue


class GraphQLError(Exception):
    def __init__(self, errors: list) -> None:
        self.errors = errors
        messages = "; ".join(e.get("message", str(e)) for e in errors)
        super().__init__(messages)
