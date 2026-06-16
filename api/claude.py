"""
api/claude.py

Vercel serverless function that proxies requests to the Groq API
(instead of Anthropic). GROQ_API_KEY is read from Vercel's Environment
Variables.

Note: filename kept as claude.py so the existing /api/claude route in
dashboard.html doesn't need to change.
"""

import os
import json
from http.server import BaseHTTPRequestHandler
from groq import Groq


class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self._send_cors_headers(200)

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body_raw = self.rfile.read(content_length)

        try:
            body = json.loads(body_raw)
        except Exception:
            self._send_json(400, {"error": "Invalid JSON body"})
            return

        system_prompt = body.get("system", "")
        user_prompt = body.get("prompt", "")
        max_tokens = body.get("max_tokens", 500)

        try:
            client = Groq()  # reads GROQ_API_KEY from env
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                max_tokens=max_tokens,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            text = completion.choices[0].message.content
            self._send_json(200, {"text": text})

        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def _send_cors_headers(self, status):
        self.send_response(status)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _send_json(self, status, body_dict):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(body_dict).encode())