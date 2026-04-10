from __future__ import annotations

import os
from typing import AsyncIterator

import grpc
from google.protobuf import empty_pb2

import transport_pb2, transport_pb2_grpc


class TransportGrpcClient:
    def __init__(self, target: str) -> None:
        self._target = target
        self._channel: grpc.aio.Channel | None = None
        self._stub: transport_pb2_grpc.TransportServiceStub | None = None

    async def connect(self) -> None:
        if self._channel is None:
            self._channel = grpc.aio.insecure_channel(self._target)
            self._stub = transport_pb2_grpc.TransportServiceStub(self._channel)

    async def close(self) -> None:
        if self._channel is not None:
            await self._channel.close()
        self._channel = None
        self._stub = None

    @property
    def stub(self) -> transport_pb2_grpc.TransportServiceStub:
        if self._stub is None:
            raise RuntimeError("gRPC client is not connected")
        return self._stub

    async def get_stops(self) -> transport_pb2.GetStopsResponse:
        timeout = float(os.getenv("GRPC_UNARY_TIMEOUT_SECONDS", "3"))
        return await self.stub.GetStops(empty_pb2.Empty(), timeout=timeout)

    async def get_stop_routes(self, stop_id: str) -> transport_pb2.GetStopRoutesResponse:
        timeout = float(os.getenv("GRPC_UNARY_TIMEOUT_SECONDS", "3"))
        req = transport_pb2.StopRequest(stop_id=stop_id)
        return await self.stub.GetStopRoutes(req, timeout=timeout)

    async def get_route_details(self, route_id: str) -> transport_pb2.GetRouteDetailsResponse:
        timeout = float(os.getenv("GRPC_UNARY_TIMEOUT_SECONDS", "3"))
        req = transport_pb2.RouteRequest(route_id=route_id)
        return await self.stub.GetRouteDetails(req, timeout=timeout)

    async def stream_vehicle_positions(
        self, route_id: str
    ) -> AsyncIterator[transport_pb2.VehiclePosition]:
        req = transport_pb2.VehicleStreamRequest(route_id=route_id)
        call = self.stub.StreamVehiclePositions(req)
        async for item in call:
            yield item
