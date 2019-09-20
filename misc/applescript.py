import re
from dataclasses import dataclass

import osascript


SINGLE_QUOTE_PATTERN1 = re.compile(r"'\\''")
SINGLE_QUOTE_PATTERN2 = re.compile(r"'")
DOUBLE_QUOTE_PATTERN = re.compile(r'"')
SENTINEL = 'pSyJmWhXyM'
SENTINEL_PATTERN = re.compile(SENTINEL)
PREAMBLE = """
to quoted(val)
    set val to val as text
	return quoted form of val
end quoted

if app "{app}" is running then tell app "{app}" to ¬
"""


@dataclass
class Element:
    name: str
    of: str = None
    quote: bool = False

    def __str__(self):
        val = self.name
        if self.of:
            val += f' of {self.of}'
        if self.quote:
            val = f'my quoted({val})'
        val = f'quoted form of "{self.name}" & ": " & {val}'
        return val


def build_command(application, *elements):
    inner = '"{" & ' + ' & ", " & '.join(str(e) for e in elements) + ' & "}"'
    return PREAMBLE.format(app=application) + inner


def run(command, application=None):
    if application:
        command = f'if app "{application}" is running then tell app "{application}" to {command}'
    code, out, err = osascript.run(command)
    if code:
        raise Exception(f'({code}) - {err}')
    return out.strip()


def to_json(output):
    output = SINGLE_QUOTE_PATTERN1.sub(SENTINEL, output)
    output = DOUBLE_QUOTE_PATTERN.sub(r'\"', output)
    output = SINGLE_QUOTE_PATTERN2.sub(r'"', output)
    output = SENTINEL_PATTERN.sub("'", output)
    return output
