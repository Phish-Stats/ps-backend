"""Database seed script for scaffold data."""

from __future__ import annotations

import asyncio
from collections.abc import Iterable

from passlib.context import CryptContext
from sqlalchemy import select

from geoalchemy2 import WKTElement

from app.database import AsyncSessionLocal
from app.models import Album, Song
from app.models.concert import Concert
from app.models.user import User
from scripts.albums_seed import ALBUMS
from scripts.concerts_seed import CONCERTS_2026
from scripts.songs_seed import ALBUM_SONGS, SONGS

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def seed_albums() -> int:
    seeded = 0
    async with AsyncSessionLocal() as session:
        for album in ALBUMS:
            existing = await session.scalar(select(Album).where(Album.name == album["name"]))
            if existing:
                continue
            session.add(Album(name=album["name"], year=album["year"]))
            seeded += 1

        await session.commit()
    return seeded


async def seed_songs() -> int:
    seeded = 0
    async with AsyncSessionLocal() as session:
        albums = {album.name: album for album in (await session.scalars(select(Album))).all()}
        existing_song_names = {song.name for song in (await session.scalars(select(Song))).all()}

        for album_name, track_names in ALBUM_SONGS.items():
            album = albums.get(album_name)
            if album is None:
                continue

            for track_number, song_name in enumerate(track_names, start=1):
                if song_name in existing_song_names:
                    continue
                session.add(Song(name=song_name, album_id=album.id, track_number=track_number))
                existing_song_names.add(song_name)
                seeded += 1

        seeded_song_names = {song["name"] for song in SONGS}
        mapped_song_names = {track for tracks in ALBUM_SONGS.values() for track in tracks}
        for song in SONGS:
            if song["name"] in mapped_song_names:
                continue
            if song["name"] not in seeded_song_names:
                continue
            if song["name"] in existing_song_names:
                continue
            session.add(Song(**song))
            existing_song_names.add(song["name"])
            seeded += 1

        await session.commit()
    return seeded


def preview_seed_payload() -> dict[str, object]:
    password_hash = pwd_context.hash("ChangeMe123!")
    return {
        "albums": list(ALBUMS),
        "album_count": len(ALBUMS),
        "songs": list(SONGS),
        "song_count": len(SONGS),
        "example_password_hash": password_hash,
    }


def print_album_summary(albums: Iterable[dict[str, int | str]]) -> None:
    for album in albums:
        print(f"- {album['name']} ({album['year']})")


async def seed_concerts() -> int:
    from datetime import date
    seeded = 0
    async with AsyncSessionLocal() as session:
        for c in CONCERTS_2026:
            concert_date = date.fromisoformat(c["date"])
            existing = await session.scalar(
                select(Concert).where(Concert.concert_date == concert_date)
            )
            if existing:
                continue
            geopoint = WKTElement(f"POINT({c['lng']} {c['lat']})", srid=4326)
            session.add(Concert(
                concert_date=concert_date,
                venue=c["venue"],
                city=c["city"],
                state_province=c["state_province"],
                state_abbr=c["state_abbr"],
                country=c["country"],
                location_geopoint=geopoint,
                setlist_url=c["setlist_url"],
            ))
            seeded += 1
        await session.commit()
    return seeded


async def seed_test_user() -> int:
    async with AsyncSessionLocal() as session:
        existing = await session.scalar(select(User).where(User.email_address == "test@email.com"))
        if existing:
            return 0
        session.add(User(
            first_name="Test",
            last_name="User",
            email_address="test@email.com",
            password_hash=pwd_context.hash("Password123"),
            slug="test-user",
        ))
        await session.commit()
    return 1


async def main() -> None:
    seeded_albums = await seed_albums()
    seeded_songs = await seed_songs()
    seeded_concerts = await seed_concerts()
    seeded_users = await seed_test_user()
    payload = preview_seed_payload()
    print(f"Inserted {seeded_albums} new albums.")
    print(f"Inserted {seeded_songs} new songs.")
    print(f"Inserted {seeded_concerts} new concerts.")
    print(f"Inserted {seeded_users} test user(s).")
    print_album_summary(payload["albums"])


if __name__ == "__main__":
    asyncio.run(main())
