import os

os.environ["CF_NO_LOAD_CLIENT"] = "1"

import requests
from typing import Dict, List
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware


from chainfury_server.commons import config as c
from chainfury_server.commons.utils import add_default_user, add_default_templates, folder, joinp

# Routers
from chainfury_server.api.auth import auth_router
from chainfury_server.api.chatbot import chatbot_router
from chainfury_server.api.feedback import feedback_router
from chainfury_server.api.intermediate_steps import intermediate_steps_router
from chainfury_server.api.langflow import router as langflow_router
from chainfury_server.api.metrics import metrics_router
from chainfury_server.api.prompts import router as prompts_router
from chainfury_server.api.template import template_router
from chainfury_server.api.user import user_router
from chainfury_server.api.dashboard import dashboard_router
from chainfury_server.api.fury import fury_router

from chainfury_server.plugins import get_phandler


logger = c.get_logger(__name__)

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
app.include_router(auth_router, prefix=c.API_URL)
app.include_router(user_router, prefix=c.API_URL)
app.include_router(feedback_router, prefix=c.API_URL)
app.include_router(metrics_router, prefix=c.API_URL + "/chatbot")
app.include_router(intermediate_steps_router, prefix=c.API_URL + "/chatbot")
app.include_router(chatbot_router, prefix=c.API_URL + "/chatbot")
app.include_router(prompts_router, prefix=c.API_URL + "/chatbot")
app.include_router(template_router, prefix=c.API_URL + "/template")
app.include_router(fury_router, prefix=c.API_URL + "/fury")
app.include_router(langflow_router, prefix=c.API_URL + "/flow")
# app.include_router(dashboard_router, prefix=c.API_URL)


####################################################
################ APIs ##############################
####################################################


# get https://chainfury.framer.website/ and serve on /
@app.get("/")
async def serve_farmer():
    r = requests.get("https://chainfury.framer.website/")
    modified_text = ""
    if r.text:
        modified_text = r.text.replace("https://chainfury.nbox.ai/ui/dashboard", "/ui/dashboard")
    return HTMLResponse(content=modified_text, status_code=r.status_code)


# add static files
_static_fp = joinp(folder(__file__), "static")
static = Jinja2Templates(directory=_static_fp)


@app.get("/ui/{rest_of_path:path}")
async def serve_spa(request: Request, rest_of_path: str):
    return static.TemplateResponse("index.html", {"request": request})


app.mount("/", StaticFiles(directory=_static_fp), name="assets")

# warmup and initialize plugins
get_phandler()
