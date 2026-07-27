"""server.py -- Red5-DHCP BMS supervisory service (FastAPI).

A self-contained monitor for the DHC-connected hotel BMS.  The device / point
model is loaded from generate_io_list.py (the same source as the Excel
deliverable) and live values are synthesized by sim.py until real field I/O is
wired in.

Endpoints:
    GET /                 -> dashboard (frontend/index.html)
    GET /api/health       -> liveness + model tallies
    GET /api/snapshot     -> full live snapshot (driver + systems + devices + points)
    GET /api/panels       -> panel / controller schedule summary
    GET /api/points       -> static point catalog (optionally ?system= / ?panel=)
    GET /api/device/{id}  -> one device's live points

Run:  uvicorn backend.server:app --reload --port 8020
"""
from __future__ import annotations

import os
import sys
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from points import DEVICES, POINTS, panel_summary, CONTROLLER_META  # noqa: E402
from sim import build_snapshot                                       # noqa: E402

ROOT = os.path.dirname(_HERE)
FRONTEND_DIR = os.path.join(ROOT, "frontend")

app = FastAPI(title="Red5-DHCP BMS", version="0.1.0-scaffold")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict:
    return {
        "ok": True, "service": "red5-dhcp", "mode": "monitor",
        "points": len(POINTS), "devices": len(DEVICES),
        "controllers": len(CONTROLLER_META),
    }


@app.get("/api/snapshot")
def snapshot() -> JSONResponse:
    return JSONResponse(build_snapshot(datetime.now()))


@app.get("/api/panels")
def panels() -> JSONResponse:
    return JSONResponse(panel_summary())


@app.get("/api/points")
def points(system: str | None = None, panel: str | None = None) -> JSONResponse:
    out = [{k: p[k] for k in ("tag", "system", "device_id", "device_type",
                              "area", "panel", "controller", "description",
                              "io_type", "signal", "units", "kind", "notes")}
           for p in POINTS
           if (system is None or p["system"] == system)
           and (panel is None or p["panel"] == panel)]
    return JSONResponse({"count": len(out), "points": out})


@app.get("/api/device/{dev_id}")
def device(dev_id: str) -> JSONResponse:
    if dev_id not in DEVICES:
        raise HTTPException(status_code=404, detail=f"unknown device '{dev_id}'")
    snap = build_snapshot(datetime.now())
    for d in snap["devices"]:
        if d["id"] == dev_id:
            return JSONResponse(d)
    raise HTTPException(status_code=404, detail=f"'{dev_id}' not in snapshot")


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
