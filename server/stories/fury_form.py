import fire
import inspect
import components
from components import ___all__ as components_all

from fury.base import func_to_vars, pyannotation_to_json_schema


def main(v: bool = False):
    for f in (getattr(components, x) for x in components_all):
        if v:
            print("=" * 30)
        print("Validating:", f.__name__, "...", end=" ")
        try:
            out = func_to_vars(f)
            ret = pyannotation_to_json_schema(inspect.signature(f).return_annotation, True, True, True)
        except Exception as e:
            print("FAIL:", e)
            continue
        print("OK!")
        for x in out:
            if v:
                print(">>", x.to_dict())
        if v:
            print("<<", ret.to_dict())


if __name__ == "__main__":
    fire.Fire(main)
