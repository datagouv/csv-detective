import os

from csv_detective.format import FormatsManager


def generate():
    fmtm = FormatsManager()
    md = (
        "# List of currently available formats\n\n"
        "| name | description | python type | tags | default proportion | mandatory label | example |\n"
        "|------|-------------|-------------|------|--------------------|-----------------|---------|\n"
    )
    template = "| {} | {} | {} | {} | {} | {} | `{}` |\n"

    for label, fmt in fmtm.formats.items():
        md += template.format(
            label,
            fmt.description,
            fmt.python_type,
            ", ".join(fmt.tags),
            fmt.proportion,
            fmt.mandatory_label,
            fmt._test_values[True][0],
        )
    with open(os.path.dirname(os.path.abspath(__file__)) + "/formats.md", "w") as f:
        f.write(md)


if __name__ == "__main__":
    generate()
