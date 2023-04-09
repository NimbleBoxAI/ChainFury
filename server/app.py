import os
from typing import Dict, List
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from commons import config as c
from commons.utils import add_default_user

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


@app.get("/", response_class=RedirectResponse, status_code=302)
async def redirect_pydantic():
    return "/ui/login"


# add static files
app.mount("/", StaticFiles(directory="static"), name="assets")
