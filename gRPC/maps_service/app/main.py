import asyncio
import json
import os
from contextlib import asynccontextmanager
from pathlib import Path

import grpc
import transport_pb2
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from grpc_client import TransportGrpcClient


def route_kind_name(kind: int) -> str:
    if kind == transport_pb2.BUS:
        return "BUS"
    if kind == transport_pb2.TROLLEYBUS:
        return "TROLLEYBUS"
    return "UNKNOWN"


@asynccontextmanager
async def lifespan(app: FastAPI):
    target = os.getenv("TRANSPORT_GRPC_TARGET", "transport_service:50051")
    client = TransportGrpcClient(target)
    await client.connect()
    app.state.grpc_client = client
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
    client: TransportGrpcClient = request.app.state.grpc_client
    res = await client.get_stops()
    return {
        "stops": [
            {"id": s.id, "name": s.name, "lat": s.lat, "lon": s.lon}
            for s in res.stops
        ]
    }


@app.get("/api/stops/{stop_id}/routes")
async def get_stop_routes(stop_id: str, request: Request):
    client: TransportGrpcClient = request.app.state.grpc_client
    try:
        res = await client.get_stop_routes(stop_id)
    except grpc.aio.AioRpcError as exc:
        if exc.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail="Stop not found") from exc
        raise HTTPException(status_code=502, detail="Transport service unavailable") from exc

    return {
        "routes": [
            {
                "id": r.id,
                "number": r.number,
                "kind": route_kind_name(r.kind),
                "display_name": r.display_name,
            }
            for r in res.routes
        ]
    }


@app.get("/api/routes/{route_id}")
async def get_route_details(route_id: str, request: Request):
    client: TransportGrpcClient = request.app.state.grpc_client
    try:
        res = await client.get_route_details(route_id)
    except grpc.aio.AioRpcError as exc:
        if exc.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(status_code=404, detail="Route not found") from exc
        raise HTTPException(status_code=502, detail="Transport service unavailable") from exc

    return {
        "route": {
            "id": res.route.id,
            "number": res.route.number,
            "kind": route_kind_name(res.route.kind),
            "display_name": res.route.display_name,
        },
        "schedule": [
            {
                "stop_id": entry.stop_id,
                "arrival_hhmm": entry.arrival_hhmm,
                "destination": entry.destination,
            }
            for entry in res.schedule
        ],
        "geometry": [
            {
                "seq": segment.seq,
                "start_lat": segment.start_lat,
                "start_lon": segment.start_lon,
                "end_lat": segment.end_lat,
                "end_lon": segment.end_lon,
            }
            for segment in res.geometry
        ],
    }


@app.get("/api/routes/{route_id}/vehicles/stream")
async def stream_vehicles(route_id: str, request: Request):
    client: TransportGrpcClient = request.app.state.grpc_client

    async def event_generator():
        try:
            async for pos in client.stream_vehicle_positions(route_id):
                payload = {
                    "vehicle_id": pos.vehicle_id,
                    "route_id": pos.route_id,
                    "lat": pos.lat,
                    "lon": pos.lon,
                    "bearing_deg": pos.bearing_deg,
                    "timestamp_unix": pos.timestamp_unix,
                }
                yield f"data: {json.dumps(payload)}\n\n"
                await asyncio.sleep(0)
        except grpc.aio.AioRpcError as exc:
            if exc.code() == grpc.StatusCode.NOT_FOUND:
                error_payload = {"error": "Route not found"}
            else:
                error_payload = {"error": "Transport stream unavailable"}
            yield f"event: error\ndata: {json.dumps(error_payload)}\n\n"
        except asyncio.CancelledError:
            return

    return StreamingResponse(event_generator(), media_type="text/event-stream")
