#!/usr/bin/env python3

import re
import subprocess

USAGE_START = "## Usage\n"
PROMPT = "> koala --help"


def remove_term_codes(line: str) -> str:
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", line)


def replace_usage(readme_lines: list[str], help_output_lines: list[str]) -> list[str]:
    content_start = readme_lines.index(USAGE_START) + 1

    for i in range(content_start, len(readme_lines)):
        if readme_lines[i].startswith("##"):
            content_end = i
            break

    before_content = readme_lines[:content_start]
    after_content = readme_lines[content_end:]

    help_output_lines.insert(0, PROMPT)

    help_output_lines.insert(0, "```")
    help_output_lines.append("```")

    help_output_lines = [remove_term_codes(line) + "\n" for line in help_output_lines]

    return before_content + help_output_lines + after_content


def update_readme():
    raw_output = subprocess.check_output(["koala", "--help"]).decode()
    help_output_lines = [line.strip() for line in raw_output.splitlines()][1:-1]

    with open("README.md", "r") as readme_file:
        readme_content = readme_file.readlines()

        try:
            updated_readme = replace_usage(readme_content, help_output_lines)
        except ValueError:
            print("Failed to find usage section!")
            return

    with open("README.md", "w") as readme_file:
        readme_file.writelines(updated_readme)


if __name__ == "__main__":
    update_readme()
