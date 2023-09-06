Privately Storing Data
======================

During running ChainFury (self-hosted), there are times when you want the data that is generated to be stored privately
off the server pod running it. For example when we call the :py:mod:`chainfury.components.stability` APIs the images
generated are not stored in the database but rather as blobs.

These blobs are stored at different places based on the :py:mod:`chainfury.utils.CFEnv` configs. Here's a list of them
and how to access them. All of it works using the :py:mod:`chainfury.utils.store_blob` function.

Not storage "no"
----------------

In this case no data is stored and empty types are returned

Local Storage "local"
---------------------

This is the default case where a folder is created at ``~/cf`` and blobs are stored at ``~/cf/blob``.

AWS S3 "s3"
-----------

This is a power mode that you want to be using if you are looking at productionizing ChainFury internally. In this case
all the blobs are stored in an S3 bucket. Here's all the environment configs that you need to set.

.. code-block:: bash

    # install the boto3 client for python
    pip install boto3

    # variables for storing blobs in AWS S3
    export CF_BLOB_ENGINE='s3'
    export AWS_ACCESS_KEY_ID='AKIAVNKAPLFKAPFIUKKCF74SF'
    export AWS_SECRET_ACCESS_KEY='daBREq2h8aP9uATFj+DJJFkkasdok3/a9Nc9qSnq1s'
    export CF_BLOB_PREFIX='chainfury/prod/'
    export CF_BLOB_BUCKET='nbx-public-assets'

    # optionally set this if you want to store AWS cloudfront URLs in the DB
    export CF_BLOB_AWS_CLOUD_FRONT='https://asdjodjasdm9.cloudfront.net/'

    # start the server
    python3 -m chainfury_server

In this case a function call like this will return the cloud front URL of the blob.

.. code-block:: python

    >>> key = store_blob(
    ...  'nbx-cf-component-stability-text-to-image-jjs9dk_1690977245_0.png',
    ...  bytes('hello world', 'utf-8'),
    ... )
    >>> key
    https://asdjodjasdm9.cloudfront.net/chainfury/prod/nbx-cf-component-stability-text-to-image-jjs9dk_1690977245_0.png

    >>> # in case CF_BLOB_AWS_CLOUD_FRONT is not set
    >>> key
    https://nbx-public-assets.s3.amazonaws.com/chainfury/prod/nbx-cf-component-stability-text-to-image-jjs9dk_1690977245_0.png

Need Help?
----------

Please raise an issue on `ChainFury Repo <https://github.com/NimbleBoxAI/ChainFury>`_
