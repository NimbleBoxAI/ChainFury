import fire, uvicorn
from typing import List


def main(
    host="0.0.0.0",
    port=8000,
    config_plugins: List[str] = [],
):
    assert type(config_plugins) == list, "config_plugins must be a list, try '[\"echo\"]'"
    import commons.config as c

    c.PluginsConfig.plugins_list = config_plugins

    from app import app

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    fire.Fire(main)
