# Copyright © 2023- Frello Technology Private Limited

# this is the landing page UI for the app

from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from chainfury_server.utils import folder, joinp


async def landing_page():
    """Serves the landing page for ChainFury"""

    return HTMLResponse(
        status_code=200,
        content="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ChainFury Page</title>
    <style>
        /* Basic styling for better appearance */
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            margin: 50px;
        }
        img {
            width: 512px;
            height: 512px;
        }
        h1 {
            font-size: 32px;
        }
        h2 {
            font-size: 24px;
            color: #666;
        }
        .btn {
            display: inline-block;
            padding: 10px 20px;
            margin: 10px;
            border: none;
            background-color: #007BFF;
            color: #fff;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <!-- Image with cloudflare URL -->
    <img src="https://d2e931syjhr5o9.cloudfront.net/tune-research/assets/tune_pruple_with_orange_padding.png" alt="Tune AI logo">

    <!-- Subtitle below image -->
    <h2>ChainFury is the Apache-2.0 OSS Chaining Engine behind TuneChat</h2>

    <!-- Three buttons -->
    <a href="https://github.com/NimbleBoxAI/ChainFury" class="btn" target="_blank">GitHub</a>
    <a href="https://nimbleboxai.github.io/ChainFury/" class="btn" target="_blank">Documentation</a>
    <a href="https://chat.tune.app/" class="btn" target="_blank">TuneChat</a>
</body>
</html>

""",
    )


# add static files
static_fp = joinp(folder(__file__), "static")
static = Jinja2Templates(directory=static_fp)


async def serve_ui(request: Request, rest_of_path: str):
    """Serves the files for dashboard"""
    return static.TemplateResponse("index.html", {"request": request})
