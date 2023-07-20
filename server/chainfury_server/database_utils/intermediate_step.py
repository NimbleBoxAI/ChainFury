from typing import List, Dict
from datetime import datetime
from sqlalchemy.orm import Session

from chainfury_server.database import IntermediateStep


def create_intermediate_steps(
    db: Session,
    prompt_id: int,
    intermediate_prompt: str = "",
    intermediate_response: str = "",
    response_json: Dict = {},
) -> IntermediateStep:
    db_prompt = IntermediateStep(
        prompt_id=prompt_id,
        intermediate_prompt=intermediate_prompt,
        intermediate_response=intermediate_response,
        response_json=response_json,
        created_at=datetime.now(),
    )
    db.add(db_prompt)
    db.commit()
    db.refresh(db_prompt)
    return db_prompt


def insert_intermediate_steps(db: Session, prompt_id: int, steps: List[Dict]) -> List[IntermediateStep]:
    db_intermediate_steps = []
    for step in steps:
        db_intermediate_step = create_intermediate_steps(
            db=db,
            prompt_id=prompt_id,
            intermediate_prompt=f"I need to use {step['action']}({step['action_input']})",
            intermediate_response=f"Observation: {step['observation']}",
        )
        db_intermediate_steps.append(db_intermediate_step)

    return db_intermediate_steps
