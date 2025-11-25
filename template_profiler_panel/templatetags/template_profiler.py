from django import template
from django.template import TemplateSyntaxError
from django.template.base import Node


register = template.Library()


@register.tag
def profile(parser, tags):
    bits = tags.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError(
            "profile tag requires a single block name argument, e.g. {% profile 'name' %}"
        )
    nodelist = parser.parse(('endprofile',))
    parser.delete_first_token()
    return ProfileNode(nodelist, bits[1])


class ProfileNode(Node):
    def __init__(self, nodelist, block_name):
        self.nodelist = nodelist
        self.block_name = block_name.strip("'").strip('"')

    def __str__(self):
        return f"Profile {self.block_name}"

    def render(self, context):
        result = self.nodelist.render(context)
        return result
