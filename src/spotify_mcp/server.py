#!/usr/bin/env python3
"""Spotify MCP Server - Main server implementation."""

import asyncio
import os
import sys
from typing import Any

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp import types

from .auth import SpotifyAuth


# Get credentials from environment variables
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")

if not SPOTIFY_CLIENT_ID:
    print("Error: SPOTIFY_CLIENT_ID environment variable is required", file=sys.stderr)
    sys.exit(1)

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

# Initialize auth
spotify_auth = SpotifyAuth(
    client_id=SPOTIFY_CLIENT_ID,
    redirect_uri="http://127.0.0.1:8888/callback",
    scopes=SCOPES,
)

# Create server instance
server = Server("spotify-mcp-server")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available Spotify tools."""
    return [
        types.Tool(
            name="search_tracks",
            description="Search for tracks on Spotify",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for tracks",
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of results to return (default: 10)",
                        "default": 10,
                    },
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="get_track",
            description="Get detailed information about a specific track by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "track_id": {
                        "type": "string",
                        "description": "Spotify track ID",
                    },
                },
                "required": ["track_id"],
            },
        ),
        types.Tool(
            name="search_artists",
            description="Search for artists on Spotify",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for artists",
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of results to return (default: 10)",
                        "default": 10,
                    },
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="get_artist",
            description="Get detailed information about a specific artist by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "artist_id": {
                        "type": "string",
                        "description": "Spotify artist ID",
                    },
                },
                "required": ["artist_id"],
            },
        ),
        types.Tool(
            name="get_artist_top_tracks",
            description="Get top tracks for a specific artist",
            inputSchema={
                "type": "object",
                "properties": {
                    "artist_id": {
                        "type": "string",
                        "description": "Spotify artist ID",
                    },
                    "market": {
                        "type": "string",
                        "description": "ISO 3166-1 alpha-2 country code (default: US)",
                        "default": "US",
                    },
                },
                "required": ["artist_id"],
            },
        ),
        types.Tool(
            name="search_albums",
            description="Search for albums on Spotify",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for albums",
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of results to return (default: 10)",
                        "default": 10,
                    },
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="get_album",
            description="Get detailed information about a specific album by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "album_id": {
                        "type": "string",
                        "description": "Spotify album ID",
                    },
                },
                "required": ["album_id"],
            },
        ),
        types.Tool(
            name="search_playlists",
            description="Search for playlists on Spotify",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for playlists",
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of results to return (default: 10)",
                        "default": 10,
                    },
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="get_playlist",
            description="Get detailed information about a specific playlist by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "playlist_id": {
                        "type": "string",
                        "description": "Spotify playlist ID",
                    },
                },
                "required": ["playlist_id"],
            },
        ),
        types.Tool(
            name="get_current_user",
            description="Get the current user's profile information",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="get_user_playlists",
            description="Get the current user's playlists",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of results to return (default: 20)",
                        "default": 20,
                    },
                },
            },
        ),
        types.Tool(
            name="get_user_top_tracks",
            description="Get the current user's top tracks",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of results to return (default: 20)",
                        "default": 20,
                    },
                    "time_range": {
                        "type": "string",
                        "description": "Time range: short_term (4 weeks), medium_term (6 months), long_term (several years)",
                        "enum": ["short_term", "medium_term", "long_term"],
                        "default": "medium_term",
                    },
                },
            },
        ),
        types.Tool(
            name="get_user_top_artists",
            description="Get the current user's top artists",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of results to return (default: 20)",
                        "default": 20,
                    },
                    "time_range": {
                        "type": "string",
                        "description": "Time range: short_term (4 weeks), medium_term (6 months), long_term (several years)",
                        "enum": ["short_term", "medium_term", "long_term"],
                        "default": "medium_term",
                    },
                },
            },
        ),
        types.Tool(
            name="get_recently_played",
            description="Get the current user's recently played tracks",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of results to return (default: 20)",
                        "default": 20,
                    },
                },
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any]
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls."""
    import json

    try:
        # Authenticate (will use cached token if available)
        client = spotify_auth.authenticate()

        if name == "search_tracks":
            query = arguments["query"]
            limit = min(arguments.get("limit", 10), 50)
            results = client.search(q=query, type="track", limit=limit)

            return [types.TextContent(type="text", text=json.dumps(results, indent=2))]

        elif name == "get_track":
            track_id = arguments["track_id"]
            track = client.track(track_id)

            return [types.TextContent(type="text", text=json.dumps(track, indent=2))]

        elif name == "search_artists":
            query = arguments["query"]
            limit = min(arguments.get("limit", 10), 50)
            results = client.search(q=query, type="artist", limit=limit)

            return [types.TextContent(type="text", text=json.dumps(results, indent=2))]

        elif name == "get_artist":
            artist_id = arguments["artist_id"]
            artist = client.artist(artist_id)

            return [types.TextContent(type="text", text=json.dumps(artist, indent=2))]

        elif name == "get_artist_top_tracks":
            artist_id = arguments["artist_id"]
            market = arguments.get("market", "US")
            tracks = client.artist_top_tracks(artist_id, country=market)

            return [types.TextContent(type="text", text=json.dumps(tracks, indent=2))]

        elif name == "search_albums":
            query = arguments["query"]
            limit = min(arguments.get("limit", 10), 50)
            results = client.search(q=query, type="album", limit=limit)

            return [types.TextContent(type="text", text=json.dumps(results, indent=2))]

        elif name == "get_album":
            album_id = arguments["album_id"]
            album = client.album(album_id)

            return [types.TextContent(type="text", text=json.dumps(album, indent=2))]

        elif name == "search_playlists":
            query = arguments["query"]
            limit = min(arguments.get("limit", 10), 50)
            results = client.search(q=query, type="playlist", limit=limit)

            return [types.TextContent(type="text", text=json.dumps(results, indent=2))]

        elif name == "get_playlist":
            playlist_id = arguments["playlist_id"]
            playlist = client.playlist(playlist_id)

            return [types.TextContent(type="text", text=json.dumps(playlist, indent=2))]

        elif name == "get_current_user":
            user = client.current_user()

            return [types.TextContent(type="text", text=json.dumps(user, indent=2))]

        elif name == "get_user_playlists":
            limit = min(arguments.get("limit", 20), 50)
            playlists = client.current_user_playlists(limit=limit)

            return [types.TextContent(type="text", text=json.dumps(playlists, indent=2))]

        elif name == "get_user_top_tracks":
            limit = min(arguments.get("limit", 20), 50)
            time_range = arguments.get("time_range", "medium_term")
            tracks = client.current_user_top_tracks(limit=limit, time_range=time_range)

            return [types.TextContent(type="text", text=json.dumps(tracks, indent=2))]

        elif name == "get_user_top_artists":
            limit = min(arguments.get("limit", 20), 50)
            time_range = arguments.get("time_range", "medium_term")
            artists = client.current_user_top_artists(limit=limit, time_range=time_range)

            return [types.TextContent(type="text", text=json.dumps(artists, indent=2))]

        elif name == "get_recently_played":
            limit = min(arguments.get("limit", 20), 50)
            tracks = client.current_user_recently_played(limit=limit)

            return [types.TextContent(type="text", text=json.dumps(tracks, indent=2))]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        print("Spotify MCP server running on stdio", file=sys.stderr, flush=True)
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="spotify-mcp-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
