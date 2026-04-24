"""Pydantic schemas for OpenSky responses."""

from __future__ import annotations

from pydantic import BaseModel


class StateVector(BaseModel):
    """Posição instantânea de uma aeronave (ADS-B)."""

    icao24: str
    callsign: str | None = None
    origin_country: str | None = None
    time_position: int | None = None
    last_contact: int | None = None
    longitude: float | None = None
    latitude: float | None = None
    baro_altitude: float | None = None
    on_ground: bool | None = None
    velocity: float | None = None
    true_track: float | None = None
    vertical_rate: float | None = None
    geo_altitude: float | None = None
    squawk: str | None = None


class Flight(BaseModel):
    """Voo consolidado (decolagem → pouso)."""

    icao24: str
    callsign: str | None = None
    first_seen: int
    last_seen: int
    est_departure_airport: str | None = None
    est_arrival_airport: str | None = None


class TrackPoint(BaseModel):
    """Ponto de trajetória."""

    time: int
    latitude: float | None = None
    longitude: float | None = None
    baro_altitude: float | None = None
    true_track: float | None = None
    on_ground: bool | None = None
