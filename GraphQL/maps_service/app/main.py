import asyncio
import json
import uvicorn
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from graphql_client import TransportGraphQLClient, GraphQLError


import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    http_url = os.getenv("TRANSPORT_GRAPHQL_HTTP", "http://localhost:8001/graphql")
    ws_url = os.getenv("TRANSPORT_GRAPHQL_WS", "ws://localhost:8001/graphql")
    client = TransportGraphQLClient(http_url, ws_url)
    await client.connect()
    app.state.graphql_client = client
    yield
    await client.close()


app = FastAPI(title="Maps Service", lifespan=lifespan)
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


@app.get("/api/stops")
async def get_stops(request: Request):
    client: TransportGraphQLClient = request.app.state.graphql_client
    stops = await client.get_stops()
    return {"stops": stops}


@app.get("/api/stops/{stop_id}/routes")
async def get_stop_routes(stop_id: str, request: Request):
    client: TransportGraphQLClient = request.app.state.graphql_client
    try:
        routes = await client.get_stop_routes(stop_id)
    except GraphQLError as exc:
        raise HTTPException(status_code=502, detail="Transport service unavailable") from exc

    if routes is None:
        raise HTTPException(status_code=404, detail="Stop not found")

    return {
        "routes": [
            {
                "id": r["id"],
                "number": r["number"],
                "kind": r["kind"],
                "display_name": r["displayName"],
            }
            for r in routes
        ]
    }


@app.get("/api/routes/{route_id}")
async def get_route_details(route_id: str, request: Request):
    client: TransportGraphQLClient = request.app.state.graphql_client
    try:
        details = await client.get_route_details(route_id)
    except GraphQLError as exc:
        raise HTTPException(status_code=502, detail="Transport service unavailable") from exc

    if details is None:
        raise HTTPException(status_code=404, detail="Route not found")

    return {
        "route": {
            "id": details["route"]["id"],
            "number": details["route"]["number"],
            "kind": details["route"]["kind"],
            "display_name": details["route"]["displayName"],
        },
        "schedule": [
            {
                "stop_id": entry["stopId"],
                "arrival_hhmm": entry["arrivalHhmm"],
                "destination": entry["destination"],
            }
            for entry in details["schedule"]
        ],
        "geometry": [
            {
                "seq": seg["seq"],
                "start_lat": seg["startLat"],
                "start_lon": seg["startLon"],
                "end_lat": seg["endLat"],
                "end_lon": seg["endLon"],
            }
            for seg in details["geometry"]
        ],
    }


@app.get("/api/routes/{route_id}/vehicles/stream")
async def stream_vehicles(route_id: str, request: Request):
    client: TransportGraphQLClient = request.app.state.graphql_client

    async def event_generator():
        try:
            async for positions in client.stream_vehicle_positions(route_id):
                for pos in positions:
                    payload = {
                        "vehicle_id": pos["vehicleId"],
                        "route_id": pos["routeId"],
                        "lat": pos["lat"],
                        "lon": pos["lon"],
                        "bearing_deg": pos["bearingDeg"],
                        "timestamp_unix": pos["timestampUnix"],
                    }
                    yield f"data: {json.dumps(payload)}\n\n"
                    await asyncio.sleep(0)
        except GraphQLError:
            error_payload = {"error": "Transport stream unavailable"}
            yield f"event: error\ndata: {json.dumps(error_payload)}\n\n"
        except asyncio.CancelledError:
            return

    return StreamingResponse(event_generator(), media_type="text/event-stream")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)