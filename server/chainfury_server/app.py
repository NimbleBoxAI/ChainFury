import requests
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from chainfury_server.commons.utils import folder, joinp, logger
from chainfury_server.database import add_default_templates, add_default_user

# Routers
from chainfury_server.api.auth import auth_router
from chainfury_server.api.chatbot import chatbot_router
from chainfury_server.api.feedback import feedback_router
from chainfury_server.api.langflow import router as langflow_router
from chainfury_server.api.metrics import metrics_router
from chainfury_server.api.prompts import router as prompts_router
from chainfury_server.api.template import template_router
from chainfury_server.api.user import user_router
from chainfury_server.api.fury import fury_router

import chainfury_server.api_v2.chatbot as api_v2_chatbot
import chainfury_server.api_v2.fury as api_v2_fury
import chainfury_server.api_v2.prompts as api_v2_prompts

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
# Registering apis.

app.include_router(auth_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1/user")
app.include_router(feedback_router, prefix="/api/v1")
app.include_router(metrics_router, prefix="/api/v1")
app.include_router(chatbot_router, prefix="/api/v1/chatbot")
app.include_router(prompts_router, prefix="/api/v1/chatbot")
app.include_router(template_router, prefix="/api/v1/template")
app.include_router(fury_router, prefix="/api/v1/fury")
app.include_router(langflow_router, prefix="/api/v1/flow")

# chains
app.add_api_route("/api/v2/chains/", api_v2_chatbot.list_chatbots, methods=["GET"], tags=["v2"])  # type: ignore
app.add_api_route("/api/v2/chains/", api_v2_chatbot.create_chatbot, methods=["PUT"], tags=["v2"])  # type: ignore
app.add_api_route("/api/v2/chains/{id}/", api_v2_chatbot.get_chatbot, methods=["GET"], tags=["v2"])  # type: ignore
app.add_api_route("/api/v2/chains/{id}/", api_v2_chatbot.delete_chatbot, methods=["DELETE"], tags=["v2"])  # type: ignore
app.add_api_route("/api/v2/chains/{id}/", api_v2_chatbot.update_chatbot, methods=["PATCH"], tags=["v2"])  # type: ignore
app.add_api_route("/api/v2/chains/{id}/", api_v2_chatbot.run_chain, methods=["POST"], tags=["v2"])  # type: ignore

# actions
app.add_api_route("/api/v2/fury/", api_v2_fury.list_actions, methods=["GET"], tags=["v2"])  # type: ignore
app.add_api_route("/api/v2/fury/", api_v2_fury.create_action, methods=["PUT"], tags=["v2"])  # type: ignore
app.add_api_route("/api/v2/fury/{id}/", api_v2_fury.get_action, methods=["GET"], tags=["v2"])  # type: ignore
app.add_api_route("/api/v2/fury/{id}/", api_v2_fury.delete_action, methods=["DELETE"], tags=["v2"])  # type: ignore
app.add_api_route("/api/v2/fury/{id}/", api_v2_fury.update_action, methods=["PATCH"], tags=["v2"])  # type: ignore
# app.add_api_route("/api/v2/fury/{id}/", fury.run_action, methods=["POST"], tags=["v2"])  # type: ignore

# prompts
app.add_api_route("/api/v2/prompts/", api_v2_prompts.list_prompts, methods=["GET"], tags=["v2"])  # type: ignore
app.add_api_route("/api/v2/prompts/{prompt_id}/", api_v2_prompts.get_prompt, methods=["GET"], tags=["v2"])  # type: ignore
app.add_api_route("/api/v2/prompts/{prompt_id}/", api_v2_prompts.delete_prompt, methods=["DELETE"], tags=["v2"])  # type: ignore


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
