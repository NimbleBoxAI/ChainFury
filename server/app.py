import database
from typing import Dict, List
from fastapi import FastAPI
from starlette.responses import Response
import requests
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

c.Base.metadata.create_all(bind=engine)

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
app.include_router(user_router)
app.include_router(metrics_router)
app.include_router(feedback_router)
app.include_router(intermediate_steps_router)
app.include_router(chatbot_router)
app.include_router(auth_router)
app.include_router(langflow_router)
app.include_router(prompts_router)
app.include_router(template_router)
####################################################
################ APIs ##############################
####################################################


# TO CHECK IF SERVER IS ON
@app.get("/test", status_code=200)
def test(response: Response):
    return {"msg": "success"}
