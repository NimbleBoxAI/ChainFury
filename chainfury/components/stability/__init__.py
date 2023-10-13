"""
Engineering Notes
-----------------

You need to have `stability_sdk` installed to use this component. You can install it with:

.. code-block:: bash
    
    pip install chainfury[stability]
    # or to install all the components, note this will keep on growing
    pip install chainfury[all]
"""
import os
from typing import List, Dict, Union, Tuple, Optional

from chainfury import Secret, model_registry, Model, exponential_backoff, DoNotRetryException
from chainfury.utils import CFEnv, store_blob
from chainfury.components.const import Env

try:
    from grpc import RpcError, StatusCode
    from stability_sdk.client import StabilityInference, process_artifacts_from_answers
    from stability_sdk.utils import sampler_from_string
    from stability_sdk.interfaces.gooseai.generation.generation_pb2 import Artifact
    from stability_sdk.interfaces.gooseai.generation.generation_pb2 import ARTIFACT_IMAGE

    STABILITY_SDK_INSTALLED = True
except:
    STABILITY_SDK_INSTALLED = False


def stability_text_to_image(
    text_prompts: Union[str, List[str], List[Dict[str, Union[str, float]]]],
    stability_api_key: Secret = Secret(""),
    stability_host: str = "grpc.stability.ai:443",
    height: int = 768,
    width: int = 768,
    cfg_scale: float = 7,
    engine: str = "stable-diffusion-768-v2-1",  # stable-diffusion-xl-1024-v0-9
    start_schedule: float = 1.0,
    end_schedule: float = 0.01,
    sampler: str = "",
    samples: int = 1,
    seed: int = 0,
    steps: int = 50,
    style_preset: str = "",
    *,
    prefix: str = "nbx-cf-component-stability-text-to-image",
    max_retries: int = 3,
    retry_delay: int = 1,
) -> List[str]:
    """
    Generate an image from text prompts using the Stability API.

    Args:
        text_prompts (List[Dict[str, Union[str, float]]]): An array of text prompts to use for generation. Given a text prompt with the text "A lighthouse on a cliff" and a weight of 0.5, it would be represented as:
            [{"text": "A lighthouse on a cliff", "weight": 0.5}]
        stability_api_key (Secret): Your Stability API key. If not provided, we'll try to use the STABILITY_KEY environment variable.
        stability_host (str): The Stability API host to use. Default: "grpc.stability.ai:443".
        height (int): Height of the image in pixels. Must be in increments of 64 and pass the following validation:
            For 768 engines: 589,824 ≤ height * width ≤ 1,048,576
            All other engines: 262,144 ≤ height * width ≤ 1,048,576
        width (int): Width of the image in pixels. Must be in increments of 64 and pass the following validation:
            For 768 engines: 589,824 ≤ height * width ≤ 1,048,576
            All other engines: 262,144 ≤ height * width ≤ 1,048,576
        cfg_scale (float): How strictly the diffusion process adheres to the prompt text (higher values keep your image closer to your prompt). Default: 7.
        sampler (str): Which sampler to use for the diffusion process. If this value is omitted we'll automatically select an appropriate sampler for you.
        samples (int): Number of images to generate. Default: 1.
        seed (int): Random noise seed (omit this option or use 0 for a random seed). Default: 0.
        steps (int): Number of diffusion steps to run. Default: 50.
        style_preset (str): Pass in a style preset to guide the image model towards a particular style. This list of style presets is subject to change.
        prefix (str): Prefix to use for the generated images. Default: "nbx-cf-component-stability-text-to-image/".

    Returns:
        List[str]: A list of base64-encoded PNG images.
    """
    # perform checks
    if not STABILITY_SDK_INSTALLED:
        raise Exception(
            "stability_sdk is not installed, cannot use with chainfury. Please install it with `pip install chainfury[stability]`"
        )
    if not stability_api_key:
        stability_api_key = Secret(Env.STABILITY_KEY("")).value
    if not stability_api_key:
        raise Exception("Stability API key not found. Please set STABILITY_KEY environment variable or pass through function")
    if isinstance(text_prompts, (list, tuple)):
        if len(text_prompts) != 1:
            raise Exception("Only one text prompt is supported at this time")
        prompt = text_prompts[0]
        if isinstance(prompt, dict):
            prompt = prompt["text"]
    else:
        if not isinstance(text_prompts, str):
            raise Exception("text_prompts must be a string or a list of strings")
        prompt = text_prompts

    # make request
    request = {}
    if sampler:
        request["sampler"] = sampler_from_string(sampler)
    if steps:
        request["steps"] = steps
    stability_api = StabilityInference(
        host=stability_host,
        key=stability_api_key,
        engine=engine,
        verbose=True,
    )

    def _fn():
        try:
            answers = stability_api.generate(
                prompt=prompt,  # type: ignore
                height=height,
                width=width,
                start_schedule=start_schedule,
                end_schedule=end_schedule,
                cfg_scale=cfg_scale,
                seed=seed,
                samples=samples,
                style_preset=style_preset,
                **request,
            )
        except RpcError as e:
            if e.code() in [  # type: ignore
                StatusCode.INVALID_ARGUMENT,
                StatusCode.UNAUTHENTICATED,
                StatusCode.UNIMPLEMENTED,
                StatusCode.PERMISSION_DENIED,
            ]:
                raise DoNotRetryException(f"Code: {e.code()} | {e.details()}")  # type: ignore
            else:
                raise e
        artifacts = process_artifacts_from_answers(
            prefix=prefix,
            prompt=prompt,  # type: ignore
            answers=answers,
            write=False,
            verbose=False,
        )
        out = []

        # store images
        for out_p, artifact in artifacts:
            if artifact.type == ARTIFACT_IMAGE:  # type: ignore
                data_bin = bytes(artifact.binary)  # type: ignore
                out_p = out_p.replace("/", "--")
                fp = store_blob(out_p, data_bin)
                out.append(fp)
        return out

    return exponential_backoff(_fn, max_retries=max_retries, retry_delay=retry_delay)  # type: ignore


model_registry.register(
    model=Model(
        collection_name="stabilityai",
        id="stability-text-to-image",
        fn=stability_text_to_image,
        description="Generate a new image from a text prompt",
    )
)
