Image Generation using Stability APIs (coming in W1 August 2023)
================================================================

This will show how to use the stability APIs to generate images. A more refined version of this will be available in W1 August 2023.

.. note::

    The underlying APIs are finalised, working on creating the abstraction layer.

Demo Working Code
-----------------


.. code-block:: python

  >>> # you can set the API key in the your env for convenience
  >>> import os
  >>> os.environ["STABILITY_KEY"] = "<API_KEY>"
  
  >>> # get the underlying API
  >>> from chainfury.components.stability import stability_text_to_image

  >>> # call the model
  >>> out = stability_text_to_image(
  ...     "a cat on the moon eating pizza, style of syd mead"
  ...     # stability_api_key = "<API_KEY>" # or pass the key here
  ... )
  >>> out = stability_text_to_image()
  >>> print(out)
  ['~/cf/blob/nbx-cf-component-stability-text-to-imagea cat on the moon eating pizza, style of syd mead_1690784124_0.png']

  >>> # let's see the image
  >>> from PIL import Image
  >>> Image.open(out[0])
