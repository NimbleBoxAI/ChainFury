# Copyright © 2023- Frello Technology Private Limited

import os
import re
import json
import time
import time
import random
import string
import logging
from uuid import uuid4
from urllib.parse import quote
from datetime import datetime, timezone
from typing import Any, Dict, List, Union, Tuple, Optional

from concurrent.futures import ThreadPoolExecutor, as_completed, Future


class CFEnv:
    """
    Single namespace for all environment variables.

    * CF_FOLDER: database connection string
    * CF_BLOB_STORAGE: blob storage folder on local machine
    * CF_BLOB_ENGINE: blob storage engine, can be one of `no`, `local` (default) or `s3`
    * CF_BLOB_BUCKET: blob storage bucket name (only used for `s3` engine)
    * CF_BLOB_PREFIX: blob storage prefix (only used for `s3` engine)
    * CF_BLOB_AWS_CLOUD_FRONT: blob storage cloud front url, if not provided defaults to primary S3 URL (only used for `s3` engine)
    * CF_URL: the URL of the chainfury server
    * CF_TOKEN: the token to use to authenticate with the chainfury server
    """

    CF_LOG_LEVEL = lambda: os.getenv("CF_LOG_LEVEL", "info")
    CF_FOLDER = lambda: os.path.expanduser(os.getenv("CF_FOLDER", "~/cf"))
    CF_BLOB_STORAGE = lambda: os.path.join(CFEnv.CF_FOLDER(), "blob")
    CF_BLOB_ENGINE = lambda: os.getenv("CF_BLOB_ENGINE", "local")
    CF_BLOB_BUCKET = lambda: os.getenv("CF_BLOB_BUCKET", "")
    CF_BLOB_PREFIX = lambda: os.getenv("CF_BLOB_PREFIX", "")
    CF_BLOB_AWS_CLOUD_FRONT = lambda: os.getenv("CF_BLOB_AWS_CLOUD_FRONT", "")
    CF_URL = lambda: os.getenv("CF_URL", "")
    CF_TOKEN = lambda: os.getenv("CF_TOKEN", "")


def store_blob(key: str, value: bytes, engine: str = "", bucket: str = "") -> str:
    """A function that stores the information in a file. This can automatically route to different storage engines.

    Args:
        key (str): The key to store the file under
        value (bytes): The value to store
        engine (str, optional): The engine to use, either pass value or set `CF_BLOB_ENGINE` env var. Defaults to "".
        bucket (str, optional): The bucket to use, either pass value or set `CF_BLOB_BUCKET` env var. Defaults to "".

    Returns:
        str: The url of the stored file or filepath
    """

    engine = engine or CFEnv.CF_BLOB_ENGINE()

    if engine == "no":
        # useful for debugging issues
        res = ""
    elif engine == "local":
        # store all the files locally, good when self hosting for demo
        fp = os.path.join(CFEnv.CF_BLOB_STORAGE(), key)
        with open(fp, "wb") as f:
            f.write(value)
        res = fp
    elif engine == "s3":
        # a more production grade storage system
        import boto3

        s3 = boto3.client("s3")
        bucket_name = bucket or CFEnv.CF_BLOB_BUCKET()
        key = CFEnv.CF_BLOB_PREFIX() + key
        logger.info(f"Storing {key} in {bucket_name}")
        s3.put_object(Bucket=bucket_name, Key=key, Body=value)
        aws_cfurl = CFEnv.CF_BLOB_AWS_CLOUD_FRONT()
        if aws_cfurl:
            res = aws_cfurl + quote(key)
        else:
            res = f"https://{bucket_name}.s3.amazonaws.com/{key}"
    else:
        raise Exception(f"Unknown blob engine: {CFEnv.CF_BLOB_ENGINE()}")
    return res


def get_blob(key: str, engine: str = "", bucket: str = "") -> bytes:
    """A function that gets the information from a file. This can automatically route to different storage engines.

    Args:
        key (str): The key to read the blob
        engine (str, optional): The engine to use, either pass value or set `CF_BLOB_ENGINE` env var. Defaults to "".
        bucket (str, optional): The bucket to use, either pass value or set `CF_BLOB_BUCKET` env var. Defaults to "".

    Returns:
        bytes: The value stored in the blob
    """

    engine = engine or CFEnv.CF_BLOB_ENGINE()

    if engine == "no":
        res = b""
    elif engine == "local":
        fp = os.path.join(CFEnv.CF_BLOB_STORAGE(), key)
        with open(fp, "rb") as f:
            res = f.read()
    elif engine == "s3":
        import boto3

        s3 = boto3.client("s3")
        bucket_name = bucket or CFEnv.CF_BLOB_BUCKET()
        key = CFEnv.CF_BLOB_PREFIX() + key
        logger.info(f"Getting {key} from {bucket_name}")
        res = s3.get_object(Bucket=bucket_name, Key=key)["Body"].read()
    else:
        raise Exception(f"Unknown blob engine: {CFEnv.CF_BLOB_ENGINE()}")
    return res


os.makedirs(CFEnv.CF_FOLDER(), exist_ok=True)
if CFEnv.CF_BLOB_ENGINE() == "local":
    os.makedirs(CFEnv.CF_BLOB_STORAGE(), exist_ok=True)


def terminal_top_with_text(msg: str = "") -> str:
    """Prints full wodth text message on the terminal

    Args:
        msg (str, optional): The message to print. Defaults to "".

    Returns:
        str: The message to print
    """
    width = os.get_terminal_size().columns
    if len(msg) > width - 5:
        x = "=" * width
        x += "\n" + msg
        x += "\n" + "=" * width // 2  # type: ignore
    else:
        x = "=" * (width - len(msg) - 1) + " " + msg
    return x


def get_logger() -> logging.Logger:
    """Returns a logger object"""
    logger = logging.getLogger("fury")
    lvl = CFEnv.CF_LOG_LEVEL().upper()
    logger.setLevel(getattr(logging, lvl))
    log_handler = logging.StreamHandler()
    log_handler.setFormatter(
        logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )
    )
    logger.addHandler(log_handler)
    return logger


logger = get_logger()
"""
This is the logger object that should be used across the entire package as well as by the user what wants to leverage
existing logging infrastructure.
"""


class UnAuthException(Exception):
    """Raised when the API returns a 401"""


class DoNotRetryException(Exception):
    """Raised when code tells not to retry"""


def exponential_backoff(
    foo, *args, max_retries=2, retry_delay=1, **kwargs
) -> Dict[str, Any]:
    """Exponential backoff function

    Args:
        foo (function): The function to call
        max_retries (int, optional): maximum number of retries. Defaults to 2.
        retry_delay (int, optional): Initial delay in seconds. Defaults to 1.

    Raises:
        e: Max retries reached. Exiting...
        Exception: This should never happen

    Returns:
        Dict[str, Any]: The completion(s) generated by the API.
    """

    if not max_retries:
        try:
            out = foo(*args, **kwargs)  # Call the function that may crash
            return out  # If successful, break out of the loop and return
        except DoNotRetryException as e:
            raise e
        except UnAuthException as e:
            raise e
        except Exception as e:
            logger.warning(f"Function crashed: {e}")
            raise e

    for attempt in range(max_retries):
        try:
            out = foo(*args, **kwargs)  # Call the function that may crash
            return out  # If successful, break out of the loop and return
        except DoNotRetryException as e:
            raise e
        except UnAuthException as e:
            raise e
        except Exception as e:
            logger.warning(f"Function crashed: {e}")
            if attempt == max_retries - 1:
                logger.error("Max retries reached. Exiting...")
                raise e
            else:
                delay = retry_delay * (2**attempt)  # Calculate the backoff delay
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)  # Wait for the calculated delay

    raise Exception("This should never happen")


"""
File System
"""


def get_files_in_folder(
    folder,
    ext="*",
    ig_pat: str = "",
    abs_path: bool = True,
    followlinks: bool = False,
) -> List[str]:
    """Get files with `ext` in `folder`"""
    # this method is faster than glob
    all_paths = []
    ext = [ext] if isinstance(ext, str) else ext
    _all = "*" in ext  # wildcard means everything so speed up
    ignore_pat = re.compile(ig_pat)

    folder_abs = os.path.abspath(folder) if abs_path else folder
    for root, _, files in os.walk(folder_abs, followlinks=followlinks):
        if _all:
            for f in files:
                _fp = joinp(root, f)
                if not ignore_pat.search(_fp):
                    all_paths.append(_fp)
            continue

        for f in files:
            for e in ext:
                if f.endswith(e):
                    _fp = joinp(root, f)
                    if not ignore_pat.search(_fp):
                        all_paths.append(_fp)
    return all_paths


def folder(x: str) -> str:
    """get the folder of this file path"""
    return os.path.split(os.path.abspath(x))[0]


def joinp(x: str, *args) -> str:
    """convienience function for os.path.join"""
    return os.path.join(x, *args)


"""
Parallel processing
"""


def threaded_map(
    fn,
    inputs: List[Tuple],
    wait: bool = True,
    max_threads=20,
    post_fn=None,
    _name: str = "",
    safe: bool = False,
) -> Union[Dict[Future, int], List[Any]]:
    """
    inputs is a list of tuples, each tuple is the input for single invocation of fn. order is preserved.

    Args:
        fn (function): The function to call
        inputs (List[Tuple[Any]]): All the inputs to the function, can be a generator
        wait (bool, optional): If true, wait for all the threads to finish, otherwise return a dict of futures. Defaults to True.
        max_threads (int, optional): The maximum number of threads to use. Defaults to 20.
        post_fn (function, optional): A function to call with the result. Defaults to None.
        _name (str, optional): The name of the thread pool. Defaults to "".
        safe (bool, optional): If true, all caughts exceptions are in the results. Defaults to False.
    """
    _name = _name or str(uuid4())
    results = [None for _ in range(len(inputs))]
    with ThreadPoolExecutor(max_workers=max_threads, thread_name_prefix=_name) as exe:
        _fn = lambda i, x: [i, fn(*x)]
        futures = {exe.submit(_fn, i, x): i for i, x in enumerate(inputs)}
        if not wait:
            return futures
        for future in as_completed(futures):
            try:
                i, res = future.result()
                if post_fn:
                    res = post_fn(res)
                results[i] = res
            except Exception as e:
                if safe:
                    results[i] = e  # type: ignore
                else:
                    raise e
    return results


def batched(iterable, n):
    """Convert any ``iterable`` to a generator of batches of size ``n``, last one may be smaller.
    Python 3.12 has ``itertools.batched`` which does the same thing.

    Example:
        >>> for x in batched(range(10), 3):
        ...    print(x)
        [0, 1, 2]
        [3, 4, 5]
        [6, 7, 8]
        [9]

    Args:
        iterable (Iterable): The iterable to convert to batches
        n (int): The batch size

    Yields:
        Iterator: The batched iterator
    """
    done = False
    buffer = []
    _iter = iter(iterable)
    while not done:
        try:
            buffer.append(next(_iter))
            if len(buffer) == n:
                yield buffer
                buffer = []
        except StopIteration:
            done = True
    if buffer:
        yield buffer


"""
Ser/Deser
"""


def to_json(x: dict, fp: str = "", indent=2, tight: bool = False) -> Optional[str]:
    """
    Convert a dict to json string and write to file if ``fp`` is provided.

    Args:
        x (dict): The dict to convert
        fp (str, optional): The file path to write to. Defaults to "".
        indent (int, optional): The indentation level. Defaults to 2.
        tight (bool, optional): If true, remove all the whitespaces, ignores ``indent``. Defaults to False.

    Returns:
        Optional[str]: The json string if ``fp`` is not provided
    """
    kwargs: Dict[str, Any] = {}
    if tight:
        kwargs["separators"] = (",", ":")  # type: ignore
    else:
        kwargs["indent"] = indent
    if fp:
        with open(fp, "w") as f:
            f.write(json.dumps(x, **kwargs))
    else:
        return json.dumps(x, **kwargs)


def from_json(fp: str = "") -> Dict[str, Any]:
    """
    Load a JSON string or filepath and return a dictionary.

    Args:
        fp (str): The filepath or JSON-ified string

    Returns:

    """
    if os.path.exists(fp):
        with open(fp, "r") as f:
            return json.load(f)
    else:
        return json.loads(fp)


"""
Time management should be dead easy.
"""


class SimplerTimes:
    """
    A class that provides a simpler interface to datetime and time modules.
    """

    tz = timezone.utc

    def get_now_datetime() -> datetime:  # type: ignore
        """Get the current datetime in UTC timezone"""
        return datetime.now(SimplerTimes.tz)

    def get_now_float() -> float:  # type: ignore
        """Get the current datetime in UTC timezone as a float"""
        return SimplerTimes.get_now_datetime().timestamp()

    def get_now_i64() -> int:  # type: ignore
        """Get the current datetime in UTC timezone as a int"""
        return int(SimplerTimes.get_now_datetime().timestamp())

    def get_now_str() -> str:  # type: ignore
        """Get the current datetime in UTC timezone as a string"""
        return SimplerTimes.get_now_datetime().strftime("%Y-%m-%d %H:%M:%S.%f")

    def i64_to_datetime(i64: int) -> datetime:  # type: ignore
        """Convert an int to datetime in UTC timezone"""
        return datetime.fromtimestamp(i64, SimplerTimes.tz)

    def get_now_human() -> str:  # type: ignore
        """Get the current datetime in UTC timezone as a human readable string"""
        return SimplerTimes.get_now_datetime().strftime("%A %d %B, %Y at %I:%M %p")


def get_random_string(length: int) -> str:
    return "".join(
        (random.choice(string.ascii_letters + string.digits) for _ in range(length))
    )
