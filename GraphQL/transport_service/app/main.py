from __future__ import annotations

import asyncio

import uvicorn
from typing import AsyncGenerator, List, Optional

import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from data import ROUTES, STOPS, STOP_TO_ROUTE_IDS
from simulation import current_positions, route_geometry_segments


@strawberry.type
class Stop:
    id: str
    name: str
    lat: float
    lon: float


@strawberry.type
class Route:
    id: str
    number: str
    kind: str
    display_name: str


@strawberry.type
class ScheduleEntry:
    stop_id: str
    arrival_hhmm: str
    destination: str


@strawberry.type
class RouteGeometrySegment:
    seq: int
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float


@strawberry.type
class VehiclePosition:
    vehicle_id: str
    route_id: str
    lat: float
    lon: float
    bearing_deg: float
    timestamp_unix: int


@strawberry.type
class RouteDetails:
    route: Route
    schedule: List[ScheduleEntry]
    geometry: List[RouteGeometrySegment]


@strawberry.type
class Query:
    @strawberry.field
    def stops(self) -> List[Stop]:
        return [
            Stop(id=s.id, name=s.name, lat=s.lat, lon=s.lon)
            for s in STOPS.values()
        ]

    @strawberry.field
    def stop_routes(self, stop_id: str, info: strawberry.Info) -> Optional[List[Route]]:
        if stop_id not in STOPS:
            raise ValueError(f"stop_id {stop_id} not in STOPS")

        routes = []
        for route_id in STOP_TO_ROUTE_IDS.get(stop_id, []):
            route = ROUTES[route_id]
            routes.append(
                Route(
                    id=route.id,
                    number=route.number,
                    kind=route.kind,
                    display_name=route.display_name,
                )
            )
        return routes

    @strawberry.field
    def route_details(self, route_id: str) -> Optional[RouteDetails]:
        route = ROUTES.get(route_id)
        if route is None:
            return None

        schedule = [
            ScheduleEntry(
                stop_id=route.stop_ids[idx % len(route.stop_ids)],
                arrival_hhmm=hhmm,
                destination=route.destination,
            )
            for idx, hhmm in enumerate(route.schedule_hhmm)
        ]
        geometry = [
            RouteGeometrySegment(
                seq=seq,
                start_lat=start_lat,
                start_lon=start_lon,
                end_lat=end_lat,
                end_lon=end_lon,
            )
            for seq, start_lat, start_lon, end_lat, end_lon in route_geometry_segments(route)
        ]
        route_msg = Route(
            id=route.id,
            number=route.number,
            kind=route.kind,
            display_name=route.display_name,
        )
        return RouteDetails(route=route_msg, schedule=schedule, geometry=geometry)


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def vehicle_positions(
        self, route_id: str, info: strawberry.Info, 
    ) -> AsyncGenerator[List[VehiclePosition], None]:
        print(info) 

        route = ROUTES.get(route_id)
        if route is None:
            return

        while True:
            positions = [
                VehiclePosition(
                    vehicle_id=pos.vehicle_id,
                    route_id=route.id,
                    lat=pos.lat,
                    lon=pos.lon,
                    bearing_deg=pos.bearing_deg,
                    timestamp_unix=pos.timestamp_unix,
                )
                for pos in current_positions(route)
            ]
            yield positions
            await asyncio.sleep(0.1)


schema = strawberry.Schema(query=Query, subscription=Subscription)
graphql_app = GraphQLRouter(schema)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
