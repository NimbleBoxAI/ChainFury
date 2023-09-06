Image Generation using Stability APIs
=====================================

Here's a quick example on how you can use image generation as a part of your chain. For this we are using Stability AI's
`DreamStudio <https://dreamstudio.ai/>`_ APIs.

The way this current codebase works is that we can pass in a text and get back the path of the image. The location of
the image storage can be improved by overriding the :py:mod:`chainfury.utils.store_blob` function with your callable.

Code
----

There will be no more breaking changes to this code. Only improvements such as higher abstraction layers will be added.


.. code-block:: python

  >>> # you can set the API key in the your env for convenience
  >>> import os
  >>> os.environ["STABILITY_KEY"] = "<API_KEY>"
  
  >>> # get the underlying API
  >>> from chainfury.components.stability import stability_text_to_image

  >>> # call the model
  >>> out = stability_text_to_image(
  ...     'a cat peacefully watching the sunset, with a serene expression on its face.", by syd mead, cold color palette, muted colors, detailed, 8k'
  ...     # stability_api_key = "<API_KEY>" # or pass the key here
  ... )
  >>> out = stability_text_to_image()
  >>> print(out)
  ['~/cf/blob/nbx-cf-..._1690784124_0.png']

  >>> # let's see the image
  >>> from PIL import Image
  >>> Image.open(out[0])

.. image:: https://d2e931syjhr5o9.cloudfront.net/chainfury/nbx-cf-component-stability-text-to-image%22a+cat+peacefully+watching+the+sunset%2C+with+a+serene+expression+on+its+face.%22%2C+by+syd+mead%2C+cold+color+palette%2C+muted+colors%2C+detailed%2C+8k_1690809210_0.png
  :alt: a cat peacefully watching the sunset, with a serene expression on its face.", by syd mead, cold color palette, muted colors, detailed, 8k
