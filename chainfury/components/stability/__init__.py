from typing import List, Dict, Union, Tuple, Optional

from chainfury import Secret, model_registry, exponential_backoff, Model


def stability_text_to_image(
    stability_api_key: Secret,
    text_prompts: List[Dict[str, Union[str, float]]],
    height: int = 512,
    width: int = 512,
    cfg_scale: float = 7,
    clip_guidance_preset: str = "NONE",
    sampler: str = None,  # type: ignore # see components README.md
    samples: int = 1,
    seed: int = 0,
    steps: int = 50,
    style_preset: str = None,  # type: ignore # see components README.md
    extras: Dict[str, Union[str, int, float]] = None,  # type: ignore # see components README.md
) -> List[str]:
    """
    Generate an image from text prompts using the Stability API.

    Args:
        text_prompts (List[Dict[str, Union[str, float]]]): An array of text prompts to use for generation. Given a text prompt with the text "A lighthouse on a cliff" and a weight of 0.5, it would be represented as:
            [{"text": "A lighthouse on a cliff", "weight": 0.5}]
        height (int): Height of the image in pixels. Must be in increments of 64 and pass the following validation:
            For 768 engines: 589,824 ≤ height * width ≤ 1,048,576
            All other engines: 262,144 ≤ height * width ≤ 1,048,576
        width (int): Width of the image in pixels. Must be in increments of 64 and pass the following validation:
            For 768 engines: 589,824 ≤ height * width ≤ 1,048,576
            All other engines: 262,144 ≤ height * width ≤ 1,048,576
        cfg_scale (float): How strictly the diffusion process adheres to the prompt text (higher values keep your image closer to your prompt). Default: 7.
        clip_guidance_preset (str): Which CLIP guidance preset to use for the diffusion process. Default: "NONE".
        sampler (str): Which sampler to use for the diffusion process. If this value is omitted we'll automatically select an appropriate sampler for you.
        samples (int): Number of images to generate. Default: 1.
        seed (int): Random noise seed (omit this option or use 0 for a random seed). Default: 0.
        steps (int): Number of diffusion steps to run. Default: 50.
        style_preset (str): Pass in a style preset to guide the image model towards a particular style. This list of style presets is subject to change.
        extras (Dict[str, Union[str, int, float]]): Extra parameters passed to the engine. These parameters are used for in-development or experimental features and may change without warning, so please use with caution.

    Returns:
        List[str]: A list of base64-encoded PNG images.
    """
    pass


model_registry.register(
    model=Model(
        collection_name="stabilityai",
        id="stability-text-to-image",
        fn=stability_text_to_image,
        description="Generate a new image from a text prompt",
    )
)


def stability_image_to_image(
    stability_api_key: Secret,
    text_prompts: List[Tuple[str, float]],
    init_image: bytes,
    init_image_mode: str = "IMAGE_STRENGTH",
    image_strength: float = 0.35,
    cfg_scale: int = 7,
    clip_guidance_preset: str = "NONE",
    sampler: str = "",
    samples: int = 1,
    seed: int = 0,
    steps: int = 50,
    style_preset: str = "",
    extras: dict = {},
) -> List[bytes]:
    """
    Generate an image using the Stability AI API.

    Args:
        text_prompts (List[Tuple[str, float]]): A list of tuples, each containing a text prompt and a weight. The text prompts will be used for generation.
        init_image (bytes): An image used to initialize the diffusion process, in lieu of random noise.
        init_image_mode (str): Whether to use image_strength or step_schedule_* to control how much influence the init_image has on the result. Default is "IMAGE_STRENGTH".
        image_strength (float): How much influence the init_image has on the diffusion process. Values close to 1 will yield images very similar to the init_image while values close to 0 will yield images wildly different than the init_image. Default is 0.35.
        cfg_scale (int): How strictly the diffusion process adheres to the prompt text (higher values keep your image closer to your prompt). Default is 7.
        clip_guidance_preset (str): A preset to guide the diffusion process towards a particular style. Default is "NONE".
        sampler (str): Which sampler to use for the diffusion process. If this value is omitted, an appropriate sampler will be selected automatically.
        samples (int): Number of images to generate. Default is 1.
        seed (int): Random noise seed (omit this option or use 0 for a random seed). Default is 0.
        steps (int): Number of diffusion steps to run. Default is 50.
        style_preset (str): Pass in a style preset to guide the diffusion process towards a particular style. Default is "".
        extras (dict): Extra parameters passed to the engine. These parameters are used for in-development or experimental features and may change without warning, so please use with caution. Default is an empty dictionary.

    Returns:
        List[bytes]: A list of base64-encoded PNG images.
    """
    pass


model_registry.register(
    model=Model(
        collection_name="stabilityai",
        id="stability-image-to-image",
        fn=stability_image_to_image,
        description="Modify an image based on a text prompt",
    )
)


def stability_image_to_image_upscale(
    stability_api_key: Secret,
    image: bytes,
    width: int = None,  # type: ignore # see components README.md
    height: int = None,  # type: ignore # see components README.md
) -> bytes:
    """
    Upscales an image to a specified width or height.

    Args:
        image (bytes): The image to upscale.
        width (int, optional): Desired width of the output image. Only one of width or height may be specified.
        height (int, optional): Desired height of the output image. Only one of width or height may be specified.

    Returns:
        bytes: The upscaled image.
    """
    pass


model_registry.register(
    model=Model(
        collection_name="stabilityai",
        id="stability-image-to-image-upscale",
        fn=stability_image_to_image,
        description="Create a higher resolution version of an input image. This operation outputs an image with a maximum pixel "
        "count of 4,194,304. This is equivalent to dimensions such as 2048x2048 and 4096x1024. By default, the input "
        "image will be upscaled by a factor of 2. For additional control over the output dimensions, a width or height "
        "parameter may be specified.",
    )
)


def stability_image_to_image_masking(
    stability_api_key: Secret,
    text_prompts: List[Dict[str, float]],
    init_image: bytes,
    mask_source: str,
    mask_image: bytes,
    cfg_scale: float = 7,
    clip_guidance_preset: str = "NONE",
    sampler: str = None,  # type: ignore # see components README.md
    samples: int = 1,
    seed: int = 0,
    steps: int = 50,
    style_preset: str = None,  # type: ignore # see components README.md
    extras: dict = None,  # type: ignore # see components README.md
) -> bytes:
    """
    Generates an image based on text prompts and an initial image. Returns the generated image as bytes.

    Args:
        text_prompts (List[Dict[str, Union[str, float]]]): An array of text prompts to use for generation. Each prompt is a dictionary with the following keys:
            'text': str -- The prompt text to use.
            'weight': float -- The weight to assign to the prompt. (Default 1.0)
        init_image (PIL.Image.Image): Image used to initialize the diffusion process, in lieu of random noise.
        mask_source (str): Determines where to source the mask from. Should be one of 'MASK_IMAGE_WHITE', 'MASK_IMAGE_BLACK', or 'INIT_IMAGE_ALPHA'.
        mask_image (PIL.Image.Image): Grayscale mask that allows for influence over which pixels are eligible for diffusion and at what strength. Must be the same dimensions as the init_image.
        cfg_scale (float, optional): How strictly the diffusion process adheres to the prompt text. Higher values keep the image closer to the prompt. (Default 7)
        clip_guidance_preset (str, optional): Pass in a clip guidance preset to guide the image model towards a particular style. Should be one of 'FAST_BLUE', 'FAST_GREEN', 'NONE', 'SIMPLE', 'SLOW', 'SLOWER', 'SLOWEST'. (Default 'NONE')
        sampler (str, optional): Which sampler to use for the diffusion process. Should be one of 'DDIM', 'DDPM', 'K_DPMPP_2M', 'K_DPMPP_2S_ANCESTRAL', 'K_DPM_2', 'K_DPM_2_ANCESTRAL', 'K_EULER', 'K_EULER_ANCESTRAL', 'K_HEUN', 'K_LMS'. If not provided, an appropriate sampler will be selected automatically.
        samples (int, optional): Number of images to generate. (Default 1)
        seed (int, optional): Random noise seed. Use 0 for a random seed. (Default 0)
        steps (int, optional): Number of diffusion steps to run. (Default 50)
        style_preset (str, optional): Pass in a style preset to guide the image model towards a particular style. Should be one of 'enhance', 'anime', 'photographic', 'digital-art', 'comic-book', 'fantasy-art', 'line-art', 'analog-film', 'neon-punk', 'isometric', 'low-poly', 'origami', 'modeling-compound', 'cinematic', '3d-model', 'pixel-art', or 'tile-texture'. (Default None)
        extras (Any, optional): Extra parameters passed to the engine. These parameters are used for in-development or experimental features and may change without warning, so please use with caution. (Default None)

    Returns:
        bytes: The generated image.
    """
    pass


model_registry.register(
    model=Model(
        collection_name="stabilityai",
        id="stability-image-to-image-masking",
        fn=stability_image_to_image,
        description="Selectively modify portions of an image using a mask",
    )
)
