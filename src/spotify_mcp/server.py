#!/usr/bin/env python3
"""Spotify MCP Server - Main server implementation using FastMCP."""

import json
from typing import Optional

from mcp.server.fastmcp import Context, FastMCP
from pydantic import BaseModel, Field
from smithery.decorators import smithery

from .auth import SpotifyAuth


class ConfigSchema(BaseModel):
    """Configuration schema for Spotify MCP server."""

    spotify_client_id: str = Field(
        ...,
        description="Your Spotify application client ID from https://developer.spotify.com/dashboard"
    )


# Define scopes for user access
SCOPES = [
    "user-read-private",
    "user-read-email",
    "user-library-read",
    "user-library-modify",
    "playlist-read-private",
    "playlist-read-collaborative",
    "playlist-modify-public",
    "playlist-modify-private",
    "user-top-read",
    "user-read-recently-played",
    "user-read-playback-state",
    "user-modify-playback-state",
    "user-read-currently-playing",
]


@smithery.server(config_schema=ConfigSchema)
def create_server():
    """Create and return a FastMCP server instance with session config."""

    mcp = FastMCP("Spotify MCP Server")

    # Initialize auth (will be done per-session via context)
    def get_spotify_client(ctx: Context):
        """Get authenticated Spotify client from context."""
        config = ctx.session_config

        # Create auth instance for this session
        if not hasattr(ctx, '_spotify_auth'):
            ctx._spotify_auth = SpotifyAuth(
                client_id=config.spotify_client_id,
                redirect_uri="http://127.0.0.1:8888/callback",
                scopes=SCOPES,
            )

        return ctx._spotify_auth.authenticate()

    @mcp.tool()
    def search_tracks(query: str, limit: int = 10, ctx: Context = None) -> str:
        """Search for tracks on Spotify.

        Args:
            query: Search query for tracks
            limit: Maximum number of results to return (default: 10)
        """
        client = get_spotify_client(ctx)
        results = client.search(q=query, type="track", limit=min(limit, 50))
        return json.dumps(results, indent=2)

    @mcp.tool()
    def get_track(track_id: str, ctx: Context = None) -> str:
        """Get detailed information about a specific track by ID.

        Args:
            track_id: Spotify track ID
        """
        client = get_spotify_client(ctx)
        track = client.track(track_id)
        return json.dumps(track, indent=2)

    @mcp.tool()
    def search_artists(query: str, limit: int = 10, ctx: Context = None) -> str:
        """Search for artists on Spotify.

        Args:
            query: Search query for artists
            limit: Maximum number of results to return (default: 10)
        """
        client = get_spotify_client(ctx)
        results = client.search(q=query, type="artist", limit=min(limit, 50))
        return json.dumps(results, indent=2)

    @mcp.tool()
    def get_artist(artist_id: str, ctx: Context = None) -> str:
        """Get detailed information about a specific artist by ID.

        Args:
            artist_id: Spotify artist ID
        """
        client = get_spotify_client(ctx)
        artist = client.artist(artist_id)
        return json.dumps(artist, indent=2)

    @mcp.tool()
    def get_artist_top_tracks(artist_id: str, market: str = "US", ctx: Context = None) -> str:
        """Get top tracks for a specific artist.

        Args:
            artist_id: Spotify artist ID
            market: ISO 3166-1 alpha-2 country code (default: US)
        """
        client = get_spotify_client(ctx)
        tracks = client.artist_top_tracks(artist_id, country=market)
        return json.dumps(tracks, indent=2)

    @mcp.tool()
    def search_albums(query: str, limit: int = 10, ctx: Context = None) -> str:
        """Search for albums on Spotify.

        Args:
            query: Search query for albums
            limit: Maximum number of results to return (default: 10)
        """
        client = get_spotify_client(ctx)
        results = client.search(q=query, type="album", limit=min(limit, 50))
        return json.dumps(results, indent=2)

    @mcp.tool()
    def get_album(album_id: str, ctx: Context = None) -> str:
        """Get detailed information about a specific album by ID.

        Args:
            album_id: Spotify album ID
        """
        client = get_spotify_client(ctx)
        album = client.album(album_id)
        return json.dumps(album, indent=2)

    @mcp.tool()
    def search_playlists(query: str, limit: int = 10, ctx: Context = None) -> str:
        """Search for playlists on Spotify.

        Args:
            query: Search query for playlists
            limit: Maximum number of results to return (default: 10)
        """
        client = get_spotify_client(ctx)
        results = client.search(q=query, type="playlist", limit=min(limit, 50))
        return json.dumps(results, indent=2)

    @mcp.tool()
    def get_playlist(playlist_id: str, ctx: Context = None) -> str:
        """Get detailed information about a specific playlist by ID.

        Args:
            playlist_id: Spotify playlist ID
        """
        client = get_spotify_client(ctx)
        playlist = client.playlist(playlist_id)
        return json.dumps(playlist, indent=2)

    @mcp.tool()
    def get_current_user(ctx: Context = None) -> str:
        """Get the current user's profile information."""
        client = get_spotify_client(ctx)
        user = client.current_user()
        return json.dumps(user, indent=2)

    @mcp.tool()
    def get_user_playlists(limit: int = 20, ctx: Context = None) -> str:
        """Get the current user's playlists.

        Args:
            limit: Maximum number of results to return (default: 20)
        """
        client = get_spotify_client(ctx)
        playlists = client.current_user_playlists(limit=min(limit, 50))
        return json.dumps(playlists, indent=2)

    @mcp.tool()
    def get_user_top_tracks(
        limit: int = 20,
        time_range: str = "medium_term",
        ctx: Context = None
    ) -> str:
        """Get the current user's top tracks.

        Args:
            limit: Maximum number of results to return (default: 20)
            time_range: Time range - short_term (4 weeks), medium_term (6 months), long_term (years)
        """
        client = get_spotify_client(ctx)
        tracks = client.current_user_top_tracks(
            limit=min(limit, 50),
            time_range=time_range
        )
        return json.dumps(tracks, indent=2)

    @mcp.tool()
    def get_user_top_artists(
        limit: int = 20,
        time_range: str = "medium_term",
        ctx: Context = None
    ) -> str:
        """Get the current user's top artists.

        Args:
            limit: Maximum number of results to return (default: 20)
            time_range: Time range - short_term (4 weeks), medium_term (6 months), long_term (years)
        """
        client = get_spotify_client(ctx)
        artists = client.current_user_top_artists(
            limit=min(limit, 50),
            time_range=time_range
        )
        return json.dumps(artists, indent=2)

    @mcp.tool()
    def get_recently_played(limit: int = 20, ctx: Context = None) -> str:
        """Get the current user's recently played tracks.

        Args:
            limit: Maximum number of results to return (default: 20)
        """
        client = get_spotify_client(ctx)
        tracks = client.current_user_recently_played(limit=min(limit, 50))
        return json.dumps(tracks, indent=2)

    return mcp
