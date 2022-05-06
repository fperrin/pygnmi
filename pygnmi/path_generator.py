#(c)2019-2021, karneliuk.com

# Modules
from pygnmi.spec.gnmi_pb2 import *
import re


def gnmi_path_generator(path_in_question: str) -> Path:
    """Parses an XPath expression into a gNMI Path

    Accepted syntaxes:

    - "" or "/" for the empty path;

    - "origin://" or "/origin://" for the empty path with origin set to `origin` (e.g., `rfc7951`)

    - "yang-module:container/container[key=value]/other-module:leaf";
      the origin set to yang-module, and specify a key-value selector

    - "/yang-module:container/container[key=value]/other-module:leaf";
       identical to the previous

    - "/container/container[key=value]"; the origin left empty

    - "/container/container[key='complex value:"/[]']"; quoting the value of
      the selector to allow arbitrary char. Single or double quotes are
      accepted. Currently there is no possible escaping of the quote char
      inside of the selector.
    """

    gnmi_path = Path()
    next_active_char = re.compile(r"(/|\[)")
    remaining_path = path_in_question

    while remaining_path:
        parts = next_active_char.split(remaining_path, maxsplit=1)
        tag = parts[0]
        if tag:
            gnmi_path.elem.add(name=tag)

        # Have we reached the end?
        if len(parts) == 1:
            break
        # else: must have split on a token, with non-empty rest
        tag, token, rest = parts

        if token == "/":
            remaining_path = rest
            continue

        # else: looking at a [abc=def] selector
        assert token == "[", (
            f"split {remaining_path}, expected / or [, found {token}"
            f"before: {tag}, after: {rest}"
        )
        try:
            key, rest = rest.split("=", maxsplit=1)
        except:
            raise RuntimeError(
                "Couldnt find '=' sign while reading selector "
                f"in {rest} (expression: {path_in_question})"
            )

        # Find the end of the selector. If looking at a quote mark, find
        # matching quote; otherwise, to the closing square bracket
        quote_char = rest[0]
        if quote_char in ["'", '"']:
            # TODO: allow escaped quotes. Follow xpath's doubling of the char
            # (see https://www.w3.org/TR/xpath-31/#prod-xpath31-StringLiteral)
            # or the more usual backslash escaping?
            m = re.match(rf"{quote_char}([^{quote_char}]*){quote_char}](.*)$", rest)
            if not m:
                raise RuntimeError(
                    f"couldn't find value for quoted key {key} in {rest}"
                    f"(expression: {path_in_question})"
                )

            value = m.group(1)
            rest = m.group(2)
        else:
            try:
                value, rest = rest.split("]", maxsplit=1)
            except:
                raise RuntimeError(
                    f"couldnt find end of selector ']' for {key} in {rest} "
                    f"(expression: {path_in_question})"
                )

        # Now that we've parsed the key=val selector, updated the last element
        if len(gnmi_path.elem) == 0:
            raise RuntimeError(f"path can't start with selector: {path_in_question}")
        last_elem = gnmi_path.elem[-1]
        last_elem.key[key] = value

        # Continue with the remaining string
        remaining_path = rest

    # For the first elem, set the prefix using text before the first ":"
    if len(gnmi_path.elem) >= 1 and ":" in gnmi_path.elem[0].name:
        origin, elemname = gnmi_path.elem[0].name.split(":", 1)
        gnmi_path.origin = origin
        if elemname:
            gnmi_path.elem[0].name = elemname
        else:
            gnmi_path.elem.pop(0)

    return gnmi_path


def gnmi_path_degenerator(gnmi_path) -> str:
    """Parses a gNMI Path int an XPath expression
    """ 
    result = None
    if gnmi_path and gnmi_path.elem:
        resource_path = []
        for path_elem in gnmi_path.elem:
            tp = ''
            if path_elem.name:
                tp += path_elem.name

            if path_elem.key:
                for pk_name, pk_value in sorted(path_elem.key.items()):
                    tp += f'[{pk_name}={pk_value}]'

            resource_path.append(tp)

        result = '/'.join(resource_path)

    return result
