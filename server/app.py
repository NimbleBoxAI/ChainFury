import os
from typing import Dict, List
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.responses import Response
from commons import config as c
from commons.config import engine
from commons.utils import add_default_user
from api.chatbot import chatbot_router
from api.auth import auth_router
from fastapi.middleware.cors import CORSMiddleware

# Routers
from api.user import user_router
from api.metrics import metrics_router
from api.feedback import feedback_router
from api.intermediate_steps import intermediate_steps_router
from api.template import template_router
from api.langflow import router as langflow_router
from api.prompts import router as prompts_router

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
API_URL = "/api/v1"
# Registering apis.
app.include_router(user_router, prefix=API_URL)
app.include_router(metrics_router, prefix=API_URL)
app.include_router(feedback_router, prefix=API_URL)
app.include_router(intermediate_steps_router, prefix=API_URL)
app.include_router(chatbot_router, prefix=API_URL)
app.include_router(auth_router, prefix=API_URL)
app.include_router(langflow_router, prefix=API_URL)
app.include_router(prompts_router, prefix=API_URL)
app.include_router(template_router, prefix=API_URL)
####################################################
################ APIs ##############################
####################################################


@app.get("/ui/{rest_of_path:path}")
async def serve_spa(request: Request, rest_of_path: str):
    return templates.TemplateResponse("index.html", {"request": request})


if "static" not in os.listdir("./"):
    # make static folder
    logger.info("Static folder not found. Creating one...")
    os.mkdir("static")

# add static files
app.mount("/", StaticFiles(directory="static"), name="assets")
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")


# TO CHECK IF SERVER IS ON
@app.get("/test", status_code=200)
def test(response: Response):
    return {"msg": "success"}
