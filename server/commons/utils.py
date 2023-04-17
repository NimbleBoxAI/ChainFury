import jwt
from passlib.hash import sha256_crypt
from sqlalchemy.exc import IntegrityError
from database import db_session, User, Prompt, IntermediateStep, Template
from commons import config as c
import database_constants as constants
from fastapi import HTTPException
from sqlalchemy import func
import json

logger = c.get_logger(__name__)


def add_default_user():
    admin_password = sha256_crypt.hash("admin")
    new_user = User(username="admin", password=admin_password, meta="")
    db = db_session()
    try:
        db.add(new_user)
        db.commit()
    except IntegrityError as e:
        logger.info("Not adding default user")


def add_default_templates():
    db = db_session()
    try:
        with open("./examples/index.json") as f:
            data = json.load(f)
        for template_data in data:
            template = db.query(Template).filter_by(id=template_data["id"]).first()
            if template:
                template.name = template_data["name"]
                template.description = template_data["description"]
                with open("./examples/" + template_data["dag"]) as f:
                    dag = json.load(f)
                template.dag = dag
            else:
                with open("./examples/" + template_data["dag"]) as f:
                    dag = json.load(f)
                template = Template(name=template_data["name"], description=template_data["description"], dag=dag)
                db.add(template)
        db.commit()
    except IntegrityError as e:
        logger.info("Not adding default templates")


def get_user_from_jwt(token):
    try:
        payload = jwt.decode(
            token,
            key=c.JWT_SECRET,
            algorithms=["HS256"],
        )
    except Exception as e:
        logger.exception("Could not decide JWT token")
        raise HTTPException(status_code=401, detail="Could not decode JWT token")
    return payload.get("username")


def verify_user(username):
    db = db_session()
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise Exception("User not found")


def filter_prompts_by_date_range(
    chatbot_id: str,
    from_date: str,
    to_date: str,
    page: int,
    page_size: int,
    sort_by: str,
    sort_order: str,
):
    db = db_session()
    order_query = Prompt.created_at.desc() if sort_order == constants.SORT_ORDER_DESC else Prompt.created_at.asc()
    if sort_by == constants.SORT_BY_TIME_TAKEN:
        order_query = Prompt.time_taken.desc() if sort_order == constants.SORT_ORDER_DESC else Prompt.time_taken.asc()
    if sort_by == constants.SORT_BY_USER_RATING:
        order_query = Prompt.user_rating.desc() if sort_order == constants.SORT_ORDER_DESC else Prompt.user_rating.asc()
    if sort_by == constants.SORT_BY_CHATBOT_USER_RATING:
        order_query = Prompt.chatbot_user_rating.desc() if sort_order == constants.SORT_ORDER_DESC else Prompt.chatbot_user_rating.asc()
    if sort_by == constants.SORT_BY_GPT_RATING:
        order_query = Prompt.gpt_rating.desc() if sort_order == constants.SORT_ORDER_DESC else Prompt.gpt_rating.asc()
    if sort_by == constants.SORT_BY_CREATED_AT:
        order_query = Prompt.created_at.desc() if sort_order == constants.SORT_ORDER_DESC else Prompt.created_at.asc()
    prompts = (
        db.query(Prompt)
        .filter(
            Prompt.chatbot_id == chatbot_id,
            Prompt.created_at >= from_date,
            Prompt.created_at <= to_date,
        )
        .order_by(order_query)
        .limit(page_size)
        .offset((page - 1) * page_size)
        .all()
    )
    return prompts


def get_prompt_intermediate_data(prompt_id: int):
    db = db_session()
    intermediate_prompts = db.query(IntermediateStep).filter(IntermediateStep.prompt_id == prompt_id).all()
    if intermediate_prompts is not None:
        return intermediate_prompts
    else:
        return None


def get_prompt_from_prompt_id(prompt_id: int):
    db = db_session()
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if prompt is not None:
        return prompt
    else:
        return None


def update_chatbot_user_rating(prompt_id: int, rating: constants.PromptRating):
    db = db_session()
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if prompt is not None:
        if prompt.chatbot_user_rating is not None:
            raise HTTPException(
                status_code=400,
                detail=f"Chatbot user rating already exists",
            )
        prompt.chatbot_user_rating = rating
        db.commit()
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Unable to find the prompt",
        )
    return prompt.chatbot_user_rating


def update_internal_user_rating(prompt_id: int, rating: constants.PromptRating):
    db = db_session()
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if prompt is not None:
        prompt.user_rating = rating
        db.commit()
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Unable to find the prompt",
        )
    return prompt.user_rating


def get_hourly_latency_metrics(chatbot_id: str):
    db = db_session()
    hourly_average_latency = (
        db.query(Prompt)
        .filter(Prompt.chatbot_id == chatbot_id)
        .with_entities(
            func.strftime("%Y-%m-%d %H:00:00", Prompt.created_at).label("hour"),
            func.avg(Prompt.time_taken).label("avg_time_taken"),
        )
        .group_by("hour")
        .limit(24)
        .all()
    )

    latency_per_hour = []
    for item in hourly_average_latency:
        latency_per_hour.append({"created_at": item[0], "time": item[1]})
    return latency_per_hour


# def get_cost_metrics(chatbot_id: str):
#     db = db_session()
#     hourly_average_cost = (
#         Prompt.query.filter(Prompt.chatbot_id == chatbot_id)
#         .with_entities(
#             func.date_trunc("token", func.date_trunc("token", Prompt.token)).label("hour"),
#             func.sum(Prompt.token).label("total_token"),
#         )
#         .group_by(func.date_trunc("hour", func.date_trunc("hour", Prompt.token)))
#         .order_by(func.date_trunc("hour", func.date_trunc("hour", Prompt.token)))
#         .limit(24)
#         .all()
#     )
#     cost_per_hour = []
#     for item in hourly_average_cost:
#         cost_per_hour.append({"x": item[0], "y": item[1]})
#     return cost_per_hour


def get_user_score_metrics(chatbot_id: str):
    db = db_session()
    one_count = ()

    one_count = db.query(Prompt).filter((Prompt.chatbot_id == chatbot_id) & (Prompt.user_rating == constants.PromptRating.SAD)).count()
    two_count = db.query(Prompt).filter((Prompt.chatbot_id == chatbot_id) & (Prompt.user_rating == constants.PromptRating.NEUTRAL)).count()
    three_count = db.query(Prompt).filter((Prompt.chatbot_id == chatbot_id) & (Prompt.user_rating == constants.PromptRating.HAPPY)).count()
    user_ratings = []
    user_ratings.append({"bad_count": one_count, "neutral_count": two_count, "good_count": three_count})
    return user_ratings


def get_chatbot_user_score_metrics(chatbot_id: str):
    db = db_session()
    one_count = (
        db.query(Prompt).filter((Prompt.chatbot_id == chatbot_id) & (Prompt.chatbot_user_rating == constants.PromptRating.SAD)).count()
    )
    two_count = (
        db.query(Prompt).filter((Prompt.chatbot_id == chatbot_id) & (Prompt.chatbot_user_rating == constants.PromptRating.NEUTRAL)).count()
    )
    three_count = (
        db.query(Prompt).filter((Prompt.chatbot_id == chatbot_id) & (Prompt.chatbot_user_rating == constants.PromptRating.HAPPY)).count()
    )
    chatbot_user_ratings = []
    chatbot_user_ratings.append({"bad_count": one_count, "neutral_count": two_count, "good_count": three_count})
    return chatbot_user_ratings


def get_gpt_rating_metrics(chatbot_id: str):
    db = db_session()
    one_count = db.query(Prompt).filter((Prompt.chatbot_id == chatbot_id) & (Prompt.gpt_rating == 1)).count()
    two_count = db.query(Prompt).filter((Prompt.chatbot_id == chatbot_id) & (Prompt.gpt_rating == 2)).count()
    three_count = db.query(Prompt).filter((Prompt.chatbot_id == chatbot_id) & (Prompt.gpt_rating == 3)).count()
    gpt_ratings = []
    gpt_ratings.append({"bad_count": one_count, "neutral_count": two_count, "good_count": three_count})
    return gpt_ratings
