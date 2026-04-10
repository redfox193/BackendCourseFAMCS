from __future__ import annotations

import asyncio
import logging
import os
import time

import grpc
from google.protobuf import empty_pb2

import transport_pb2, transport_pb2_grpc
from data import ROUTES, STOPS, STOP_TO_ROUTE_IDS
from simulation import current_positions, kinds_to_enum_value, route_geometry_segments


logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("transport-service")


class TransportService(transport_pb2_grpc.TransportServiceServicer):
    async def GetStops(self, request: empty_pb2.Empty, context: grpc.aio.ServicerContext):
        stops = [
            transport_pb2.Stop(id=s.id, name=s.name, lat=s.lat, lon=s.lon)
            for s in STOPS.values()
        ]
        return transport_pb2.GetStopsResponse(stops=stops)

    async def GetStopRoutes(
        self, request: transport_pb2.StopRequest, context: grpc.aio.ServicerContext
    ):
        if request.stop_id not in STOPS:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Stop not found")
            return transport_pb2.GetStopRoutesResponse()

        routes = []
        for route_id in STOP_TO_ROUTE_IDS.get(request.stop_id, []):
            route = ROUTES[route_id]
            routes.append(
                transport_pb2.Route(
                    id=route.id,
                    number=route.number,
                    kind=kinds_to_enum_value(route.kind),
                    display_name=route.display_name,
                )
            )
        return transport_pb2.GetStopRoutesResponse(routes=routes)

    async def GetRouteDetails(
        self, request: transport_pb2.RouteRequest, context: grpc.aio.ServicerContext
    ):
        route = ROUTES.get(request.route_id)
        if route is None:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Route not found")
            return transport_pb2.GetRouteDetailsResponse()

        schedule = [
            transport_pb2.ScheduleEntry(
                stop_id=route.stop_ids[idx % len(route.stop_ids)],
                arrival_hhmm=hhmm,
                destination=route.destination,
            )
            for idx, hhmm in enumerate(route.schedule_hhmm)
        ]
        geometry = [
            transport_pb2.RouteGeometrySegment(
                seq=seq,
                start_lat=start_lat,
                start_lon=start_lon,
                end_lat=end_lat,
                end_lon=end_lon,
            )
            for seq, start_lat, start_lon, end_lat, end_lon in route_geometry_segments(route)
        ]
        route_msg = transport_pb2.Route(
            id=route.id,
            number=route.number,
            kind=kinds_to_enum_value(route.kind),
            display_name=route.display_name,
        )
        return transport_pb2.GetRouteDetailsResponse(
            route=route_msg,
            schedule=schedule,
            geometry=geometry,
        )

    async def StreamVehiclePositions(
        self, request: transport_pb2.VehicleStreamRequest, context: grpc.aio.ServicerContext
    ):
        route = ROUTES.get(request.route_id)
        if route is None:
            await context.abort(grpc.StatusCode.NOT_FOUND, "Route not found")

        default_interval_seconds = float(os.getenv("STREAM_INTERVAL_SECONDS", "1.0"))
        while True:
            for pos in current_positions(route):
                yield transport_pb2.VehiclePosition(
                    vehicle_id=pos.vehicle_id,
                    route_id=route.id,
                    lat=pos.lat,
                    lon=pos.lon,
                    bearing_deg=pos.bearing_deg,
                    timestamp_unix=pos.timestamp_unix,
                )
            await asyncio.sleep(default_interval_seconds)


async def serve() -> None:
    port = os.getenv("GRPC_PORT", "50051")
    server = grpc.aio.server()
    transport_pb2_grpc.add_TransportServiceServicer_to_server(TransportService(), server)
    server.add_insecure_port(f"0.0.0.0:{port}")
    logger.info("Starting transport gRPC server on 0.0.0.0:%s", port)
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
