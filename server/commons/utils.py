from sqlalchemy.exc import IntegrityError
from database import db_session, User, Prompt, IntermediateStep
import database_constants as constants


def add_default_user():
    new_user = User(username="admin", password="admin", meta="")
    db = db_session()
    try:
        db.add(new_user)
        db.commit()
    except IntegrityError as e:
        print("Not adding default user")


def filter_prompts_by_date_range(
    chatbot_id: int,
    from_date: str,
    to_date: str,
    page: int,
    page_size: int,
    sort_by: str,
    sort_order: str,
):
    db = db_session()
    order_query = (
        Prompt.created_at.desc()
        if sort_order == constants.SORT_ORDER_DESC
        else Prompt.created_at.asc()
    )
    if sort_by == constants.SORT_BY_TIME_TAKEN:
        order_query = (
            Prompt.time_taken.desc()
            if sort_order == constants.SORT_ORDER_DESC
            else Prompt.time_taken.asc()
        )
    if sort_by == constants.SORT_BY_USER_RATING:
        order_query = (
            Prompt.user_rating.desc()
            if sort_order == constants.SORT_ORDER_DESC
            else Prompt.user_rating.asc()
        )
    if sort_by == constants.SORT_BY_CHATBOT_USER_RATING:
        order_query = (
            Prompt.chatbot_user_rating.desc()
            if sort_order == constants.SORT_ORDER_DESC
            else Prompt.chatbot_user_rating.asc()
        )
    if sort_by == constants.SORT_BY_GPT_RATING:
        order_query = (
            Prompt.gpt_rating.desc()
            if sort_order == constants.SORT_ORDER_DESC
            else Prompt.gpt_rating.asc()
        )
    if sort_by == constants.SORT_BY_CREATED_AT:
        order_query = (
            Prompt.created_at.desc()
            if sort_order == constants.SORT_ORDER_DESC
            else Prompt.created_at.asc()
        )
    prompts = (
        db.query(Prompt)
        .filter(
            Prompt.chatbot_id == chatbot_id,
            Prompt.date >= from_date,
            Prompt.date <= to_date,
        )
        .order_by(order_query)
        .limit(page_size)
        .offset((page - 1) * page_size)
        .all()
    )
    return prompts


def get_prompt_intermediate_data(prompt_id: int):
    db = db_session()
    intermediate_prompts = (
        db.query(IntermediateStep).filter(IntermediateStep.prompt_id == prompt_id).all()
    )
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
