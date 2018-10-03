from typing import Any, Dict, Sequence, cast

from ..language import ast, DirectiveLocation
from ..pyutils.compat import string_types
from .definition import GraphQLArgument, GraphQLInputType, GraphQLNonNull, is_input_type
from .scalars import GraphQLBoolean, GraphQLString

__all__ = [
    "is_directive",
    "is_specified_directive",
    "specified_directives",
    "GraphQLDirective",
    "GraphQLIncludeDirective",
    "GraphQLSkipDirective",
    "GraphQLDeprecatedDirective",
    "DirectiveLocation",
    "DEFAULT_DEPRECATION_REASON",
]


def is_directive(directive):
    """Test if the given value is a GraphQL directive."""
    return isinstance(directive, GraphQLDirective)


class GraphQLDirective(object):
    """GraphQL Directive

    Directives are used by the GraphQL runtime as a way of modifying execution
    behavior. Type system creators will usually not create these directly.
    """

    def __init__(self, name, locations, args=None, description=None, ast_node=None):
        if not name:
            raise TypeError("Directive must be named.")
        elif not isinstance(name, string_types):
            raise TypeError("The directive name must be a string.")
        if not isinstance(locations, (list, tuple)):
            raise TypeError("{} locations must be a list/tuple.".format(name))
        if not all(isinstance(value, DirectiveLocation) for value in locations):
            try:
                locations = [
                    value
                    if isinstance(value, DirectiveLocation)
                    else DirectiveLocation[value]
                    for value in locations
                ]
            except (KeyError, TypeError):
                raise TypeError(
                    "{} locations must be DirectiveLocation objects.".format(name)
                )
        if args is None:
            args = {}
        elif not isinstance(args, dict) or not all(
            isinstance(key, string_types) for key in args
        ):
            raise TypeError(
                "{} args must be a dict with argument names as keys.".format(name)
            )
        elif not all(
            isinstance(value, GraphQLArgument) or is_input_type(value)
            for value in args.values()
        ):
            raise TypeError(
                "{} args must be GraphQLArgument or input type objects.".format(name)
            )
        else:
            args = {
                name: value
                if isinstance(value, GraphQLArgument)
                else GraphQLArgument(value)
                for name, value in args.items()
            }
        if description is not None and not isinstance(description, string_types):
            raise TypeError("{} description must be a string.".format(name))
        if ast_node and not isinstance(ast_node, ast.DirectiveDefinitionNode):
            raise TypeError(
                "{} AST node must be a DirectiveDefinitionNode.".format(name)
            )
        self.name = name
        self.locations = locations
        self.args = args
        self.description = description
        self.ast_node = ast_node

    def __str__(self):
        return "@{}".format(self.name)

    def __repr__(self):
        return "<{}({})>".format(self.__class__.__name__, self)


# Used to conditionally include fields or fragments.
GraphQLIncludeDirective = GraphQLDirective(
    name="include",
    locations=[
        DirectiveLocation.FIELD,
        DirectiveLocation.FRAGMENT_SPREAD,
        DirectiveLocation.INLINE_FRAGMENT,
    ],
    args={
        "if": GraphQLArgument(
            GraphQLNonNull(GraphQLBoolean), description="Included when true."
        )
    },
    description="Directs the executor to include this field or fragment"
    " only when the `if` argument is true.",
)


# Used to conditionally skip (exclude) fields or fragments:
GraphQLSkipDirective = GraphQLDirective(
    name="skip",
    locations=[
        DirectiveLocation.FIELD,
        DirectiveLocation.FRAGMENT_SPREAD,
        DirectiveLocation.INLINE_FRAGMENT,
    ],
    args={
        "if": GraphQLArgument(
            GraphQLNonNull(GraphQLBoolean), description="Skipped when true."
        )
    },
    description="Directs the executor to skip this field or fragment"
    " when the `if` argument is true.",
)


# Constant string used for default reason for a deprecation:
DEFAULT_DEPRECATION_REASON = "No longer supported"

# Used to declare element of a GraphQL schema as deprecated:
GraphQLDeprecatedDirective = GraphQLDirective(
    name="deprecated",
    locations=[DirectiveLocation.FIELD_DEFINITION, DirectiveLocation.ENUM_VALUE],
    args={
        "reason": GraphQLArgument(
            GraphQLString,
            description="Explains why this element was deprecated,"
            " usually also including a suggestion for how to access"
            " supported similar data."
            " Formatted using the Markdown syntax, as specified by"
            " [CommonMark](https://commonmark.org/).",
            default_value=DEFAULT_DEPRECATION_REASON,
        )
    },
    description="Marks an element of a GraphQL schema as no longer supported.",
)


# The full list of specified directives.
specified_directives = (
    GraphQLIncludeDirective,
    GraphQLSkipDirective,
    GraphQLDeprecatedDirective,
)


def is_specified_directive(directive):
    """Check whether the given directive is one of the specified directives."""
    return any(
        specified_directive.name == directive.name
        for specified_directive in specified_directives
    )
