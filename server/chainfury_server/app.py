import requests
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from chainfury_server.utils import folder, joinp
from chainfury_server.database import add_default_templates, add_default_user

# API function imports
import chainfury_server.api.user as api_user
import chainfury_server.api.chains as api_chains
import chainfury_server.api.prompts as api_prompts
from chainfury_server.landing import landing_page

app = FastAPI(
    title="ChainFury",
    description="ChainFury server changes the game for using Software 2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

add_default_user()
add_default_templates()

# v2 APIs (Koval)
# ---------------

# TODO: deprecate this
app.add_api_route("/api/v1/chatbot/{id}/prompt", api_chains.run_chain, methods=["POST"], tags=["deprecated"], response_model=None)  # type: ignore

app.add_api_route("/", landing_page, methods=["GET"], tags=["deprecated"], response_class=HTMLResponse)  # type: ignore

# user
app.add_api_route("/user/login/", api_user.login, methods=["POST"], tags=["user"])  # type: ignore
app.add_api_route("/user/signup/", api_user.sign_up, methods=["POST"], tags=["user"])  # type: ignore
app.add_api_route("/user/change_password/", api_user.change_password, methods=["POST"], tags=["user"])  # type: ignore

# chains
app.add_api_route("/api/chains/", api_chains.list_chains, methods=["GET"], tags=["chains"])  # type: ignore
app.add_api_route("/api/chains/", api_chains.create_chain, methods=["PUT"], tags=["chains"])  # type: ignore
app.add_api_route("/api/chains/{id}/", api_chains.get_chain, methods=["GET"], tags=["chains"])  # type: ignore
app.add_api_route("/api/chains/{id}/", api_chains.delete_chain, methods=["DELETE"], tags=["chains"])  # type: ignore
app.add_api_route("/api/chains/{id}/", api_chains.update_chain, methods=["PATCH"], tags=["chains"])  # type: ignore
app.add_api_route("/api/chains/{id}/", api_chains.run_chain, methods=["POST"], tags=["chains"], response_model=None)  # type: ignore
app.add_api_route("/api/chains/{id}/metrics/", api_chains.get_chain_metrics, methods=["GET"], tags=["chains"])  # type: ignore

# prompts
app.add_api_route("/api/prompts/", api_prompts.list_prompts, methods=["GET"], tags=["prompts"])  # type: ignore
app.add_api_route("/api/prompts/{prompt_id}/", api_prompts.get_prompt, methods=["GET"], tags=["prompts"])  # type: ignore
app.add_api_route("/api/prompts/{prompt_id}/", api_prompts.delete_prompt, methods=["DELETE"], tags=["prompts"])  # type: ignore
app.add_api_route("/api/prompts/{prompt_id}/feedback", api_prompts.prompt_feedback, methods=["PUT"], tags=["prompts"])  # type: ignore


# Static files
# ------------

# add static files
_static_fp = joinp(folder(__file__), "static")
static = Jinja2Templates(directory=_static_fp)


@app.get("/ui/{rest_of_path:path}")
async def serve_ui(request: Request, rest_of_path: str):
    """Serves the files for dashboard"""
    return static.TemplateResponse("index.html", {"request": request})


app.mount("/", StaticFiles(directory=_static_fp), name="assets")
