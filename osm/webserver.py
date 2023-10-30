from web_html import *
from http.server import SimpleHTTPRequestHandler, HTTPServer
from typing import List, Union, Pattern, Callable, Dict, Optional, Sequence, Any

import json

class osm_web_server:
    def __init__(
        self,
        port: int,
        path: str,
        http_server_logger_enabled: bool = True,
    ):
        """Slack App Development Server

        This is a thin wrapper of http.server.HTTPServer and is good enough
        for your local development or prototyping.

        However, as mentioned in Python official documents, using http.server module in production
        is not recommended. Please consider using an adapter (refer to slack_bolt.adapter.*)
        along with a production-grade server when running the app for end users.
        https://docs.python.org/3/library/http.server.html#http.server.HTTPServer

        Args:
            port: the port number
            path: the path to receive incoming requests
            app: the `App` instance to execute
            oauth_flow: the `OAuthFlow` instance to use for OAuth flow
            http_server_logger_enabled: The flag to turn on/off http.server's logging
        """
        self._port: int = port
        self._bolt_endpoint_path: str = path
        self._http_server_logger_enabled = http_server_logger_enabled

        _port: int = self._port
        _bolt_endpoint_path: str = self._bolt_endpoint_path
        _http_server_logger_enabled = self._http_server_logger_enabled

        class SlackAppHandler(SimpleHTTPRequestHandler):
            def log_message(self, format: str, *args: Any) -> None:
                if _http_server_logger_enabled is True:
                    super().log_message(format, *args)

            def do_GET(self):
                self._send_response(200, headers={}, body=generate_front_page('beavers'))

            def do_POST(self):
                self._send_response(200, headers={}, body='')

            def _send_bolt_response(self, response):
                self._send_response(
                    status=response.status,
                    headers=response.headers,
                    body=response.body,
                )

            def _send_response(
                self,
                status: int,
                headers: Dict[str, Sequence[str]],
                body: Union[str, dict] = "",
            ):
                self.send_response(status)

                response_body = body if isinstance(body, str) else json.dumps(body)
                body_bytes = response_body.encode("utf-8")

                for k, vs in headers.items():
                    for v in vs:
                        self.send_header(k, v)
                self.send_header("Content-Length", str(len(body_bytes)))
                self.end_headers()
                self.wfile.write(body_bytes)

        self._server = HTTPServer(("0.0.0.0", self._port), SlackAppHandler)

    def start(self) -> None:
        """Starts a new web server process."""
        # if self.logger.level > logging.INFO:
        #     print(development_server=True)
        # else:
        #     self.logger.info(development_server=True)
        print("development_server=True")
        try:
            self._server.serve_forever(0.05)
        finally:
            self._server.server_close()
    
