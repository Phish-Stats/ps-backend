from __future__ import annotations

import uuid
from datetime import date

from pydantic import BaseModel


class ConcertResponse(BaseModel):
    id: uuid.UUID
    concert_date: date
    venue: str | None
    city: str
    state_province: str | None
    state_abbr: str | None
    country: str
    lat: float | None
    lng: float | None
    setlist_url: str | None
