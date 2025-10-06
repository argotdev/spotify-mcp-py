"""Spotify PKCE authentication module."""

import hashlib
import secrets
import base64
import json
import webbrowser
from pathlib import Path
from typing import Optional
from urllib.parse import urlencode
import time

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from .oauth_server import start_oauth_callback_server


class SpotifyAuth:
    """Handles Spotify authentication using PKCE flow."""

    def __init__(
        self,
        client_id: str,
        redirect_uri: str,
        scopes: list[str],
        cache_dir: Optional[str] = None,
    ):
        """
        Initialize Spotify authenticator.

        Args:
            client_id: Spotify application client ID
            redirect_uri: OAuth redirect URI (must use 127.0.0.1)
            scopes: List of Spotify API scopes to request
            cache_dir: Directory to cache tokens (default: ~/.spotify-mcp)
        """
        self.client_id = client_id
        self.redirect_uri = redirect_uri
        self.scopes = scopes

        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path.home() / ".spotify-mcp"

        self.token_cache_path = self.cache_dir / "token-cache.json"
        self._spotify_client: Optional[spotipy.Spotify] = None

    def _generate_code_verifier(self) -> str:
        """Generate PKCE code verifier."""
        code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32))
        return code_verifier.decode('utf-8').rstrip('=')

    def _generate_code_challenge(self, verifier: str) -> str:
        """Generate PKCE code challenge from verifier."""
        digest = hashlib.sha256(verifier.encode('utf-8')).digest()
        code_challenge = base64.urlsafe_b64encode(digest)
        return code_challenge.decode('utf-8').rstrip('=')

    def _load_token_cache(self) -> Optional[dict]:
        """Load cached tokens from disk."""
        try:
            if self.token_cache_path.exists():
                with open(self.token_cache_path, 'r') as f:
                    cache = json.load(f)

                # Check if token is still valid (with 5 minute buffer)
                if cache.get('expires_at', 0) > time.time() + 300:
                    return cache

                # If we have a refresh token, return cache so we can refresh
                if cache.get('refresh_token'):
                    return cache

            return None
        except Exception:
            return None

    def _save_token_cache(self, token_info: dict) -> None:
        """Save tokens to disk cache."""
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

            cache = {
                'access_token': token_info['access_token'],
                'token_type': token_info['token_type'],
                'expires_in': token_info['expires_in'],
                'refresh_token': token_info.get('refresh_token', ''),
                'scope': token_info['scope'],
                'expires_at': int(time.time()) + token_info['expires_in'],
            }

            with open(self.token_cache_path, 'w') as f:
                json.dump(cache, f, indent=2)

        except Exception as e:
            print(f"Failed to save token cache: {e}", flush=True)

    def authenticate(self) -> spotipy.Spotify:
        """
        Authenticate with Spotify using PKCE flow.

        Returns:
            Authenticated Spotipy client

        Raises:
            Exception: If authentication fails
        """
        if self._spotify_client:
            return self._spotify_client

        # Try to load cached tokens
        cached_tokens = self._load_token_cache()

        if cached_tokens:
            # Check if token needs refresh
            if cached_tokens['expires_at'] <= time.time() + 300:
                print("Access token expired, refreshing...", flush=True)
                try:
                    auth_manager = SpotifyOAuth(
                        client_id=self.client_id,
                        redirect_uri=self.redirect_uri,
                        scope=' '.join(self.scopes),
                        open_browser=False,
                    )

                    new_tokens = auth_manager.refresh_access_token(
                        cached_tokens['refresh_token']
                    )

                    # Keep the refresh token if not provided in response
                    if 'refresh_token' not in new_tokens:
                        new_tokens['refresh_token'] = cached_tokens['refresh_token']

                    self._save_token_cache(new_tokens)
                    self._spotify_client = spotipy.Spotify(
                        auth=new_tokens['access_token']
                    )
                    return self._spotify_client

                except Exception as e:
                    print(f"Failed to refresh token, starting new auth flow: {e}",
                          flush=True)
                    # Continue to full auth flow below
            else:
                print("Using cached access token", flush=True)
                self._spotify_client = spotipy.Spotify(
                    auth=cached_tokens['access_token']
                )
                return self._spotify_client

        # Start full PKCE auth flow
        print("Starting Spotify authentication...", flush=True)

        code_verifier = self._generate_code_verifier()
        code_challenge = self._generate_code_challenge(code_verifier)
        state = secrets.token_hex(16)

        auth_params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'code_challenge_method': 'S256',
            'code_challenge': code_challenge,
            'state': state,
            'scope': ' '.join(self.scopes),
        }

        auth_url = f"https://accounts.spotify.com/authorize?{urlencode(auth_params)}"

        print("Opening browser for authentication...", flush=True)
        print(f"If the browser doesn't open, visit: {auth_url}", flush=True)

        # Start callback server and open browser
        webbrowser.open(auth_url)
        callback_result = start_oauth_callback_server(8888)

        if state != callback_result.state:
            raise Exception("State mismatch - possible CSRF attack")

        # Exchange code for tokens using SpotifyOAuth
        auth_manager = SpotifyOAuth(
            client_id=self.client_id,
            redirect_uri=self.redirect_uri,
            scope=' '.join(self.scopes),
            open_browser=False,
        )

        # Manually construct the token request with PKCE
        token_info = auth_manager._request_access_token(
            callback_result.code,
            code_verifier
        )

        self._save_token_cache(token_info)

        print("Authentication successful!", flush=True)
        self._spotify_client = spotipy.Spotify(auth=token_info['access_token'])
        return self._spotify_client

    def get_client(self) -> spotipy.Spotify:
        """
        Get authenticated Spotify client.

        Returns:
            Authenticated Spotipy client

        Raises:
            Exception: If not authenticated
        """
        if not self._spotify_client:
            raise Exception("Not authenticated. Call authenticate() first.")
        return self._spotify_client
