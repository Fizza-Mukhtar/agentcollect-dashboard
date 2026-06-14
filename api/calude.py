"""
api/claude.py

Vercel serverless function that proxies requests to the Anthropic API.
The ANTHROPIC_API_KEY is read from Vercel's Environment Variables (set in
the Vercel dashboard, NEVER hardcoded here).
"""

import os
import json
from anthropic import Anthropic

client = Anthropic()  # reads ANTHROPIC_API_KEY from env (set in Vercel dashboard)


def handler(request):
    if request.method == "OPTIONS":
        return _response(200, {})

    if request.method != "POST":
        return _response(405, {"error": "Method not allowed"})

    try:
        body = json.loads(request.body)
    except Exception:
        return _response(400, {"error": "Invalid JSON body"})

    system_prompt = body.get("system", "")
    user_prompt = body.get("prompt", "")
    max_tokens = body.get("max_tokens", 500)

    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        text = message.content[0].text
        return _response(200, {"text": text})

    except Exception as e:
        return _response(500, {"error": str(e)})


def _response(status, body_dict):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        },
        "body": json.dumps(body_dict),
    }