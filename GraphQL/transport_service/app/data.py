from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class StopData:
    id: str
    name: str
    lat: float
    lon: float


@dataclass(frozen=True)
class RouteData:
    id: str
    number: str
    kind: str  # "BUS" or "TROLLEYBUS"
    display_name: str
    stop_ids: List[str]
    path_points: List[tuple[float, float]]
    schedule_hhmm: List[str]
    destination: str


STOPS: Dict[str, StopData] = {
    "s1": StopData("s1", "Central Station", 55.7512, 37.6184),
    "s2": StopData("s2", "City Hall", 55.7561, 37.6145),
    "s3": StopData("s3", "River Park", 55.7616, 37.6267),
    "s4": StopData("s4", "University", 55.7479, 37.6334),
    "s5": StopData("s5", "Tech District", 55.7425, 37.6204),
    "s6": StopData("s6", "South Market", 55.7382, 37.6108),
}

ROUTES: Dict[str, RouteData] = {
    "r10": RouteData(
        id="r10",
        number="10",
        kind="BUS",
        display_name="Bus 10",
        stop_ids=["s1", "s2", "s3", "s4"],
        path_points=[
            (55.7512, 37.6184),
            (55.7538, 37.6164),
            (55.7561, 37.6145),
            (55.7584, 37.6201),
            (55.7616, 37.6267),
            (55.7548, 37.6302),
            (55.7479, 37.6334),
        ],
        schedule_hhmm=["07:40", "08:00", "08:20", "08:40", "09:00", "09:20"],
        destination="University",
    ),
    "r24": RouteData(
        id="r24",
        number="24",
        kind="BUS",
        display_name="Bus 24",
        stop_ids=["s5", "s1", "s2", "s6"],
        path_points=[
            (55.7425, 37.6204),
            (55.7472, 37.6190),
            (55.7512, 37.6184),
            (55.7537, 37.6163),
            (55.7561, 37.6145),
            (55.7480, 37.6127),
            (55.7382, 37.6108),
        ],
        schedule_hhmm=["07:45", "08:05", "08:25", "08:45", "09:05", "09:25"],
        destination="South Market",
    ),
    "t7": RouteData(
        id="t7",
        number="7",
        kind="TROLLEYBUS",
        display_name="Trolleybus 7",
        stop_ids=["s3", "s2", "s1", "s5"],
        path_points=[
            (55.7616, 37.6267),
            (55.7598, 37.6210),
            (55.7561, 37.6145),
            (55.7535, 37.6168),
            (55.7512, 37.6184),
            (55.7468, 37.6200),
            (55.7425, 37.6204),
        ],
        schedule_hhmm=["07:50", "08:10", "08:30", "08:50", "09:10", "09:30"],
        destination="Tech District",
    ),
}

STOP_TO_ROUTE_IDS: Dict[str, List[str]] = {}
for route in ROUTES.values():
    for stop_id in route.stop_ids:
        STOP_TO_ROUTE_IDS.setdefault(stop_id, []).append(route.id)
