# Copyright © 2023- Frello Technology Private Limited

import jwt
from fastapi import HTTPException
from passlib.hash import sha256_crypt
from sqlalchemy.orm import Session
from fastapi import Depends, Header
from typing import Annotated, List

from chainfury_server.utils import logger, Env
import chainfury_server.database as DB
import chainfury.types as T

from tuneapi.utils import encrypt, decrypt


def login(
    auth: T.ApiAuthRequest,
    db: Session = Depends(DB.fastapi_db_session),
) -> T.ApiLoginResponse:
    user: DB.User = db.query(DB.User).filter(DB.User.username == auth.username).first()  # type: ignore
    if user is not None and sha256_crypt.verify(auth.password, user.password):  # type: ignore
        token = jwt.encode(
            payload=DB.JWTPayload(username=auth.username, user_id=user.id).to_dict(),
            key=Env.JWT_SECRET(),
        )
        return T.ApiLoginResponse(message="success", token=token)
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")


def sign_up(
    auth: T.ApiSignUpRequest,
    db: Session = Depends(DB.fastapi_db_session),
) -> T.ApiLoginResponse:
    user_exists = False
    email_exists = False
    user: DB.User = db.query(DB.User).filter(DB.User.username == auth.username).first()  # type: ignore
    if user is not None:
        user_exists = True
    user: DB.User = db.query(DB.User).filter(DB.User.email == auth.email).first()  # type: ignore
    if user is not None:
        email_exists = True
    if user_exists and email_exists:
        raise HTTPException(
            status_code=400,
            detail="Username and email already registered",
        )
    elif user_exists:
        raise HTTPException(status_code=400, detail="Username is taken")
    elif email_exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    if not user_exists and not email_exists:  # type: ignore
        user = DB.User(
            username=auth.username,
            email=auth.email,
            password=sha256_crypt.hash(auth.password),
        )  # type: ignore
        db.add(user)
        db.commit()
        token = jwt.encode(
            payload=DB.JWTPayload(username=auth.username, user_id=user.id).to_dict(),
            key=Env.JWT_SECRET(),
        )
        return T.ApiLoginResponse(message="success", token=token)
    else:
        raise HTTPException(status_code=500, detail="Unknown error")


def change_password(
    token: Annotated[str, Header()],
    inputs: T.ApiChangePasswordRequest,
    db: Session = Depends(DB.fastapi_db_session),
) -> T.ApiResponse:
    # validate user
    user = DB.get_user_from_jwt(token=token, db=db)

    if sha256_crypt.verify(inputs.old_password, user.password):
        password = sha256_crypt.hash(inputs.new_password)
        user.password = password  # type: ignore
        db.commit()
        return T.ApiResponse(message="success")
    else:
        raise HTTPException(status_code=401, detail="Invalid old password")


def create_secret(
    inputs: T.ApiToken,
    token: Annotated[str, Header()],
    db: Session = Depends(DB.fastapi_db_session),
) -> T.ApiResponse:
    # validate user
    user = DB.get_user_from_jwt(token=token, db=db)

    # validate inputs
    if len(inputs.token) >= DB.Tokens.MAXLEN_TOKEN:
        raise HTTPException(
            status_code=400,
            detail=f"Token too long, should be less than {DB.Tokens.MAXLEN_TOKEN} characters",
        )
    if len(inputs.key) >= DB.Tokens.MAXLEN_KEY:
        raise HTTPException(
            status_code=400,
            detail=f"Key too long, should be less than {DB.Tokens.MAXLEN_KEY} characters",
        )

    cfs_secrets_password = Env.CFS_SECRETS_PASSWORD()
    if cfs_secrets_password is None:
        logger.error("CFS_TOKEN_PASSWORD not set, cannot create secrets")
        raise HTTPException(500, "internal server error")

    # create a token
    token = DB.Tokens(
        user_id=user.id,
        key=inputs.key,
        value=encrypt(inputs.token, cfs_secrets_password, user.id).decode("utf-8"),
        meta=inputs.meta,
    )  # type: ignore
    db.add(token)
    db.commit()
    return T.ApiResponse(message="success")


def get_secret(
    key: str,
    token: Annotated[str, Header()],
    db: Session = Depends(DB.fastapi_db_session),
) -> T.ApiToken:
    # validate user
    user = DB.get_user_from_jwt(token=token, db=db)

    db_token: DB.Tokens = db.query(DB.Tokens).filter(DB.Tokens.key == key, user.id == user.id).first()  # type: ignore
    if db_token is None:
        raise HTTPException(status_code=404, detail="Token not found")

    cfs_token = Env.CFS_SECRETS_PASSWORD()
    if cfs_token is None:
        logger.error("CFS_TOKEN_PASSWORD not set, cannot create secrets")
        raise HTTPException(500, "internal server error")

    try:
        db_token.value = decrypt(db_token.value, cfs_token, user.id)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Cannot get token")
    return db_token.to_ApiToken()


def list_secret(
    token: Annotated[str, Header()],
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(DB.fastapi_db_session),
) -> T.ApiListTokensResponse:
    """Returns a list of token keys, and metadata. The token values are not returned."""
    # validate user
    user = DB.get_user_from_jwt(token=token, db=db)

    # get tokens
    tokens: List[DB.Tokens] = (
        db.query(DB.Tokens)
        .filter(DB.Tokens.user_id == user.id)  # type: ignore
        .limit(limit)
        .offset(offset)
        .all()
    )
    tokens_resp = []
    for t in tokens:
        tok = t.to_ApiToken()
        tok.token = ""
        tokens_resp.append(tok)
    return T.ApiListTokensResponse(tokens=tokens_resp)


def delete_secret(
    key: str,
    token: Annotated[str, Header()],
    db: Session = Depends(DB.fastapi_db_session),
) -> T.ApiResponse:
    # validate user
    user = DB.get_user_from_jwt(token=token, db=db)

    # validate the user can access the token
    _ = get_secret(key=key, token=token, db=db)

    # delete token
    db_token: DB.Tokens = db.query(DB.Tokens).filter(DB.Tokens.key == key, user.id == user.id).first()  # type: ignore
    if db_token is None:
        raise HTTPException(status_code=404, detail="Token not found")
    db.delete(db_token)
    db.commit()
    return T.ApiResponse(message="success")
