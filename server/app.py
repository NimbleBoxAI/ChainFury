import os
import requests
from typing import Dict, List
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from commons import config as c
from commons.utils import add_default_user, add_default_templates

# Routers
from api.auth import auth_router
from api.chatbot import chatbot_router
from api.feedback import feedback_router
from api.intermediate_steps import intermediate_steps_router
from api.langflow import router as langflow_router
from api.metrics import metrics_router
from api.prompts import router as prompts_router
from api.template import template_router
from api.user import user_router
from api.dashboard import dashboard_router
from api.components import components_router

from plugins import get_phandler


logger = c.get_logger(__name__)

app = FastAPI(
    title="ChainFury",
    description="Transform LLM development with LangChain DB - monitor I/O, evaluate models, and track performance with precision and efficiency using this open-source tool",
    version="0.0.1",
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
app.include_router(user_router, prefix=c.API_URL)
app.include_router(metrics_router, prefix=c.API_URL)
app.include_router(feedback_router, prefix=c.API_URL)
app.include_router(intermediate_steps_router, prefix=c.API_URL)
app.include_router(chatbot_router, prefix=c.API_URL)
app.include_router(auth_router, prefix=c.API_URL)
app.include_router(langflow_router, prefix=c.API_URL)
app.include_router(prompts_router, prefix=c.API_URL)
app.include_router(template_router, prefix=c.API_URL)
app.include_router(dashboard_router, prefix=c.API_URL)
app.include_router(components_router, prefix=c.API_URL)
####################################################
################ APIs ##############################
####################################################


templates = Jinja2Templates(directory="templates")


@app.get("/ui/{rest_of_path:path}")
async def serve_spa(request: Request, rest_of_path: str):
    return templates.TemplateResponse("index.html", {"request": request})


if "static" not in os.listdir("./"):
    # make static folder
    logger.info("Static folder not found. Creating one...")
    os.mkdir("static")


# get https://chainfury.framer.website/ and serve on /
@app.get("/")
async def serve_farmer():
    r = requests.get("https://chainfury.framer.website/")
    modified_text = ""
    if r.text:
        modified_text = r.text.replace("https://chainfury.nbox.ai/ui/dashboard", "/ui/dashboard")
    return HTMLResponse(content=modified_text, status_code=r.status_code)


# add static files
app.mount("/", StaticFiles(directory="static"), name="assets")

# warmup and initialize plugins
get_phandler()

# warmup and initialize components
import components
