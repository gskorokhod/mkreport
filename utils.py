import copy
from datetime import datetime
import re


def format_date(date: datetime):
    day = date.day

    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]

    return date.strftime(f"%A, {day}{suffix} %B, %Y")


def dict_pop(dct: dict, key):
    ans = copy.deepcopy(dct.get(key, None))

    if key in dct:
        del dct[key]

    return ans


def to_snake_case(s: str) -> str:
    s = re.sub(r'\W+', '_', s)
    return s.lower()


def make_metadata_line(key, value, is_quarto=False):
    if isinstance(value, datetime):
        if is_quarto: # Quarto handles dates for us, just pass the timestamp
            value = value.strftime("%Y-%m-%dT%H:%M:%SZ")
        else:
            value = format_date(value)

    if is_quarto:
        value = f'"{value}"'

    return f'{key}: {value}\n'


def update_report_metadata(file_path, metadata):
    """
    Updates the metadata block at the top of a Markdown file and adds any additional metadata

    :param file_path: Path to the Markdown file.
    :param metadata: Dictionary containing the metadata to update or add.
    """
    is_quarto = str(file_path).endswith('.qmd')

    with open(file_path, 'r+') as file:
        lines = file.readlines()
        file.seek(0)

        in_block = False
        metadata_keys_written = set()
        for line in lines:
            if line.strip() == '---':
                if in_block:
                    # Exiting the metadata block, add any additional metadata from ans
                    for key, value in metadata.items():
                        if key not in metadata_keys_written:
                            file.write(make_metadata_line(key, value, is_quarto=is_quarto))
                    in_block = False
                else:
                    # Entering the metadata block
                    in_block = True
                file.write(line)
                continue

            if in_block:
                # Check and replace metadata values if they exist
                found_key = None
                for key, value in metadata.items():
                    if line.startswith(f'{key}:'):
                        line = make_metadata_line(key, value, is_quarto=is_quarto)
                        found_key = key
                        break
                if found_key:
                    metadata_keys_written.add(found_key)
            file.write(line)

        file.truncate()
