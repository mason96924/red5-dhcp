"""models.py -- Pydantic schemas for the Red5-DHCP BMS API."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class PointValue(BaseModel):
    tag: str
    suffix: str
    system: str
    device_id: str
    device_type: str
    area: str
    panel: str
    controller: str
    description: str
    io_type: str          # AI / AO / BI / BO
    units: str
    kind: str             # temp / rh / percent / status / command / ...
    sp: bool = False
    trend: bool = False
    notes: str = ""
    # live
    value: Optional[float] = None    # numeric points
    state: Optional[bool] = None     # binary points
    display: str = ""                # human display string
    alarm: bool = False              # currently in alarm


class DeviceState(BaseModel):
    id: str
    type: str
    system: str
    area: str
    panel: str
    controller: str
    running: Optional[bool] = None   # None for passive interfaces/meters
    locked: bool = False             # forced off (season / interlock)
    status: str = "ok"               # ok | off | alarm | standby
    summary: str = ""                # short one-line metric for the tile
    alarms: int = 0
    points: List[PointValue] = []


class SystemSummary(BaseModel):
    name: str
    devices: int
    running: int
    points: int
    alarms: int


class Driver(BaseModel):
    load_pct: float
    oat_c: float
    oa_rh: float
    wetbulb_c: float
    heating_season: bool
    occupied: bool


class Snapshot(BaseModel):
    ts: str
    service: str = "red5-dhcp"
    driver: Driver
    systems: List[SystemSummary]
    devices: List[DeviceState]
    alarms: int
    point_count: int
    device_count: int
    panel_count: int
    controller_count: int
