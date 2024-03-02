# Copyright © 2023- Frello Technology Private Limited

import os
import json
import random
from functools import partial
from collections.abc import Iterable
from typing import Dict, List, Any, Tuple, Optional, Generator

from chainfury.utils import to_json, get_random_string, logger


class Message:
    SYSTEM = "system"
    HUMAN = "human"
    GPT = "gpt"
    VALUE = "value"
    FUNCTION = "function"
    FUNCTION_RESPONSE = "function-response"

    # start initialization here
    def __init__(self, value: str | float, role: str):
        if role in ["system", "sys"]:
            role = self.SYSTEM
        elif role in ["user", "human"]:
            role = self.HUMAN
        elif role in ["gpt", "assistant", "machine"]:
            role = self.GPT
        elif role in ["value"]:
            role = self.VALUE
        elif role in ["function", "fn"]:
            role = self.FUNCTION
        elif role in ["function-response", "fn-resp"]:
            role = self.FUNCTION_RESPONSE
        else:
            raise ValueError(f"Unknown role: {role}")
        if value is None:
            raise ValueError("value cannot be None")

        self.role = role
        self.value = value
        self._unq_value = get_random_string(6)

    def __str__(self) -> str:
        try:
            idx = max(os.get_terminal_size().columns - len(self.role) - 40, 10)
        except OSError:
            idx = 50
        return f"<{self.role}: {json.dumps(self.value)[:idx]}>"

    def __repr__(self) -> str:
        return str(self.value)

    def to_dict(self, ft: bool = False):
        """
        if `ft` then export to following format: `{"from": "system/human/gpt", "value": "..."}`
        else export to following format: `{"role": "system/user/assistant", "content": "..."}`
        """
        role = self.role
        if not ft:
            if self.role == self.HUMAN:
                role = "user"
            elif self.role == self.GPT:
                role = "assistant"

        chat_message: Dict[str, str | float]
        if ft:
            chat_message = {"from": role}
        else:
            chat_message = {"role": role}

        if not ft:
            chat_message["content"] = self.value
        else:
            chat_message["value"] = self.value
        return chat_message

    @classmethod
    def from_dict(cls, data):
        return cls(
            value=data.get("value") or data.get("content"),
            role=data.get("from") or data.get("role"),
        )  # type: ignore


### Aliases
human = partial(Message, role=Message.HUMAN)
system = partial(Message, role=Message.SYSTEM)
assistant = partial(Message, role=Message.GPT)


class Chat:
    """
    If the last Message is a "value" then a special tag "koro.regression"="true" is added to the meta.

    Args:
        chats (List[Message]): List of chat messages
        jl (Dict[str, Any]): Optional json-logic
    """

    def __init__(
        self,
        chats: List[Message],
        jl: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None,
        **kwargs,
    ):
        self.chats = chats
        self.jl = jl
        self.model = model

        # check for regression
        if self.chats[-1].role == Message.VALUE:
            kwargs["koro.regression"] = True

        kwargs = {k: v for k, v in sorted(kwargs.items())}
        self.meta = kwargs
        self.keys = list(kwargs.keys())
        self.values = tuple(kwargs.values())

        # avoid special character BS.
        assert not any(["=" in x or "&" in x for x in self.keys])
        if self.values:
            assert all([type(x) in [int, str, float, bool] for x in self.values])

        self.value_hash = hash(self.values)

    def __repr__(self) -> str:
        x = "<TBS "
        for k, v in self.meta.items():
            x += f"{k}={v} "
        for c in self.chats:
            x += f"\n  {c}"
        x += "\n>"
        return x

    def __getattr__(self, __name: str) -> Any:
        if __name in self.meta:
            return self.meta[__name]
        raise AttributeError(f"Attribute {__name} not found")

    # ser/deser

    def to_dict(self, full: bool = False):
        if full:
            return {
                "chats": [x.to_dict() for x in self.chats],
                "jl": self.jl,
                "model": self.model,
                "meta": self.meta,
            }
        return {
            "chats": [x.to_dict() for x in self.chats],
        }

    def to_chat_template(self):
        return self.to_dict()["chats"]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        chats = data.get("chats", None) or data.get("conversations", None)
        if not chats:
            raise ValueError("No chats found")
        return cls(
            chats=[Message.from_dict(x) for x in chats],
            jl=data.get("jl"),
            model=data.get("model"),
            **data.get("meta", {}),
        )

    def to_ft(
        self, id: Any = None, drop_last: bool = False
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        chats = self.chats if not drop_last else self.chats[:-1]
        ft_dict = {
            "id": id or get_random_string(6),
            "conversations": [x.to_dict(ft=True) for x in chats],
        }
        if drop_last:
            ft_dict["last"] = self.chats[-1].to_dict(ft=True)
        return ft_dict, self.meta

    # modifications

    def copy(self) -> "Chat":
        return Chat(
            chats=[x for x in self.chats],
            jl=self.jl,
            model=self.model,
            **self.meta,
        )

    def add(self, message: Message):
        self.chats.append(message)


# these are the classes that we use for tune datasets from r-stack


class TuneChats(list):
    """This class implements some basic container methods for a list of Chat objects"""

    def __init__(self):
        self.keys = {}
        self.items: List[Chat] = []
        self.idx_dict: Dict[int, Tuple[Any, ...]] = {}
        self.key_to_items_idx: Dict[int, List[int]] = {}

    def __repr__(self) -> str:
        return (
            f"TuneChats(unq_keys={len(self.key_to_items_idx)}, items={len(self.items)})"
        )

    def __len__(self) -> int:
        return len(self.items)

    def __iter__(self) -> Generator[Chat, None, None]:
        for x in self.items:
            yield x

    def stream(self) -> Generator[Chat, None, None]:
        for x in self:
            yield x

    def __getitem__(self, __index) -> List[Chat]:
        return self.items[__index]

    def table(self) -> str:
        try:
            from tabulate import tabulate
        except ImportError:
            raise ImportError("Install tabulate to use this method")

        table = []
        for k, v in self.idx_dict.items():
            table.append(
                [
                    *v,
                    len(self.key_to_items_idx[k]),
                    f"{len(self.key_to_items_idx[k])/len(self)*100:0.2f}%",
                ]
            )
        return tabulate(table, headers=[*list(self.keys), "count", "percentage"])

    # data manipulation

    def append(self, __object: Any) -> None:
        if not self.items:
            self.keys = __object.meta.keys()
        if self.keys != __object.meta.keys():
            raise ValueError("Keys should match")
        self.idx_dict.setdefault(__object.value_hash, __object.values)
        self.key_to_items_idx.setdefault(__object.value_hash, [])
        self.key_to_items_idx[__object.value_hash].append(len(self.items))
        self.items.append(__object)

    def add(self, x: Chat):
        return self.append(x)

    def extend(self, __iterable: Iterable) -> None:
        if hasattr(__iterable, "items"):
            for x in __iterable.items:  # type: ignore
                self.append(x)
        elif isinstance(__iterable, Iterable):
            for x in __iterable:
                self.append(x)
        else:
            raise ValueError("Unknown iterable")

    def shuffle(self, seed: Optional[int] = None) -> None:
        """Perform in place shuffle"""
        # shuffle using indices, self.items and self.key_to_items_idx
        idx = list(range(len(self.items)))
        if seed:
            rng = random.Random(seed)
            rng.shuffle(idx)
        else:
            random.shuffle(idx)
        self.items = [self.items[i] for i in idx]
        self.key_to_items_idx = {}
        for i, x in enumerate(self.items):
            self.key_to_items_idx.setdefault(x.value_hash, [])
            self.key_to_items_idx[x.value_hash].append(i)

    def create_te_split(self, test_items: int | float = 0.1) -> Tuple["TuneChats", ...]:
        try:
            import numpy as np
        except ImportError:
            raise ImportError("Install numpy to use `create_te_split` method")

        train_ds = TuneChats()
        eval_ds = TuneChats()
        items_np_arr = np.array(self.items)
        for k, v in self.key_to_items_idx.items():
            if isinstance(test_items, float):
                if int(len(v) * test_items) < 1:
                    raise ValueError(
                        f"Test percentage {test_items} is too high for the dataset key '{k}'"
                    )
                split_ids = random.sample(v, int(len(v) * test_items))
            else:
                if test_items > len(v):
                    raise ValueError(
                        f"Test items {test_items} is too high for the dataset key '{k}'"
                    )
                split_ids = random.sample(v, test_items)

            # get items
            eval_items = items_np_arr[split_ids]
            train_items = items_np_arr[np.setdiff1d(v, split_ids)]
            train_ds.extend(train_items)
            eval_ds.extend(eval_items)

        return train_ds, eval_ds

    # ser / deser

    def to_dict(self):
        return {"items": [x.to_dict() for x in self.items]}

    @classmethod
    def from_dict(cls, data):
        bench_dataset = cls()
        for item in data["items"]:
            bench_dataset.append(Chat.from_dict(item))
        return bench_dataset

    def to_disk(self, folder: str, fmt: Optional[str] = None):
        if fmt:
            logger.warn(
                f"exporting to {fmt} format, you cannot recreate the dataset from this."
            )
        os.makedirs(folder)
        with open(f"{folder}/tuneds.jsonl", "w") as f:
            for sample in self.items:
                if fmt == "sharegpt":
                    item, _ = sample.to_ft()
                elif fmt is None:
                    item = sample.to_dict()
                else:
                    raise ValueError(f"Unknown format: {fmt}")
                f.write(to_json(item, tight=True) + "\n")  # type: ignore

    @classmethod
    def from_disk(cls, folder: str):
        bench_dataset = cls()
        with open(f"{folder}/tuneds.jsonl", "r") as f:
            for line in f:
                item = json.loads(line)
                bench_dataset.append(Chat.from_dict(item))
        return bench_dataset

    def to_hf_dataset(self) -> Tuple["datasets.Dataset", List]:  # type: ignore
        try:
            import datasets as dst
        except ImportError:
            raise ImportError("Install huggingface datasets library to use this method")

        _ds_list = []
        meta_list = []
        for x in self.items:
            sample, meta = x.to_ft()
            _ds_list.append(sample)
            meta_list.append(meta)
        return dst.Dataset.from_list(_ds_list), meta_list

    # properties

    def can_train_koro_regression(self) -> bool:
        return all(["koro.regression" in x.meta for x in self])


class TuneDataset:
    """This class is a container for training and evaulation datasets, useful for serialising items to and from disk"""

    def __init__(self, train: TuneChats, eval: TuneChats):
        self.train_ds = train
        self.eval_ds = eval

    def __repr__(self) -> str:
        return f"TuneDataset(\n  train={self.train_ds},\n  eval={self.eval_ds}\n)"

    @classmethod
    def from_list(cls, items: List["TuneDataset"]):
        train_ds = TuneChats()
        eval_ds = TuneChats()
        for item in items:
            train_ds.extend(item.train_ds)
            eval_ds.extend(item.eval_ds)
        return cls(train=train_ds, eval=eval_ds)

    def to_hf_dict(self) -> Tuple["datasets.DatasetDict", Dict[str, List]]:  # type: ignore
        try:
            import datasets as dst
        except ImportError:
            raise ImportError("Install huggingface datasets library to use this method")

        train_ds, train_meta = self.train_ds.to_hf_dataset()
        eval_ds, eval_meta = self.eval_ds.to_hf_dataset()
        return dst.DatasetDict(train=train_ds, eval=eval_ds), {
            "train": train_meta,
            "eval": eval_meta,
        }

    def to_disk(self, folder: str, fmt: Optional[str] = None):
        config = {}
        config["type"] = "tune"
        config["hf_type"] = fmt
        os.makedirs(folder)
        self.train_ds.to_disk(f"{folder}/train", fmt=fmt)
        self.eval_ds.to_disk(f"{folder}/eval", fmt=fmt)
        to_json(config, fp=f"{folder}/tune_config.json", tight=True)

    @classmethod
    def from_disk(cls, folder: str):
        if not os.path.exists(folder):
            raise ValueError(f"Folder '{folder}' does not exist")
        if not os.path.exists(f"{folder}/train"):
            raise ValueError(f"Folder '{folder}/train' does not exist")
        if not os.path.exists(f"{folder}/eval"):
            raise ValueError(f"Folder '{folder}/eval' does not exist")
        if not os.path.exists(f"{folder}/tune_config.json"):
            raise ValueError(f"File '{folder}/tune_config.json' does not exist")

        # not sure what to do with these
        with open(f"{folder}/tune_config.json", "r") as f:
            config = json.load(f)
        return cls(
            train=TuneChats.from_disk(f"{folder}/train"),
            eval=TuneChats.from_disk(f"{folder}/eval"),
        )
