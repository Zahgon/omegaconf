import os
import string
import warnings
from typing import Any, Optional

from omegaconf import Container, Node
from omegaconf._utils import _DEFAULT_MARKER_, _get_value
from omegaconf.basecontainer import BaseContainer
from omegaconf.errors import ConfigKeyError
from omegaconf.grammar_parser import parse
from omegaconf.resolvers.oc import dict


def create(obj: Any, _parent_: Container) -> Any:
    """Create a config object from `obj`, similar to `OmegaConf.create`"""
    from omegaconf import OmegaConf

    assert isinstance(_parent_, BaseContainer)
    return OmegaConf.create(obj, parent=_parent_)


def env(key: str, default: Any = _DEFAULT_MARKER_) -> Optional[str]:
    """
    :param key: Environment variable key
    :param default: Optional default value to use in case the key environment variable is not set.
                    If default is not a string, it is converted with str(default).
                    None default is returned as is.
    :return: The environment variable 'key'. If the environment variable is not set and a default is
            provided, the default is used. If used, the default is converted to a string with str(default).
            If the default is None, None is returned (without a string conversion).
    """
    pass


def decode(expr: Optional[str], _parent_: Container, _node_: Node) -> Any:
    """
    Parse and evaluate `expr` according to the `singleElement` rule of the grammar.

    If `expr` is `None`, then return `None`.
    """
    pass


def deprecated(
    key: str,
    message: str = "'$OLD_KEY' is deprecated. Change your code and config to use '$NEW_KEY'",
    *,
    _parent_: Container,
    _node_: Node,
) -> Any:
    pass


def select(
    key: str,
    default: Any = _DEFAULT_MARKER_,
    *,
    _parent_: Container,
) -> Any:
    pass


__all__ = [
    "create",
    "decode",
    "deprecated",
    "dict",
    "env",
    "select",
]
