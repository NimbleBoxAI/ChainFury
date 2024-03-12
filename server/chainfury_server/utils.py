# Copyright © 2023- Frello Technology Private Limited

import os
from Cryptodome.Cipher import AES
from base64 import b64decode, b64encode

# WARNING: do not import anything from anywhere here, this is the place where chainfury_server starts.
#          importing anything can cause the --pre and --post flags to fail when starting server.

from chainfury.utils import (
    logger,
)  # keep this here, rest of package imports from this file


class Env:
    """
    Single namespace for all environment variables.
    """

    # once a lifetime secret
    JWT_SECRET = lambda: os.getenv("JWT_SECRET", "hajime-shimamoto")
    CFS_SECRETS_PASSWORD = lambda: os.getenv("CFS_SECRETS_PASSWORDs")

    # when you want to use chainfury as a client you need to set the following vars
    CFS_DATABASE = lambda: os.getenv("CFS_DATABASE", None)
    CFS_MAXLEN_CF_NDOE = lambda: int(os.getenv("CFS_MAXLEN_CF_NDOE", 80))
    CFS_MAXLEN_WORKER = lambda: int(os.getenv("CFS_MAXLEN_WORKER", 16))
    CFS_ALLOW_CORS_ORIGINS = lambda: [
        x.strip() for x in os.getenv("CFS_ALLOW_CORS_ORIGINS", "*").split(",")
    ]
    CFS_ALLOW_METHODS = lambda: [
        x.strip() for x in os.getenv("CFS_ALLOW_METHODS", "*").split(",")
    ]
    CFS_ALLOW_HEADERS = lambda: [
        x.strip() for x in os.getenv("CFS_ALLOW_HEADERS", "*").split(",")
    ]
    CFS_DISABLE_UI = lambda: os.getenv("CFS_DISABLE_UI", "0") == "1"
    CFS_DISABLE_DOCS = lambda: os.getenv("CFS_DISABLE_DOCS", "0") == "1"


def folder(x: str) -> str:
    """get the folder of this file path"""
    return os.path.split(os.path.abspath(x))[0]


def joinp(x: str, *args) -> str:
    """convienience function for os.path.join"""
    return os.path.join(x, *args)


class Crypt:

    def __init__(self, salt="SlTKeYOpHygTYkP3"):
        self.salt = salt.encode("utf8")
        self.enc_dec_method = "utf-8"

    def encrypt(self, str_to_enc, str_key):
        try:
            aes_obj = AES.new(str_key.encode("utf-8"), AES.MODE_CFB, self.salt)
            hx_enc = aes_obj.encrypt(str_to_enc.encode("utf8"))
            mret = b64encode(hx_enc).decode(self.enc_dec_method)
            return mret
        except ValueError as value_error:
            if value_error.args[0] == "IV must be 16 bytes long":
                raise ValueError("Encryption Error: SALT must be 16 characters long")
            elif (
                value_error.args[0] == "AES key must be either 16, 24, or 32 bytes long"
            ):
                raise ValueError(
                    "Encryption Error: Encryption key must be either 16, 24, or 32 characters long"
                )
            else:
                raise ValueError(value_error)

    def decrypt(self, enc_str, str_key):
        try:
            aes_obj = AES.new(str_key.encode("utf8"), AES.MODE_CFB, self.salt)
            str_tmp = b64decode(enc_str.encode(self.enc_dec_method))
            str_dec = aes_obj.decrypt(str_tmp)
            mret = str_dec.decode(self.enc_dec_method)
            return mret
        except ValueError as value_error:
            if value_error.args[0] == "IV must be 16 bytes long":
                raise ValueError("Decryption Error: SALT must be 16 characters long")
            elif (
                value_error.args[0] == "AES key must be either 16, 24, or 32 bytes long"
            ):
                raise ValueError(
                    "Decryption Error: Encryption key must be either 16, 24, or 32 characters long"
                )
            else:
                raise ValueError(value_error)


CURRENT_EPOCH_START = 1705905900000  # UTC timezone
"""Start of the current epoch, used for generating snowflake ids"""

from snowflake import SnowflakeGenerator


class SFGen:
    def __init__(self, instance, epoch=CURRENT_EPOCH_START):
        self.gen = SnowflakeGenerator(instance, epoch=epoch)

    def __call__(self):
        return next(self.gen)
