# Copyright © 2023- Frello Technology Private Limited

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from chainfury_server.utils import Env
from chainfury_server.database import add_default_user

# API function imports
import chainfury_server.api.user as api_user
import chainfury_server.api.chains as api_chains
import chainfury_server.api.prompts as api_prompts
from chainfury_server.ui import landing_page, serve_ui, static_fp
from chainfury_server.version import __version__

app = FastAPI(
    title="ChainFury",
    description="""
chainfury server is a way to deploy and run chainfury engine over APIs. `chainfury` is [Tune AI](tunehq.ai)'s FOSS project
released under [Apache-2 License](https://choosealicense.com/licenses/apache-2.0/) so you can use this for your commercial
projects. A version `chainfury` is used in production in [Tune.Chat](chat.tune.app) and serves thousands of users daily.
""".strip(),
    version=__version__,
    docs_url="" if Env.CFS_DISABLE_DOCS() else "/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=Env.CFS_ALLOW_CORS_ORIGINS(),
    allow_methods=Env.CFS_ALLOW_METHODS(),
    allow_headers=Env.CFS_ALLOW_HEADERS(),
)

add_default_user()

# v2 APIs (Koval)
# ---------------

# TODO: deprecate this
app.add_api_route("/api/v1/chatbot/{id}/prompt", api_chains.run_chain, methods=["POST"], tags=["deprecated"], response_model=None)  # type: ignore

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


# UI files
# --------
if not Env.CFS_DISABLE_UI():
    app.add_api_route("/", landing_page, methods=["GET"], tags=["deprecated"], response_class=HTMLResponse)  # type: ignore
    app.add_api_route("/ui/{rest_of_path:path}", serve_ui, methods=["GET"], tags=["ui"])  # type: ignore
    app.mount("/", StaticFiles(directory=static_fp), name="assets")
