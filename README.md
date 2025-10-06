# Spotify MCP Server (Python)

MCP server for Spotify integration using PKCE authentication.

## Features

- PKCE authentication (no client secret needed)
- Automatic token caching and refresh
- 14 Spotify tools for search, user data, and more

## Installation

```bash
cd spotify-mcp-py
pip install -e .
```

## Setup

1. **Create Spotify App** at https://developer.spotify.com/dashboard:
   - Add redirect URI: `http://127.0.0.1:8888/callback`
   - Copy your Client ID

2. **Configure Claude Desktop** at `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "spotify": {
      "command": "python",
      "args": [
        "-m",
        "spotify_mcp.server"
      ],
      "env": {
        "SPOTIFY_CLIENT_ID": "your_client_id_here"
      }
    }
  }
}
```

3. **Restart Claude Desktop** - browser will open for Spotify login on first use

## Available Tools

- `search_tracks` - Search for tracks
- `get_track` - Get track details
- `search_artists` - Search for artists
- `get_artist` - Get artist details
- `get_artist_top_tracks` - Get artist's top tracks
- `search_albums` - Search for albums
- `get_album` - Get album details
- `search_playlists` - Search for playlists
- `get_playlist` - Get playlist details
- `get_current_user` - Get user profile
- `get_user_playlists` - Get user's playlists
- `get_user_top_tracks` - Get user's top tracks
- `get_user_top_artists` - Get user's top artists
- `get_recently_played` - Get recently played tracks

## Token Cache

Tokens are cached in `~/.spotify-mcp/token-cache.json` and automatically refreshed.
