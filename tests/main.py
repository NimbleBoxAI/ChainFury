# Copyright © 2023- Frello Technology Private Limited

import os
from tuneapi.utils import folder, joinp

tests = []
curdir = folder(__file__)
for x in os.listdir(curdir):
    if x.startswith("test_") and x.endswith(".py"):
        tests.append(joinp(curdir, x))

for t in tests:
    code = os.system(f"python3 {t} -v")
    if code != 0:
        raise Exception(f"Test {t} failed with code {code}")
