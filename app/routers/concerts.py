from __future__ import annotations

import binascii
import struct
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import extract, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.concert import Concert
from app.schemas.concert import ConcertResponse

router = APIRouter(prefix="/concerts", tags=["concerts"])


def _wkb_to_lat_lng(wkb_element: object) -> tuple[float, float] | tuple[None, None]:
    """Decode a GeoAlchemy2 WKBElement to (lat, lng) without requiring Shapely."""
    try:
        # .desc holds the hex-encoded WKB string
        raw = binascii.unhexlify(wkb_element.desc)  # type: ignore[union-attr]
        byte_order = raw[0]
        fmt = "<dd" if byte_order == 1 else ">dd"
        x, y = struct.unpack_from(fmt, raw, 5)
        return y, x  # (lat, lng)
    except Exception:
        return None, None


def _serialize(concert: Concert) -> ConcertResponse:
    lat = lng = None
    if concert.location_geopoint is not None:
        lat, lng = _wkb_to_lat_lng(concert.location_geopoint)
    return ConcertResponse(
        id=concert.id,
        concert_date=concert.concert_date,
        venue=concert.venue,
        city=concert.city,
        state_province=concert.state_province,
        state_abbr=concert.state_abbr,
        country=concert.country,
        lat=lat,
        lng=lng,
        setlist_url=concert.setlist_url,
    )


@router.get("", response_model=list[ConcertResponse])
async def list_concerts(
    year: int = Query(default=date.today().year, ge=1983),
    db: AsyncSession = Depends(get_db),
) -> list[ConcertResponse]:
    result = await db.execute(
        select(Concert)
        .where(extract("year", Concert.concert_date) == year)
        .order_by(Concert.concert_date)
    )
    return [_serialize(c) for c in result.scalars().all()]
