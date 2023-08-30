import time
import traceback
from pprint import pprint, pformat
from functools import partial
from fastapi import HTTPException
from typing import Tuple, List, Dict, Any, Generator, Union
from sqlalchemy.orm import Session

from chainfury.types import Dag as DagType
from chainfury import Chain, Node, Edge, ai_actions_registry, programatic_actions_registry

from chainfury_server.schemas.prompt_schema import PromptBody
from chainfury_server.database import ChatBot, Session, FuryActions
from chainfury_server.commons import config as c
from chainfury_server.commons.types import CFPromptResult
from chainfury_server.database_utils.prompt import create_prompt
from chainfury_server.database_utils.intermediate_step import create_intermediate_steps, insert_intermediate_steps

from chainfury_server.engines.registry import EngineInterface, engine_registry


logger = c.get_logger(__name__)


class FuryEngine(EngineInterface):
    def run(self, chatbot: ChatBot, prompt: PromptBody, db: Session, start: float) -> CFPromptResult:
        try:
            logger.debug("Adding prompt to database")
            prompt_row = create_prompt(db, chatbot.id, prompt.new_message, prompt.session_id)  # type: ignore

            # Create a Fury chain then run the chain while logging all the intermediate steps
            # prompt.chat_history
            chain = convert_chatbot_dag_to_fury_chain(chatbot=chatbot, db=db)
            callback = FuryThoughts(db, prompt_row.id)
            mainline_out, full_ir = chain(prompt.new_message, thoughts_callback=callback, print_thoughts=False)
            result = CFPromptResult(
                result=str(mainline_out),
                thought=[{"engine": "fury", "ir_steps": callback.count, "thoughts": list(full_ir.keys())}],
                num_tokens=1,
                prompt=prompt_row,
                prompt_id=prompt_row.id,  # type: ignore
            )

            # commit the prompt to DB
            prompt_row.response = result.result  # type: ignore
            prompt_row.time_taken = float(time.time() - start)  # type: ignore
            prompt_row.num_tokens = result.num_tokens  # type: ignore
            db.commit()

            # result["prompt_id"] = prompt_row.id
            logger.debug("Processed graph")
            return result

        except Exception as e:
            traceback.print_exc()
            logger.exception(e)
            raise HTTPException(status_code=500, detail=str(e)) from e

    def stream(
        self, chatbot: ChatBot, prompt: PromptBody, db: Session, start: float
    ) -> Generator[Tuple[Union[CFPromptResult, Dict[str, Any]], bool], None, None]:
        try:
            logger.debug("Adding prompt to database")
            prompt_row = create_prompt(db, chatbot.id, prompt.new_message, prompt.session_id)  # type: ignore

            # Create a Fury chain then run the chain while logging all the intermediate steps
            # prompt.chat_history
            chain = convert_chatbot_dag_to_fury_chain(chatbot=chatbot, db=db)
            callback = FuryThoughts(db, prompt_row.id)
            iterator = chain.stream(prompt.new_message, thoughts_callback=callback, print_thoughts=False)
            full_ir = {}
            mainline_out = ""
            for ir, done in iterator:
                if not done:
                    full_ir.update(ir)
                    yield ir, False
                else:
                    mainline_out = ir
                    yield ir, False

            result = CFPromptResult(
                result=str(mainline_out),
                thought=[{"engine": "fury", "ir_steps": callback.count, "thoughts": list(full_ir.keys())}],
                num_tokens=1,
                prompt=prompt_row,
                prompt_id=prompt_row.id,  # type: ignore
            )

            # commit the prompt to DB
            prompt_row.response = result.result  # type: ignore
            prompt_row.time_taken = float(time.time() - start)  # type: ignore
            prompt_row.num_tokens = result.num_tokens  # type: ignore
            db.commit()

            logger.debug("Processed graph")
            yield result.to_dict(), True

        except Exception as e:
            traceback.print_exc()
            logger.exception(e)
            raise HTTPException(status_code=500, detail=str(e)) from e


engine_registry.register(FuryEngine(), "fury")

# helpers


class FuryThoughts:
    def __init__(self, db, prompt_id):
        self.db = db
        self.prompt_id = prompt_id
        self.count = 0

    def __call__(self, thought):
        intermediate_response = thought.get("value", "")
        if intermediate_response is None:
            intermediate_response = ""
        if type(intermediate_response) != str:
            intermediate_response = str(intermediate_response)
        create_intermediate_steps(self.db, prompt_id=self.prompt_id, intermediate_response=intermediate_response)
        self.count += 1


def convert_chatbot_dag_to_fury_chain(chatbot: ChatBot, db: Session) -> Chain:
    nodes = []
    edges = []

    # convert to dag and checks
    dag = DagType(**chatbot.dag)  # type: ignore
    if not dag.sample:
        raise HTTPException(status_code=400, detail="Dag has no sample")
    if not dag.main_in:
        raise HTTPException(status_code=400, detail="Dag has no main_in")
    if not dag.main_out:
        raise HTTPException(status_code=400, detail="Dag has no main_out")

    # get all the actions by querying the db
    dag_nodes = dag.nodes
    cf_action_ids = set()
    actions_map = dict()
    for x in dag_nodes:
        if not x.cf_id and not x.cf_data:
            raise HTTPException(status_code=400, detail=f"Action {x.id} has no cf_id or cf_data")
        if x.cf_data:
            actions_map[x.id] = x.cf_data
        else:
            cf_action_ids.add(x.cf_id)
    actions: List[FuryActions] = db.query(FuryActions).filter(FuryActions.id.in_(cf_action_ids)).all()
    actions_map.update({str(x.id): x.to_dict() for x in actions})
    for node in dag_nodes:
        cf_action = actions_map.get(node.cf_id, None)
        if node.cf_data:
            # programmatic ones should always be picked from the registry also FE will always send this
            # so server should always check for programatic ones via registry
            if node.cf_data.type == Node.types.PROGRAMATIC:
                try:
                    cf_action = programatic_actions_registry.get(node.cf_id)
                except ValueError:
                    raise HTTPException(status_code=400, detail=f"Action {node.id} not found")
            else:
                cf_action = Node.from_dict(node.cf_data.node)
        elif node.cf_id:
            cf_action = actions_map.get(node.cf_id, None)
        else:
            raise HTTPException(status_code=400, detail=f"Action {node.id} has no cf_id or cf_data")

        # check if this action is in the registry
        if not cf_action:
            try:
                cf_action = ai_actions_registry.get(node.cf_id)
            except ValueError:
                pass
        if not cf_action:
            try:
                cf_action = programatic_actions_registry.get(node.cf_id)
            except ValueError:
                pass
        if not cf_action:
            raise HTTPException(status_code=400, detail=f"Action {node.cf_id} not found")

        # standardsize everything to node
        if not isinstance(cf_action, Node):
            cf_action = Node.from_dict(cf_action)
        cf_action.id = node.id  # override the id
        nodes.append(cf_action)

    # now create all the edges
    dag_edges = dag.edges
    for edge in dag_edges:
        if not (edge.source and edge.target and edge.sourceHandle and edge.targetHandle):
            raise HTTPException(status_code=400, detail=f"Invalid edge {edge}")
        edges.append(Edge(edge.source, edge.sourceHandle, edge.target, edge.targetHandle))

    out = Chain(
        nodes=nodes,
        edges=edges,
        sample=dag.sample,
        main_in=dag.main_in,
        main_out=dag.main_out,
    )
    return out
