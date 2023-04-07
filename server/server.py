from typing import Dict, List
from fastapi import FastAPI
from starlette.responses import Response
import requests

import commons.config as c

# Routers
# from api.initialize import X
# from api.environment import Environment
# from api.monitoring import Monitoring
# from commons import google_drive
# from api.initialize import run_servers
# from commons import unix_system as system

app = FastAPI(
    title="ChainFury",
    description="Transform LLM development with LangChain DB - monitor I/O, evaluate models, and track performance with precision and efficiency using this open-source tool",
    version="0.0.1",
)


####################################################
################ INITIALIZE ########################
####################################################
# Registering apis.
# app.include_router(initialize_router)

####################################################
################ APIs ##############################
####################################################

# TO CHECK IF SERVER IS ON
@app.get("/test", status_code=200)
def test(response: Response):
    return {"msg": "success"}
