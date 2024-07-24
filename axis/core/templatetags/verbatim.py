"""
"""


import logging
from django import template

__author__ = "Steven Klass"
__date__ = "5/23/13 1:43 PM"
__copyright__ = "Copyright 2011-2023 Pivotal Energy Solutions. All rights reserved."
__credits__ = [
    "Steven Klass",
]

log = logging.getLogger(__name__)
register = template.Library()


class VerbatimNode(template.Node):
    def __init__(self, text):
        self.text = text

    def render(self, context):
        return self.text


@register.tag
def verbatim(parser, token):
    text = []
    while 1:
        token = parser.tokens.pop(0)
        if token.contents == "endverbatim":
            break
        if token.token_type == template.TOKEN_VAR:
            text.append("{{ ")
        elif token.token_type == template.TOKEN_BLOCK:
            text.append("{%")
        text.append(token.contents)
        if token.token_type == template.TOKEN_VAR:
            text.append(" }}")
        elif token.token_type == template.TOKEN_BLOCK:
            if not text[-1].startswith("="):
                text[-1:-1] = [" "]
            text.append(" %}")
    return VerbatimNode("".join(text))
