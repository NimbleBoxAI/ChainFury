import fire, uvicorn
from typing import List
import importlib


def _main(
    host: str = "0.0.0.0",
    port: int = 8000,
    config_plugins: List[str] = [],
    pre: List[str] = [],
    post: List[str] = [],
):
    """
    Starts the server with the given configuration

    Args:
        host (str, optional): Host to run the server on. Defaults to "
        port (int, optional): Port to run the server on. Defaults to 8000.
        config_plugins (List[str], optional): List of plugins to load. Defaults to [].
        pre (List[str], optional): List of modules to load before the server is imported. Defaults to [].
        post (List[str], optional): List of modules to load after the server is imported. Defaults to [].

    Raises:
        AssertionError: If config_plugins is not a list
    """

    assert type(config_plugins) == list, "config_plugins must be a list, try '[\"echo\"]'"
    import chainfury_server.commons.config as c
    from chainfury_server.commons.utils import logger

    c.PluginsConfig.plugins_list = config_plugins
    port = int(port)

    for mod in pre:
        logger.info(f"Pre Loading {mod}")
        importlib.import_module(mod)

    from chainfury_server.app import app  # load the server here

    # for r in app.routes:
    #     if r.path == "/help":
    #         print(r)
    #         print(r.endpoint)
    #         print(r.endpoint())

    for mod in post:
        logger.info(f"Post Loading {mod}")
        _module = importlib.import_module(mod)
        # if hasattr(_module, "modify_app"):
        #     app = _module.modify_app(app)

    uvicorn.run(app, host=host, port=port)


def main():
    fire.Fire(_main)


if __name__ == "__main__":
    main()
