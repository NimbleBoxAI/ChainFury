import requests
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from chainfury_server.commons.utils import folder, joinp, logger
from chainfury_server.database import add_default_templates, add_default_user

# Routers
from chainfury_server.api.chatbot import chatbot_router
from chainfury_server.api.prompts import router as prompts_router
from chainfury_server.api.fury import fury_router

# v2
import chainfury_server.api.auth as api_auth
import chainfury_server.api_v2.chains as api_chains
import chainfury_server.api_v2.fury as api_fury
import chainfury_server.api_v2.prompts as api_prompts

from chainfury_server.plugins import get_phandler


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

####################################################
################ INITIALIZE ########################
####################################################

# TODO: deprecate this
app.add_api_route("/api/v1/prompts/{id}/prompt", api_chains.run_chain, methods=["POST"], tags=["deprecated"])  # type: ignore


####################################################
################ v2 APIs (Koval) ###################
####################################################

# auth endpoints for v2
app.add_api_route("/user/login/", api_auth.login, methods=["POST"], tags=["auth"])  # type: ignore
app.add_api_route("/user/signup/", api_auth.sign_up, methods=["POST"], tags=["auth"])  # type: ignore
app.add_api_route("/user/change_password/", api_auth.change_password, methods=["POST"], tags=["auth"])  # type: ignore

# chains
app.add_api_route("/api/v2/chains/", api_chains.list_chatbots, methods=["GET"], tags=["chains"])  # type: ignore
app.add_api_route("/api/v2/chains/", api_chains.create_chatbot, methods=["PUT"], tags=["chains"])  # type: ignore
app.add_api_route("/api/v2/chains/{id}/", api_chains.get_chatbot, methods=["GET"], tags=["chains"])  # type: ignore
app.add_api_route("/api/v2/chains/{id}/", api_chains.delete_chatbot, methods=["DELETE"], tags=["chains"])  # type: ignore
app.add_api_route("/api/v2/chains/{id}/", api_chains.update_chatbot, methods=["PATCH"], tags=["chains"])  # type: ignore
app.add_api_route("/api/v2/chains/{id}/", api_chains.run_chain, methods=["POST"], tags=["chains"])  # type: ignore
app.add_api_route("/api/v2/chains/{id}/metrics/", api_chains.get_chain_metrics, methods=["GET"], tags=["chains"])  # type: ignore

# actions
app.add_api_route("/api/v2/fury/", api_fury.list_actions, methods=["GET"], tags=["fury"])  # type: ignore
app.add_api_route("/api/v2/fury/", api_fury.create_action, methods=["PUT"], tags=["fury"])  # type: ignore
app.add_api_route("/api/v2/fury/{id}/", api_fury.get_action, methods=["GET"], tags=["fury"])  # type: ignore
app.add_api_route("/api/v2/fury/{id}/", api_fury.delete_action, methods=["DELETE"], tags=["fury"])  # type: ignore
app.add_api_route("/api/v2/fury/{id}/", api_fury.update_action, methods=["PATCH"], tags=["fury"])  # type: ignore
# app.add_api_route("/api/v2/fury/{id}/", fury.run_action, methods=["POST"], tags=["fury"])  # type: ignore

# prompts
app.add_api_route("/api/v2/prompts/", api_prompts.list_prompts, methods=["GET"], tags=["prompts"])  # type: ignore
app.add_api_route("/api/v2/prompts/{prompt_id}/", api_prompts.get_prompt, methods=["GET"], tags=["prompts"])  # type: ignore
app.add_api_route("/api/v2/prompts/{prompt_id}/", api_prompts.delete_prompt, methods=["DELETE"], tags=["prompts"])  # type: ignore
app.add_api_route("/api/v2/prompts/{prompt_id}/feedback", api_prompts.prompt_feedback, methods=["PUT"], tags=["prompts"])  # type: ignore


####################################################
################ APIs ##############################
####################################################


# get https://chainfury.framer.website/ and serve on /
@app.get("/")
async def serve_framer():
    """Serves the landing page for ChainFury"""
    r = requests.get("https://chainfury.framer.website/")
    return HTMLResponse(content=r.text, status_code=r.status_code)


# add static files
_static_fp = joinp(folder(__file__), "static")
static = Jinja2Templates(directory=_static_fp)


@app.get("/ui/{rest_of_path:path}")
async def serve_ui(request: Request, rest_of_path: str):
    """Serves the files for dashboard"""
    return static.TemplateResponse("index.html", {"request": request})


app.mount("/", StaticFiles(directory=_static_fp), name="assets")

# warmup and initialize plugins
get_phandler()
