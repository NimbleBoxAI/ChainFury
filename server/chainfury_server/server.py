import fire, uvicorn
from typing import List


def _main(
    host: str = "0.0.0.0",
    port: int = 8000,
    config_plugins: List[str] = [],
):
    """
    Starts the server with the given configuration

    Args:
        host (str, optional): Host to run the server on. Defaults to "
        port (int, optional): Port to run the server on. Defaults to 8000.
        config_plugins (List[str], optional): List of plugins to load. Defaults to [].

    Raises:
        AssertionError: If config_plugins is not a list
    """

    assert type(config_plugins) == list, "config_plugins must be a list, try '[\"echo\"]'"
    import chainfury_server.commons.config as c

    c.PluginsConfig.plugins_list = config_plugins
    port = int(port)

    from chainfury_server.app import app

    uvicorn.run(app, host=host, port=port)


def main():
    fire.Fire(_main)


if __name__ == "__main__":
    main()
