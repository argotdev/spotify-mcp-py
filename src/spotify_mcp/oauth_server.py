"""OAuth callback server for handling Spotify PKCE authentication."""

import http.server
import socketserver
from typing import Optional
from urllib.parse import urlparse, parse_qs
import threading


class OAuthCallbackResult:
    """Result from OAuth callback."""

    def __init__(self, code: str, state: str):
        self.code = code
        self.state = state


class OAuthCallbackHandler(http.server.BaseHTTPRequestHandler):
    """HTTP request handler for OAuth callback."""

    result: Optional[OAuthCallbackResult] = None
    error: Optional[str] = None

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass

    def do_GET(self):
        """Handle GET request to callback endpoint."""
        parsed_url = urlparse(self.path)

        if parsed_url.path == '/callback':
            query_params = parse_qs(parsed_url.query)

            error = query_params.get('error', [None])[0]
            if error:
                self.send_response(400)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(f"""
                    <html>
                        <body>
                            <h1>Authentication Failed</h1>
                            <p>Error: {error}</p>
                            <p>You can close this window.</p>
                        </body>
                    </html>
                """.encode())
                OAuthCallbackHandler.error = error
                return

            code = query_params.get('code', [None])[0]
            state = query_params.get('state', [None])[0]

            if not code or not state:
                self.send_response(400)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(b"""
                    <html>
                        <body>
                            <h1>Authentication Failed</h1>
                            <p>Missing code or state parameter.</p>
                            <p>You can close this window.</p>
                        </body>
                    </html>
                """)
                OAuthCallbackHandler.error = "Missing code or state"
                return

            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
                <html>
                    <body>
                        <h1>Authentication Successful!</h1>
                        <p>You have successfully authenticated with Spotify.</p>
                        <p>You can close this window and return to Claude Desktop.</p>
                        <script>window.close();</script>
                    </body>
                </html>
            """)

            OAuthCallbackHandler.result = OAuthCallbackResult(code, state)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not found')


def start_oauth_callback_server(port: int = 8888) -> OAuthCallbackResult:
    """
    Start OAuth callback server and wait for callback.

    Args:
        port: Port to listen on (default: 8888)

    Returns:
        OAuthCallbackResult with code and state

    Raises:
        Exception: If OAuth callback fails
    """
    OAuthCallbackHandler.result = None
    OAuthCallbackHandler.error = None

    with socketserver.TCPServer(("127.0.0.1", port), OAuthCallbackHandler) as httpd:
        print(f"OAuth callback server listening on http://127.0.0.1:{port}/callback",
              flush=True)

        # Handle requests until we get a result or error
        while OAuthCallbackHandler.result is None and OAuthCallbackHandler.error is None:
            httpd.handle_request()

        if OAuthCallbackHandler.error:
            raise Exception(f"OAuth error: {OAuthCallbackHandler.error}")

        if OAuthCallbackHandler.result is None:
            raise Exception("OAuth callback failed")

        return OAuthCallbackHandler.result
