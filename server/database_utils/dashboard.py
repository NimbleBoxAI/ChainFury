from database import db_session, ChatBot, Prompt


def get_chatbots_from_username(username: str):
    chatbots = []
    db = db_session()
    chatbots = db.query(ChatBot).filter(ChatBot.username == username).all()
    return chatbots


def get_prompts_from_chatbot_id(chatbot_id: int):
    prompts = []
    db = db_session()
    prompts = db.query(Prompt).filter(Prompt.chatbot_id == chatbot_id).all()
    return prompts


def get_prompts_with_user_rating_from_chatbot_id(chatbot_id: int):
    prompts = []
    db = db_session()
    prompts = db.query(Prompt).filter(Prompt.chatbot_id == chatbot_id, Prompt.user_rating != None).all()
    return prompts


def get_prompts_with_chatbot_user_rating_from_chatbot_id(chatbot_id: int):
    prompts = []
    db = db_session()
    prompts = db.query(Prompt).filter(Prompt.chatbot_id == chatbot_id, Prompt.chatbot_user_rating != None).all()
    return prompts


def get_prompts_with_openai_rating_from_chatbot_id(chatbot_id: int):
    prompts = []
    db = db_session()
    prompts = db.query(Prompt).filter(Prompt.chatbot_id == chatbot_id, Prompt.gpt_rating != None).all()
    return prompts
