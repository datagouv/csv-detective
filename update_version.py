import os
import toml


def main():
    pyproject_file = "pyproject.toml"
    with open(pyproject_file, "r") as f:
        pyproject = toml.load(f)

    circle_tag = os.getenv("CIRCLE_TAG", None)
    if circle_tag is not None:
        # This is a tagged release, version should be handled upstream
        print("Has a CIRCLE TAG:", circle_tag)
        return

    circle_build_num = os.getenv("CIRCLE_BUILD_NUM ", None)
    if circle_tag is None:
        raise ValueError("No CIRCLE_BUILD_NUM found")
    pyproject["project"]["version"] += circle_build_num
    print("Going forwards with version:", pyproject["project"]["version"])

    with open(pyproject_file, "w") as f:
        toml.dump(pyproject, f)


if __name__ == "main":
    main()
