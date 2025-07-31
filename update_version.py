import os

import toml

pyproject_file = "pyproject.toml"
with open(pyproject_file, "r") as f:
    pyproject = toml.load(f)

circle_build_num = os.environ.get("CIRCLE_BUILD_NUM", None)
if circle_build_num is None:
    raise ValueError("No CIRCLE_BUILD_NUM found")
pyproject["project"]["version"] += circle_build_num
print("Going forwards with version:", pyproject["project"]["version"])

with open(pyproject_file, "w") as f:
    toml.dump(pyproject, f)
