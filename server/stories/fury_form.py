from components.openai import openai_chat, openai_completion
from components.stability import (
    stability_image_to_image,
    stability_text_to_image,
    stability_image_to_image_masking,
    stability_image_to_image_upscale,
)

funcs = [
    openai_chat,
    openai_completion,
    stability_image_to_image,
    stability_text_to_image,
    stability_image_to_image_masking,
    stability_image_to_image_upscale,
]

from fury.base import func_to_template_fields

for f in funcs:
    print("=" * 30)
    print(f.__name__)
    try:
        out = func_to_template_fields(f)
    except Exception as e:
        print("failed:", e)
        continue
    for x in out:
        # print(x)
        print(x.to_dict())
