from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Dict, Iterable, List

from data import RouteData


@dataclass(frozen=True)
class SimPosition:
    vehicle_id: str
    lat: float
    lon: float
    bearing_deg: float
    timestamp_unix: int


def _build_segments(points: List[tuple[float, float]]) -> List[dict]:
    segments: List[dict] = []
    cumulative = 0.0
    for i in range(len(points) - 1):
        lat1, lon1 = points[i]
        lat2, lon2 = points[i + 1]
        length = math.dist((lat1, lon1), (lat2, lon2))
        segments.append(
            {
                "start": points[i],
                "end": points[i + 1],
                "start_dist": cumulative,
                "length": max(length, 1e-6),
            }
        )
        cumulative += max(length, 1e-6)
    return segments


def _interpolate(route: RouteData, progress: float) -> tuple[float, float, float]:
    points = route.path_points
    if len(points) < 2:
        lat, lon = points[0]
        return lat, lon, 0.0

    segments = _build_segments(points)
    total = segments[-1]["start_dist"] + segments[-1]["length"]
    target_dist = progress * total

    segment = segments[-1]
    for candidate in segments:
        if target_dist <= candidate["start_dist"] + candidate["length"]:
            segment = candidate
            break

    local_dist = target_dist - segment["start_dist"]
    ratio = max(0.0, min(1.0, local_dist / segment["length"]))

    (lat1, lon1) = segment["start"]
    (lat2, lon2) = segment["end"]
    lat = lat1 + (lat2 - lat1) * ratio
    lon = lon1 + (lon2 - lon1) * ratio
    bearing = (math.degrees(math.atan2(lon2 - lon1, lat2 - lat1)) + 360.0) % 360.0
    return lat, lon, bearing


def current_positions(route: RouteData, vehicle_count: int = 3) -> Iterable[SimPosition]:
    now = time.time()
    cycle_seconds = 30.0

    for idx in range(vehicle_count):
        # Vehicles are equally offset along the same route loop.
        phase = ((now + idx * (cycle_seconds / vehicle_count)) % cycle_seconds) / cycle_seconds
        lat, lon, bearing = _interpolate(route, phase)
        yield SimPosition(
            vehicle_id=f"{route.id}-v{idx + 1}",
            lat=lat,
            lon=lon,
            bearing_deg=bearing,
            timestamp_unix=int(now),
        )


def route_geometry_segments(route: RouteData) -> List[tuple[int, float, float, float, float]]:
    result: List[tuple[int, float, float, float, float]] = []
    for idx in range(len(route.path_points) - 1):
        lat1, lon1 = route.path_points[idx]
        lat2, lon2 = route.path_points[idx + 1]
        result.append((idx, lat1, lon1, lat2, lon2))
    return result


def kinds_to_enum_value(kind: str) -> int:
    mapping: Dict[str, int] = {"BUS": 1, "TROLLEYBUS": 2}
    return mapping.get(kind, 0)
