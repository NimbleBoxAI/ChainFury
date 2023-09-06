import copy
import json
import inspect
import datetime
import traceback
from pprint import pformat
from typing import Any, Union, Optional, Dict, List, Tuple, Callable, Generator
from collections import deque, defaultdict

import jinja2schema
from jinja2schema import model as j2sm

from chainfury.utils import logger, terminal_top_with_text
from chainfury.types import FENode


class Secret(str):
    """This class just means that in Var it will be taken as a password field"""

    def __init__(self, value = ""):
        self.value = value


#
# Vars: this is the base class for all the fields that the user can provide from the front end
#


class Var:
    def __init__(
        self,
        type: Union[str, List["Var"]],
        format: str = "",
        items: List["Var"] = [],
        additionalProperties: Union[List["Var"], "Var"] = [],
        password: bool = False,
        #
        required: bool = False,
        placeholder: str = "",
        show: bool = False,
        name: str = "",
        *,
        loc: Optional[Tuple] = (),
    ):
        """`Var` is a single input / output for a node.

        Args:
            type (Union[str, List[Var]]): The type of the variable. If it is a list, then it is a list of Var objects.
            format (str, optional): The format of the variable. Defaults to "".
            items (List[Var], optional): If the type is a list, then this is the list of Var objects that are in the list. Defaults to [].
            additionalProperties (Union[List[Var], Var], optional): If the type is an object, then this is the list of Var objects that are in the object. Defaults to [].
            password (bool, optional): If the type is a string, then this is whether it is a password field. Defaults to False.
            required (bool, optional): Whether this field is required. Defaults to False.
            placeholder (str, optional): The placeholder text for this field. Defaults to "".
            show (bool, optional): Whether this field should be shown. Defaults to False.
            name (str, optional): The name of this field. Defaults to "".
            loc (Optional[Tuple], optional): The location of this field. Defaults to ().
        """
        self.type = type
        self.format = format
        self.items = items or []
        self.additionalProperties = additionalProperties
        self.password = password
        #
        self.required = required
        self.placeholder = placeholder
        self.show = show
        self.name = name
        #
        self.value = None
        self.loc = loc  # this is the location from which this value is extracted

    def __repr__(self) -> str:
        return f"Var({'*' if self.required else ''}name='{self.name}', type='{self.type}', items={self.items}, additionalProperties={self.additionalProperties})"

    def to_dict(self) -> Dict[str, Any]:
        """Serialise this Var to a dictionary that can be JSON serialised and sent to the client.

        Returns:
            Dict[str, Any]: The serialised Var.
        """
        d: Dict[str, Any] = {"type": self.type}
        if type(self.type) == list and len(self.type) and type(self.type[0]) == Var:
            d["type"] = [x.to_dict() for x in self.type]
        if self.format:
            d["format"] = self.format
        if self.items:
            d["items"] = [item.to_dict() for item in self.items]
        if self.additionalProperties:
            if isinstance(self.additionalProperties, Var):
                d["additionalProperties"] = self.additionalProperties.to_dict()
            else:
                d["additionalProperties"] = self.additionalProperties
        if self.password:
            d["password"] = self.password
        #
        if self.required:
            d["required"] = self.required
        if self.placeholder:
            d["placeholder"] = self.placeholder
        if self.show:
            d["show"] = self.show
        if self.name:
            d["name"] = self.name
        if self.loc:
            d["loc"] = self.loc
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Var":
        """Deserialise a Var from a dictionary.

        Args:
            d (Dict[str, Any]): The dictionary to deserialise from.

        Returns:
            Var: The deserialised Var.
        """
        type_val = d.get("type")
        format_val = d.get("format", "")
        items_val = d.get("items", [])
        additional_properties_val = d.get("additionalProperties", [])
        password_val = d.get("password", False)
        required_val = d.get("required", False)
        placeholder_val = d.get("placeholder", "")
        show_val = d.get("show", False)
        name_val = d.get("name", "")
        loc_val = d.get("loc", ())

        if isinstance(type_val, list):
            type_val = [Var.from_dict(x) if isinstance(x, dict) else x for x in type_val]
        elif isinstance(type_val, dict):
            type_val = Var.from_dict(type_val)

        items_val = [Var.from_dict(x) if isinstance(x, dict) else x for x in items_val]
        additional_properties_val = (
            Var.from_dict(additional_properties_val) if isinstance(additional_properties_val, dict) else additional_properties_val
        )

        var = cls(
            type=type_val,  # type: ignore
            format=format_val,
            items=items_val,
            additionalProperties=additional_properties_val,
            password=password_val,
            required=required_val,
            placeholder=placeholder_val,
            show=show_val,
            name=name_val,
            loc=loc_val,
        )
        return var

    def set_value(self, v: Any):
        """Set the value of this Var.

        Args:
            v (Any): The value to set.
        """
        self.value = v


def pyannotation_to_json_schema(
    x: Any,
    allow_any: bool,
    allow_exc: bool,
    allow_none: bool,
    *,
    trace: bool = False,
) -> Var:
    """Function to convert the given annotation from python to a Var which can then be JSON serialised and sent to the
    clients.

    Args:
        x (Any): The annotation to convert.
        allow_any (bool): Whether to allow the `Any` type.
        allow_exc (bool): Whether to allow the `Exception` type.
        allow_none (bool): Whether to allow the `None` type.
        trace (bool, optional): Adds verbosity the schema generation also set FURY_LOG_LEVEL='debug'. Defaults to False.

    Returns:
        Var: The converted annotation.
    """
    if isinstance(x, type):
        if trace:
            logger.debug("t0")

        if x == str:
            return Var(type="string")
        elif x == int or x == float:
            return Var(type="number")
        elif x == bool:
            return Var(type="boolean")
        elif x == bytes:
            return Var(type="string", format="byte")
        elif x == list:
            return Var(type="array", items=[Var(type="string")])
        elif x == dict:
            return Var(type="object", additionalProperties=Var(type="string"))

        # there are some types that are unique to the fury system
        elif x == Secret:
            return Var(type="string", password=True)
        elif x == Model:
            return Var(type=Model.TYPE_NAME, required=False, show=False)
        if x == Exception and allow_exc:
            return Var(type="exception", required=False, show=False)
        elif x == type(None) and allow_none:
            return Var(type="null", required=False, show=False)
        else:
            raise ValueError(f"i0: Unsupported type: {x}. Some of your inputs are not annotated. Write like ... foo(x: str)")
    elif isinstance(x, str):
        if trace:
            logger.debug("t1")
        return Var(type="string")
    elif hasattr(x, "__origin__") and hasattr(x, "__args__"):
        if trace:
            logger.debug("t2")
        if x.__origin__ == list:
            if trace:
                logger.debug("t2.1")
            return Var(
                type="array",
                items=[pyannotation_to_json_schema(x=x.__args__[0], allow_any=allow_any, allow_exc=allow_exc, allow_none=allow_none)],
            )
        elif x.__origin__ == dict:
            if len(x.__args__) == 2 and x.__args__[0] == str:
                if trace:
                    logger.debug("t2.2")
                return Var(
                    type="object",
                    additionalProperties=pyannotation_to_json_schema(
                        x=x.__args__[1], allow_any=allow_any, allow_exc=allow_exc, allow_none=allow_none
                    ),
                )
            else:
                raise ValueError(f"i2: Unsupported type: {x}")
        elif x.__origin__ == tuple:
            if trace:
                logger.debug("t2.3")
            return Var(
                type="array",
                items=[
                    pyannotation_to_json_schema(x=arg, allow_any=allow_any, allow_exc=allow_exc, allow_none=allow_none)
                    for arg in x.__args__
                ],
            )
        elif x.__origin__ == Union:
            # Unwrap union types with None type
            types = [arg for arg in x.__args__ if arg is not None]
            if len(types) == 1:
                if trace:
                    logger.debug("t2.4")
                return pyannotation_to_json_schema(x=types[0], allow_any=allow_any, allow_exc=allow_exc, allow_none=allow_none)
            else:
                if trace:
                    logger.debug("t2.5")
                return Var(
                    type=[
                        pyannotation_to_json_schema(x=typ, allow_any=allow_any, allow_exc=allow_exc, allow_none=allow_none) for typ in types
                    ]
                )
        else:
            raise ValueError(f"i3: Unsupported type: {x}")
    elif isinstance(x, tuple):
        if trace:
            logger.debug("t4")
        return Var(
            type="array",
            items=[
                Var(type="string"),
                pyannotation_to_json_schema(x=x[1], allow_any=allow_any, allow_exc=allow_exc, allow_none=allow_none),
            ]
            * len(x),
        )
    elif x == Any and allow_any:
        if trace:
            logger.debug("t5")
        return Var(type="string")
    else:
        if trace:
            logger.debug("t6")
        raise ValueError(f"i4: Unsupported type: {x}")


def func_to_vars(func: object) -> List[Var]:
    """
    Extracts the signature of a function and converts it to an array of Var objects.

    Args:
        func (Callable): The function to extract the signature from.

    Returns:
        List[Var]: The array of Var objects.
    """
    signature = inspect.signature(func)  # type: ignore
    fields = []
    for param in signature.parameters.values():
        schema = pyannotation_to_json_schema(param.annotation, allow_any=False, allow_exc=False, allow_none=False)
        schema.required = param.default is inspect.Parameter.empty
        schema.name = param.name
        schema.placeholder = str(param.default) if param.default is not inspect.Parameter.empty else ""
        if not schema.name.startswith("_"):
            schema.show = True
        fields.append(schema)
    return fields


def func_to_return_vars(func, returns: Dict[str, Tuple]) -> List[Var]:
    """
    Analyses the return annotation type of the signature of a function and converts it to an array of named Var objects.

    Args:
        func (Callable): The function to extract the signature from.
        returns (Dict[str, Tuple]): The dictionary of return types.

    Returns:
        List[Var]: The array of Var objects.
    """
    signature = inspect.signature(func)
    schema = pyannotation_to_json_schema(signature.return_annotation, allow_any=False, allow_exc=True, allow_none=True)
    if not (
        schema.type == "array"
        and len(schema.items) == 2
        and type(schema.items[1].type) == list
        and any(x.type == "exception" for x in schema.items[1].type)
    ):
        raise ValueError("Interface requires return type Tuple[..., Optional[Exception]] where ... is JSON serializable")

    # take the names provided in returns and populate the returning field
    logger.debug(f"RETURNS: {returns}")
    ret = schema.items[0]
    logger.debug(f"RET: {ret}")
    if ret.type == "array":
        assert len(returns) in [1, len(ret.items)], f"For array outputs, returns should either be 1 or {len(ret.items)}, got {len(returns)}"
        if len(returns) == 1:
            ret.items[0].name = next(iter(returns))
            ret.items[0].loc = returns[next(iter(returns))]
        for i, n in zip(ret.items, returns):
            i.name = n
            i.loc = returns[n]
        ret = ret.items
    else:
        assert len(returns) == 1, "Items that are not arrays can have only 1 returning var. This can also be a bug"
        ret.name = next(iter(returns))
        ret.loc = returns[next(iter(returns))]
        ret = [
            ret,
        ]
    logger.debug(f"FINAL: {ret}")
    return ret


def jinja_schema_to_vars(v) -> Var:
    """
    Converts a Jinja schema to a Var object.

    Args:
        v ([type]): The Jinja schema.

    Returns:
        Var: The Var object.
    """
    if type(v) == j2sm.Scalar or type(v) == j2sm.String:
        field = Var(type="string", required=True)
    elif type(v) == j2sm.Number:
        field = Var(type="number", required=True)
    elif type(v) == j2sm.Boolean:
        field = Var(type="boolean", required=True)
    elif type(v) == j2sm.Unknown:
        field = Var(type="string", required=True)
    elif type(v) == j2sm.Variable:
        field = Var(type="string", required=True)
    elif type(v) == j2sm.Dictionary:
        field = Var(type="object", required=True)
        all_fields = []
        for k, v in v.items():
            field_item = jinja_schema_to_vars(v)
            field_item.name = k
            all_fields.append(field_item)
        field.additionalProperties = all_fields
    elif type(v) == j2sm.List:
        field = Var(type="array", required=True)
        field.items = [jinja_schema_to_vars(v.item)]
    elif type(v) == j2sm.Tuple:
        field = Var(type="array", required=True)
        if v.items:
            field.items = [jinja_schema_to_vars(x) for x in v.items]
    else:
        raise ValueError(f"cannot handle type {type(v)}")
    return field


def jtype_to_vars(prompt: str) -> List[Var]:
    """
    Converts a Jinja prompt to an array of Var objects.

    Args:
        prompt (str): The Jinja prompt.

    Returns:
        List[Var]: The array of Var objects.
    """
    try:
        s = jinja2schema.infer(prompt)
        fields = []
        for k, v in s.items():
            f = jinja_schema_to_vars(v)
            f.name = k
            fields.append(f)
    except Exception as e:
        logger.error(
            "Could not parse prompt to jinja schema. We support only for/if/filters in jinja2. "
            "Please read here for more information: https://jinja.palletsprojects.com/en/3.1.x/templates/"
        )
        raise e
    return fields


def extract_jinja_indices(data: Union[str, List, Dict[str, Any]], current_index=(), indices=None) -> List:
    """
    This takes in a nested object and returns all the locations where jinja template was detected.

    Args:
        data (Union[str, List, Dict[str, Any]]): The nested object.
        current_index (tuple, optional): The current index. Defaults to ().
        indices ([type], optional): The indices. Defaults to None.

    Returns:
        List: The list of indices.

    Example:
        >>> from chainfury.base import extract_jinja_indices
        >>> extract_jinja_indices({
        ...     "foo": {
        ...         "bar": "{{ baz }}",
        ...         "gaa": ["{{ joo }}"]
        ...    }
        ... })
        [(('foo', 'bar'), Var(...)), (('foo', 'gaa', '0'), Var(...))]
        >>> # more examples
        [(('3', 'content'), [Var('num1', type=string, items=[], additionalProperties=[]), Var('num2', type=string, items=[], additionalProperties=[])])]
        [((), [Var('message', type=string, items=[], additionalProperties=[])])]
        [(('meta_prompt', 'data'), [Var('place', type=string, items=[], additionalProperties=[])])]
        [('0', [Var('name', type=string, items=[], additionalProperties=[])])]
        [(('meta', 'ptype'), [Var('genome', type=string, items=[], additionalProperties=[])])]
        [(('level-0', 'level-1', 'level-2'), [Var('thing', type=string, items=[], additionalProperties=[])]), (('level-0', 'nice'), [Var('feeling', type=string, items=[], additionalProperties=[])])]
        []
    """
    if indices is None:
        indices = []

    if isinstance(data, str):
        fields = jtype_to_vars(data)
        if fields:
            indices.append((current_index, fields))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if current_index:
                if type(current_index) == tuple:
                    new_index = (*current_index, i)
                else:
                    new_index = (current_index, i)
            else:
                new_index = str(i)
            extract_jinja_indices(data=item, current_index=new_index, indices=indices)
    elif isinstance(data, dict):
        for key, value in data.items():
            if current_index:
                if type(current_index) == tuple:
                    new_index = (*current_index, key)
                else:
                    new_index = (current_index, key)
            else:
                new_index = key
            extract_jinja_indices(data=value, current_index=new_index, indices=indices)

    return indices


def get_value_by_keys(obj, keys, *, _first_sentinal: bool = False) -> Any:
    """Takes in an arbitrary nested object and returns the value at the location specified by the keys.

    Args:
        obj (Union[List, Dict[str, Any]]): The nested object.
        keys (Union[str, List[str], Tuple[str, ...]]): The keys. See `extract_jinja_indices` for examples.
        _first_sentinal (bool, optional): flag to tell if this is the first input or not, user should not use this. Defaults to False.

    Returns:
        Any: The value at the location specified by the keys.
    """
    if not keys:
        return obj

    keys = (keys,) if not isinstance(keys, (list, tuple)) else keys
    key = keys[0]

    if key == "*":
        if not _first_sentinal:
            raise ValueError("gvk1: Cannot use wildcard '*' as first key")

        # If the key is "*", apply the subsequent keys to all elements in the current list or dictionary.
        if isinstance(obj, list):
            return [get_value_by_keys(elem, keys[1:], _first_sentinal=True) for elem in obj]
        elif isinstance(obj, dict):
            return {k: get_value_by_keys(v, keys[1:], _first_sentinal=True) for k, v in obj.items()}

    if isinstance(obj, dict):
        return get_value_by_keys(obj.get(key), keys[1:], _first_sentinal=True)
    elif isinstance(obj, (tuple, list)):
        try:
            key = int(key)
        except ValueError:
            raise ValueError(f"gvk2: Cannot use key '{key}' on a list")
        if not type(key) == int:
            raise ValueError(f"gvk3: Cannot use key '{key}' on a list")
        key = int(key)
        if isinstance(key, int) and 0 <= key < len(obj):
            return get_value_by_keys(obj[key], keys[1:], _first_sentinal=True)

    return None


def put_value_by_keys(obj, keys, value: Any):
    """Takes in an arbitrary nested object and sets the value at the location specified by the keys.

    Args:
        obj (Union[List, Dict[str, Any]]): The nested object.
        keys (Union[str, List[str], Tuple[str, ...]]): The keys. See `extract_jinja_indices` for examples.
        value (Any): The value to set.
    """
    if not keys:
        return

    keys = (keys,) if not isinstance(keys, (list, tuple)) else keys
    key = keys[0]
    if len(keys) == 1:
        if isinstance(obj, dict):
            obj[key] = value
        elif isinstance(obj, list) and isinstance(key, int) and 0 <= key < len(obj):
            obj[key] = value
    else:
        if isinstance(obj, dict):
            if key not in obj or not isinstance(obj[key], (dict, list)):
                obj[key] = {} if isinstance(keys[1], str) else []
            put_value_by_keys(obj[key], keys[1:], value)
        elif isinstance(obj, list) and isinstance(key, int) and 0 <= key < len(obj):
            if not isinstance(obj[key], (dict, list)):
                obj[key] = {} if isinstance(keys[1], str) else []
            put_value_by_keys(obj[key], keys[1:], value)


#
# Model: Each model is the processing engine of the AI actions. It is responsible for keeping
#        the state of each of the wrapped functions for different API calls.
#


class Model:
    TYPE_NAME = "model"
    """constant for the type name"""

    def __init__(
        self,
        collection_name: str,
        id: str,
        fn: object,
        description,
        usage: List[Union[str, int]] = [],
        tags=[],
    ):
        """Defines a single callable model.

        Args:
            collection_name (str): The name of the collection.
            id (str): The id of the model.
            fn (Callable): The callable to wrap.
            description (str): The description of the model.
            usage (List[Union[str, int]], optional): The location that tells usage for a call. Defaults to [].
            tags (List[str], optional): The tags for the model. Defaults to [].
        """
        self.collection_name = collection_name
        self.id = id
        self.fn = fn
        self.description = description
        self.usage = usage
        self.vars = func_to_vars(fn)
        self.tags = tags

    def __repr__(self) -> str:
        return f"Model('{self.collection_name}', '{self.id}')"

    def to_dict(self, no_vars: bool = False) -> Dict[str, Any]:
        """Converts the model to a dictionary.

        Args:
            no_vars (bool, optional): Whether to include the vars. Defaults to False.

        Returns:
            Dict[str, Any]: The dictionary representation of the model.
        """
        return {
            "collection_name": self.collection_name,
            "id": self.id,
            "description": self.description,
            "usage": self.usage,
            "vars": [x.to_dict() for x in self.vars] if not no_vars else [],
            "tags": self.tags,
        }

    def __call__(self, model_data: Dict[str, Any]) -> Tuple[Any, Optional[Exception]]:
        """Calls the model with the given data.

        Args:
            model_data (Dict[str, Any]): The data to pass to the model.

        Returns:
            Tuple[Any, Optional[Exception]]: The result of the model and the exception if any.
        """
        try:
            out = self.fn(**model_data)  # type: ignore
            return out, None
        except Exception as e:
            return traceback.format_exc(), e


#
# Node: Each box that is drag and dropped in the UI is a Node, it will tell what kind of things are
#       its inputs, outputs and fields that are shown in the UI. It can be of different types and
#       it only wraps teh
#


class NodeType:
    PROGRAMATIC = "programatic"
    """constant for the programatic node type"""
    AI = "ai-powered"
    """constant for the AI node type"""
    MEMORY = "memory"
    """constant for the memory node type"""


class Node:
    types = NodeType()

    def __init__(
        self,
        id: str,
        type: str,
        fn: object,  # the function to call
        fields: List[Var],
        outputs: List[Var],
        description: str = "",
        tags: List[str] = [],
    ):
        """Node is a single unit of computation in a Dag. All the actions are considered as nodes.

        Args:
            id (str): The id of the node.
            type (str): The type of the node. See `Node.types` for valid types.
            fn (object): The function to call.
            fields (List[Var]): The fields of the node.
            outputs (List[Var]): The outputs of the node.
            description (str, optional): The description of the node. Defaults to "".
            tags (List[str], optional): The tags for the node. Defaults to [].
        """
        # some bacic checks
        _valid_types = [getattr(NodeType, x) for x in dir(NodeType) if not x.startswith("__")]
        if type not in _valid_types:
            raise ValueError(f"Invalid node type: {type}, {_valid_types}")

        # set the values
        self.id = id
        self.type = type
        self.description = description
        self.fields: List[Var] = fields
        self.outputs: List[Var] = outputs
        self.fn = fn
        self.tags = tags

    def __repr__(self) -> str:
        out = f"FuryNode{{ ('{self.id}', '{self.type}') ["
        for f in self.fields:
            if f.required:
                out += f"\n      {f},"
        out += f"\n] ({len(self.fields)}) => ({len(self.outputs)}) ["
        for o in self.outputs:
            out += f"\n      {o},"
        out += f"\n] }}"
        return out

    def has_field(self, field: str) -> bool:
        """helper function to check if the node has a field with the given name.

        Args:
            field (str): The name of the field to check.

        Returns:
            bool: True if the node has the field, False otherwise.
        """
        return any([x.name == field for x in self.fields])

    def to_dict(self) -> Dict[str, Any]:
        """Converts the node to a dictionary.

        Returns:
            Dict[str, Any]: The dictionary representation of the node.
        """
        from chainfury.agent import AIAction, Memory

        fn = {}
        name = self.id
        if isinstance(self.fn, AIAction):
            fn = self.fn.to_dict(no_vars=True)
            name = fn.pop("action_name")
        elif isinstance(self.fn, Memory):
            fn = self.fn.to_dict()
        elif callable(self.fn):
            fn = {
                "fn_name": self.fn.__name__,  # type: ignore
                "fn_module": self.fn.__module__,
            }

        return {
            "id": self.id,
            "type": self.type,
            "fn": fn,
            "name": name,
            "description": self.description,
            "fields": [field.to_dict() for field in self.fields],
            "outputs": [o.to_dict() for o in self.outputs],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], verbose: bool = False) -> "Node":
        """Creates a node from a dictionary.

        Args:
            data (Dict[str, Any]): The dictionary representation of the node.
            verbose (bool, optional): Whether to print verbose logs. Defaults to False.

        Returns:
            Node: The node created from the dictionary.
        """
        if verbose:
            logger.info("Creating node from dict: %s", data)
        fields = [Var.from_dict(x) for x in data["fields"]]
        outputs = [Var.from_dict(x) for x in data["outputs"]]
        fn = data["fn"]
        if not fn:
            raise ValueError(f"Invalid fn: {fn}")

        from chainfury.agent import AIAction, Memory

        node_type = data["type"]
        if node_type == NodeType.AI:
            fn = AIAction.from_dict(fn)
        elif node_type == NodeType.MEMORY:
            fn = Memory.from_dict(fn)
        elif node_type == NodeType.PROGRAMATIC and isinstance(fn, dict):
            import importlib

            fn = getattr(importlib.import_module(fn["fn_module"]), fn["fn_name"])

        return cls(
            id=data["id"],
            type=node_type,
            fn=fn,
            description=data["description"],
            fields=fields,
            outputs=outputs,
        )

    def to_json(self, indent=None) -> str:
        """Converts the node to a json string.

        Args:
            indent (int, optional): The indent to use. Defaults to None.

        Returns:
            str: The json string representation of the node.
        """
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_json(cls, data: str) -> "Node":
        """Creates a node from a json string.

        Args:
            data (str): The json string representation of the node.

        Returns:
            Node: The node created from the json string.
        """
        return cls.from_dict(json.loads(data))

    def __call__(self, data: Dict[str, Any], print_thoughts: bool = False) -> Tuple[Any, Optional[Exception]]:
        """Calls the node with the given data.

        Args:
            data (Dict[str, Any]): The data to pass to the node.
            print_thoughts (bool, optional): Whether to print the thoughts of the node, useful for debugging. Defaults to False.

        Returns:
            Tuple[Any, Optional[Exception]]: The result of the node and the exception if any.
        """
        data_keys = set(data.keys())
        template_keys = set([x.name for x in self.fields])
        try:
            if not data_keys.issubset(template_keys):
                raise ValueError(f"Invalid keys passed to node '{self.id}': {data_keys - template_keys}")
            if print_thoughts:
                print(f"Node: {self.id}")
                print("Inputs:\n------")
                print(pformat(data))

            _out = self.fn(**data)  # type: ignore
            out = _out[0] if isinstance(_out, tuple) else _out
            err = _out[1] if isinstance(_out, tuple) and len(_out) > 1 else None
            if err:
                raise err

            # this is where we have to polish this outgoing result into the structure as configured in self.outputs
            logger.debug(f"> fn_out: {out}")
            logger.debug(f"> OUTPUTS: {self.outputs}")
            for o in self.outputs:
                # logger.debug("  OP:", o.name, o._loc)
                o.set_value(get_value_by_keys(out, o.loc))

            fout = {o.name: o.value for o in self.outputs}
            if print_thoughts:
                print("Outputs:\n-------")
                print(pformat(fout))
            return fout, None
        except Exception as e:
            tb = traceback.format_exc()
            return tb, e


#
# Edge: Each connection between two boxes on the UI is called an Edge, it is only a dataclass without any methods.
#


class Edge:
    """Creates an edge between two nodes.

    Args:
        src_node_id (str): The id of the source node.
        src_node_var (str): The name of the source node variable.
        trg_node_id (str): The id of the target node.
        trg_node_var (str): The name of the target node variable.
    """

    def __init__(
        self,
        src_node_id: str,
        src_node_var: str,
        trg_node_id: str,
        trg_node_var,
    ):
        self.src_node_id = src_node_id
        self.trg_node_id = trg_node_id
        self.src_node_var = src_node_var
        self.trg_node_var = trg_node_var
        self.source = f"{self.src_node_id}/{self.src_node_var}"
        self.target = f"{self.trg_node_id}/{self.trg_node_var}"

    def __repr__(self) -> str:
        out = f"FuryEdge('{self.src_node_id}/{self.src_node_var}' => '{self.trg_node_id}/{self.trg_node_var}')"
        return out

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the edge to a dictionary.

        Returns:
            Dict[str, Any]: The dictionary representation of the edge.
        """
        return {
            "source": self.src_node_id,
            "sourceHandle": self.src_node_var,
            "target": self.trg_node_id,
            "targetHandle": self.trg_node_var,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], verbose: bool = False) -> "Edge":
        """Creates an edge from a dictionary.

        Args:
            data (Dict[str, Any]): The dictionary representation of the edge.

        Returns:
            Edge: The edge created from the dictionary.
        """
        return cls(
            data["source"],
            data["sourceHandle"],
            data["target"],
            data["targetHandle"],
        )


#
# Dag: An entire flow is called the Chain
#


class Chain:
    """A chain is a full flow of nodes and edges.

    Args:
        nodes (List[Node], optional): The list of nodes in the chain. Defaults to [].
        edges (List[Edge], optional): The list of edges in the chain. Defaults to [].
        sample (Dict[str, Any], optional): The sample data to use for the chain. Defaults to {}.
        main_in (str, optional): The name of the input var for the chat input. Defaults to "".
        main_out (str, optional): The name of the output var for the chat output. Defaults to "".
    """

    def __init__(
        self,
        nodes: List[Node] = [],
        edges: List[Edge] = [],
        *,
        sample: Dict[str, Any] = {},
        main_in: str = "",
        main_out: str = "",
    ):
        self.nodes: Dict[str, Node] = {node.id: node for node in nodes}
        self.edges = edges

        if len(self.nodes) == 1:
            assert len(self.edges) == 0, "Cannot have edges with only 1 node"
            self.topo_order = [next(iter(self.nodes))]
        else:
            self.topo_order = topological_sort(self.edges)
        self.sample = sample
        self.main_in = main_in
        self.main_out = main_out

        for node_id in self.topo_order:
            assert node_id in self.nodes, f"Missing node from an edge: {node_id}"

        # to a dry run to validate everything
        self.to_dict()

    def __repr__(self) -> str:
        # return f"FuryDag(nodes: {len(self.nodes)}, edges: {len(self.edges)})"
        out = "FuryDag(\n  nodes: ["
        for n in self.nodes:
            out += f"\n    {n},"
        out += "\n  ],\n  edges: ["
        for e in self.edges:
            out += f"\n    {e},"
        out += f"\n  ]\n  main_in: {self.main_in}\n  main_out: {self.main_out}\n)"
        return out

    def to_dict(self, main_in: str = "", main_out: str = "", sample: Dict[str, Any] = {}) -> Dict[str, Any]:
        """Serializes the chain to a dictionary.

        Args:
            main_in (str, optional): The name of the input var for the chat input. Defaults to "".
            main_out (str, optional): The name of the output var for the chat output. Defaults to "".
            sample (Dict[str, Any], optional): The sample data to use for the chain. Defaults to {}.

        Returns:
            Dict[str, Any]: The dictionary representation of the chain.
        """
        main_in = main_in or self.main_in
        main_out = main_out or self.main_out
        sample = sample or self.sample
        if main_in not in sample:
            logger.error(f"Key should be present in 'sample': {main_in}")
        # assert main_in in sample, f"Invalid key: {main_in}"

        if not (main_in or main_out or sample):
            logger.warning("No main_in, main_out or sample provided, using defaults")
            raise ValueError("No main_in, main_out or sample provided, using defaults")
        return {
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": [edge.to_dict() for edge in self.edges],
            "topo_order": self.topo_order,
            "sample": sample,
            "main_in": main_in,
            "main_out": main_out,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], verbose: bool = False) -> "Chain":
        """Creates a chain from a dictionary.

        Args:
            data (Dict[str, Any]): The dictionary representation of the chain.

        Returns:
            Chain: The chain created from the dictionary.
        """
        nodes = [Node.from_dict(data=x, verbose=verbose) for x in data["nodes"]]
        edges = [Edge.from_dict(data=x, verbose=verbose) for x in data["edges"]]
        return cls(nodes=nodes, edges=edges, sample=data["sample"], main_in=data["main_in"], main_out=data["main_out"])

    def to_json(self, indent=None) -> str:
        """Serializes the chain to a JSON string.

        Returns:
            str: The JSON string representation of the chain.
        """
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_json(cls, data: str):
        """Creates a chain from a JSON string.

        Args:
            data (str): The JSON string representation of the chain.

        Returns:
            Chain: The chain created from the JSON string.
        """
        return cls.from_dict(json.loads(data))

    @classmethod
    def from_id(cls, id: str):
        from chainfury.client import get_chain_from_id

        return get_chain_from_id(id)

    def step(
        self,
        node_id: str,
        pre_data: Dict[str, Any],
        full_ir: Dict[str, Any],
        print_thoughts: bool = False,
        thoughts_callback: Optional[Callable] = None,
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Performs a single step in the chain, useful for manual debugging.

        Args:
            node_id (str): The id of the node to step.
            pre_data (Dict[str, Any]): The data to use for the step.
            full_ir (Dict[str, Any]): The full IR to use for the step.
            print_thoughts (bool, optional): Whether to print the thoughts. Defaults to False.
            thoughts_callback (Optional[Callable], optional): A callback to call with the thoughts. Defaults to None.

        Returns:
            Tuple[Dict[str, Any], Dict[str, Any]]: The currrent output and updated thoughts ir buffer.
        """
        node = self.nodes[node_id]
        incoming_edges = list(filter(lambda edge: edge.trg_node_id == node_id, self.edges))

        # clear out all the nodes that this thing needs into a separate rep
        logger.debug(f">>> Processing node: {node_id}")
        logger.debug(f"Current full_ir: {set(full_ir.keys())}")
        _data = {}

        # first check if this node has any fields that are in the data
        all_keys = list(pre_data.keys())
        for k in all_keys:
            if node.has_field(k):
                _data[k] = pre_data[k]  # don't pop this, some things are shared between actions eg. openai_api_key
            elif k.startswith(node.id):
                _data[k.split("/", 1)[1]] = pre_data.pop(k)  # pop this, it is not needed anymore

        # then merge from the ir buffer
        for edge in incoming_edges:
            logger.debug(f"Incoming edge: {edge}")
            req_key = f"{edge.src_node_id}/{edge.src_node_var}"
            logger.debug(f"Looking for key: {req_key}")
            # need to check if this information is available in the IR buffer, if it is not then this is an error
            ir_value = pre_data.get(req_key, None) or full_ir.get(req_key, {}).get("value", None)
            if ir_value is None:
                raise ValueError(f"Missing value for {req_key}")
            _data[edge.trg_node_var] = ir_value

        # then run the node
        out, err = node(_data, print_thoughts=print_thoughts)
        if err:
            logger.error(f"TRACE: {out}")
            raise err

        # create the thoughts buffer
        yield_dict = {}
        for k, v in out.items():
            key = f"{node_id}/{k}"
            value = {
                "value": v,
                "timestamp": datetime.datetime.now().isoformat(),
            }
            full_ir[key] = value
            thought = {"key": key, **value}
            yield_dict[key] = value
            if thoughts_callback is not None:
                thoughts_callback(thought)
                if print_thoughts:
                    print(thought)

        return yield_dict, full_ir

    def __call__(
        self,
        data: Union[str, Dict[str, Any]],
        thoughts_callback: Optional[Callable] = None,
        print_thoughts: bool = False,
    ) -> Tuple[Var, Dict[str, Any]]:
        """
        Runs the chain on the given data. In this function it will run a full dataflow engine along with thoughts buffer
        and a simple callback system at each step.

        Example:
            >>> chain = Chain(...)
            >>> out, thoughts = chain("Hello world")
            >>> print(out)
            The first man chuckled and shook his head, "You always have the weirdest explanations for everything."
            >>> print(thoughts)
            {
                '38c813a2-850c-448b-8cfb-bd5775cc4b61/answer': {
                    'timestamp': '2023-06-27T16:50:04.178833',
                    'value': '...'
                }
                '1378538b-a15e-475b-9a9d-a31a261165c0/out': {
                    'timestamp': '2023-06-27T16:50:07.818709',
                    'value': '...'
                }
            }

        You can also stream the intermediate responses by setting using `stream_call` method. You can get the exact same
        result as above by iterating over the response and getting the last response.

        Args:
            data (Union[str, Dict[str, Any]]): The data to run the chain on.
            thoughts_callback (Optional[Callable], optional): The callback function to call at each step. Defaults to None.
            print_thoughts (bool, optional): Whether to print the thoughts buffer at each step. Defaults to False.
            stream (bool, optional): Whether to stream the output or not. Defaults to False.

        Returns:
            Tuple[Var, Dict[str, Any]]: The output of the chain and the thoughts buffer.
        """
        if not isinstance(data, dict):
            assert isinstance(data, str), f"Invalid data type: {type(data)}"
            assert self.main_in, "main_in not defined, pass dictionary input"
            data = {self.main_in: data}
        _data = copy.deepcopy(self.sample)  # don't corrupt yourself over multiple calls
        _data.update(data)
        data = _data

        if print_thoughts:
            print(terminal_top_with_text("Chain Starts"))
            print("Inputs:\n------")
            print(pformat(data))

        full_ir = {}
        out = None
        for node_id in self.topo_order:
            yield_dict, full_ir = self.step(
                node_id=node_id,
                pre_data=data,
                full_ir=full_ir,
                print_thoughts=print_thoughts,
                thoughts_callback=thoughts_callback,
            )

        if self.main_out:
            out = full_ir.get(self.main_out)["value"]  # type: ignore

        if print_thoughts:
            print(terminal_top_with_text("Chain Last"))
            print("Outputs:\n------")
            print(pformat(out))
            print(terminal_top_with_text("Chain Ends"))

        return out, full_ir  # type: ignore

    def stream(
        self,
        data: Union[str, Dict[str, Any]],
        thoughts_callback: Optional[Callable] = None,
        print_thoughts: bool = False,
    ) -> Generator[Tuple[Union[Any, Dict[str, Any]], bool], None, None]:
        """
        This is a streaming version of __call__ method. It will yield the intermediate responses as they come in.

        Example:
            >>> chain = Chain(...)
            >>> cf_response_gen = chain.stream("Hello world")
            >>> out = None
            >>> thoughts = {}
            >>> for ir, done in cf_response_gen:
            ...     if done:
            ...         out = ir
            ...     else:
            ...         thoughts.update(ir)
            >>> print(out)
            The first man chuckled and shook his head, "You always have the weirdest explanations for everything."
            >>> print(thoughts)
            {
                '38c813a2-850c-448b-8cfb-bd5775cc4b61/answer': {
                    'timestamp': '2023-06-27T16:50:04.178833',
                    'value': '...'
                }
                '1378538b-a15e-475b-9a9d-a31a261165c0/out': {
                    'timestamp': '2023-06-27T16:50:07.818709',
                    'value': '...'
                }
            }

        Args:
            data (Union[str, Dict[str, Any]]): The data to run the chain on.
            thoughts_callback (Optional[Callable], optional): The callback function to call at each step. Defaults to None.
            print_thoughts (bool, optional): Whether to print the thoughts buffer at each step. Defaults to False.

        Yields:
            Generator[Tuple[Union[Any, Dict[str, Any]], bool], None, None]: The intermediate responses and whether the
            response is the final response or not.
        """
        if not isinstance(data, dict):
            assert isinstance(data, str), f"Invalid data type: {type(data)}"
            assert self.main_in, "main_in not defined, pass dictionary input"
            data = {self.main_in: data}
        _data = copy.deepcopy(self.sample)  # don't corrupt yourself over multiple calls
        _data.update(data)
        data = _data

        if print_thoughts:
            print(terminal_top_with_text("Chain Starts"))
            print("Inputs:\n------")
            print(pformat(data))

        full_ir = {}
        out = None
        for node_id in self.topo_order:
            yield_dict, full_ir = self.step(
                node_id=node_id,
                pre_data=data,
                full_ir=full_ir,
                print_thoughts=print_thoughts,
                thoughts_callback=thoughts_callback,
            )
            yield yield_dict, False

        if print_thoughts:
            print(terminal_top_with_text("Chain Last"))
            print("Outputs:\n------")
            print(pformat(out))
            print(terminal_top_with_text("Chain Ends"))

        if self.main_out:
            out = full_ir.get(self.main_out)["value"]  # type: ignore
        yield out, True


#
# helper functions
#


class NotDAGError(Exception):
    pass


def edge_array_to_adjacency_list(edges: List[Edge]):
    adjacency_lists = {}
    for edge in edges:
        src = edge.src_node_id
        dst = edge.trg_node_id
        if src not in adjacency_lists:
            adjacency_lists[src] = []
        adjacency_lists[src].append(dst)
    return adjacency_lists


def adjacency_list_to_edge_map(adjacency_list) -> List[Edge]:
    edges = []
    for src, dsts in adjacency_list.items():
        for dst in dsts:
            edges.append(Edge(src_node_id=src, src_node_var="", trg_node_id=dst, trg_node_var=""))
    return edges


def topological_sort(edges: List[Edge]) -> List[str]:
    """Topological sort of a DAG, raises NotDAGError if the graph is not a DAG. This is full proof version
    which will work even if the DAG contains several unconnected chains.

    Args:
        edges (List[Edge]): The edges of the DAG

    Returns:
        List[str]: The topologically sorted list of node ids
    """
    adjacency_lists = edge_array_to_adjacency_list(edges)
    in_degree = defaultdict(int)
    for src, dsts in adjacency_lists.items():
        for dst in dsts:
            in_degree[dst] += 1

    # Add all nodes with no incoming edges to the queue
    queue = deque()
    for node in adjacency_lists:
        if in_degree[node] == 0:
            queue.append(node)

    # For each node, remove it from the graph and add it to the sorted list
    sorted_list = []
    edge_nodes_cntr = 0
    while queue:
        node = queue.popleft()
        sorted_list.append(node)
        neighbours = adjacency_lists.get(node, [])
        if not neighbours:
            edge_nodes_cntr += 1
        for neighbor in neighbours:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # Check to see if all edges are removed
    if len(sorted_list) == len(adjacency_lists) + edge_nodes_cntr:
        return sorted_list
    else:
        raise NotDAGError("A cycle exists in the graph.")
