import sys
import warnings
from itertools import zip_longest
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Generator,
    List,
    NoReturn,
    Optional,
    Set,
    Tuple,
    Union,
    cast,
)

from .errors import InterpolationResolutionError
from .vendor.antlr4 import TerminalNode  # type: ignore[attr-defined]

if TYPE_CHECKING:
    from .base import Node  # noqa F401

try:
    from omegaconf.grammar.gen.OmegaConfGrammarLexer import OmegaConfGrammarLexer
    from omegaconf.grammar.gen.OmegaConfGrammarParser import OmegaConfGrammarParser
    from omegaconf.grammar.gen.OmegaConfGrammarParserVisitor import (
        OmegaConfGrammarParserVisitor,
    )

except ModuleNotFoundError:  # pragma: no cover
    print(
        "Error importing OmegaConf's generated parsers, run `python setup.py antlr` to regenerate.",
        file=sys.stderr,
    )
    sys.exit(1)


class GrammarVisitor(OmegaConfGrammarParserVisitor):
    def __init__(
        self,
        node_interpolation_callback: Optional[
            Callable[
                [str, Optional[Set[int]]],
                Optional["Node"],
            ]
        ],
        resolver_interpolation_callback: Optional[Callable[..., Any]],
        memo: Optional[Set[int]],
        **kw: Dict[Any, Any],
    ):
        """
        Constructor.

        :param node_interpolation_callback: Callback function that is called when
            needing to resolve a node interpolation. This function should take a single
            string input which is the key's dot path (ex: `"foo.bar"`).

        :param resolver_interpolation_callback: Callback function that is called when
            needing to resolve a resolver interpolation. This function should accept
            three keyword arguments: `name` (str, the name of the resolver),
            `args` (tuple, the inputs to the resolver), and `args_str` (tuple,
            the string representation of the inputs to the resolver).

        :param kw: Additional keyword arguments to be forwarded to parent class.
        """
        super().__init__(**kw)
        self.node_interpolation_callback = node_interpolation_callback
        self.resolver_interpolation_callback = resolver_interpolation_callback
        self.memo = memo

    def aggregateResult(self, aggregate: List[Any], nextResult: Any) -> List[Any]:
        raise NotImplementedError

    def defaultResult(self) -> NoReturn:
        # Raising an exception because not currently used (like `aggregateResult()`).
        raise NotImplementedError

    def visitConfigKey(self, ctx: OmegaConfGrammarParser.ConfigKeyContext) -> str:
        pass

    def visitConfigValue(self, ctx: OmegaConfGrammarParser.ConfigValueContext) -> Any:
        # text EOF
        pass

    def visitDictKey(self, ctx: OmegaConfGrammarParser.DictKeyContext) -> Any:
        pass

    def visitDictContainer(
        self, ctx: OmegaConfGrammarParser.DictContainerContext
    ) -> Dict[Any, Any]:
        # BRACE_OPEN (dictKeyValuePair (COMMA dictKeyValuePair)*)? BRACE_CLOSE
        pass

    def visitElement(self, ctx: OmegaConfGrammarParser.ElementContext) -> Any:
        # primitive | quotedValue | listContainer | dictContainer
        pass

    def visitInterpolation(
        self, ctx: OmegaConfGrammarParser.InterpolationContext
    ) -> Any:
        pass

    def visitInterpolationNode(
        self, ctx: OmegaConfGrammarParser.InterpolationNodeContext
    ) -> Optional["Node"]:
        # INTER_OPEN
        # DOT*                                                     // relative interpolation?
        # (configKey | BRACKET_OPEN configKey BRACKET_CLOSE)       // foo, [foo]
        # (DOT configKey | BRACKET_OPEN configKey BRACKET_CLOSE)*  // .foo, [foo], .foo[bar], [foo].bar[baz]
        # INTER_CLOSE;

        pass

    def visitInterpolationResolver(
        self, ctx: OmegaConfGrammarParser.InterpolationResolverContext
    ) -> Any:
        # INTER_OPEN resolverName COLON sequence? BRACE_CLOSE
        pass

    def visitDictKeyValuePair(
        self, ctx: OmegaConfGrammarParser.DictKeyValuePairContext
    ) -> Tuple[Any, Any]:
        pass

    def visitListContainer(
        self, ctx: OmegaConfGrammarParser.ListContainerContext
    ) -> List[Any]:
        # BRACKET_OPEN sequence? BRACKET_CLOSE;
        pass

    def visitPrimitive(self, ctx: OmegaConfGrammarParser.PrimitiveContext) -> Any:
        pass

    def visitQuotedValue(self, ctx: OmegaConfGrammarParser.QuotedValueContext) -> str:
        # (QUOTE_OPEN_SINGLE | QUOTE_OPEN_DOUBLE) text? MATCHING_QUOTE_CLOSE
        pass

    def visitResolverName(self, ctx: OmegaConfGrammarParser.ResolverNameContext) -> str:
        pass

    def visitSequence(
        self, ctx: OmegaConfGrammarParser.SequenceContext
    ) -> Generator[Any, None, None]:
        pass

    def visitSingleElement(
        self, ctx: OmegaConfGrammarParser.SingleElementContext
    ) -> Any:
        # element EOF
        pass

    def visitText(self, ctx: OmegaConfGrammarParser.TextContext) -> Any:
        # (interpolation | ANY_STR | ESC | ESC_INTER | TOP_ESC | QUOTED_ESC)+

        # Single interpolation? If yes, return its resolved value "as is".
        pass

    def _createPrimitive(
        self,
        ctx: Union[
            OmegaConfGrammarParser.PrimitiveContext,
            OmegaConfGrammarParser.DictKeyContext,
        ],
    ) -> Any:
        # (ID | NULL | INT | FLOAT | BOOL | UNQUOTED_CHAR | COLON | ESC | WS | interpolation)+
        pass

    def _unescape(
        self,
        seq: List[Union[TerminalNode, OmegaConfGrammarParser.InterpolationContext]],
    ) -> str:
        """
        Concatenate all symbols / interpolations in `seq`, unescaping symbols as needed.

        Interpolations are resolved and cast to string *WITHOUT* escaping their result
        (it is assumed that whatever escaping is required was already handled during the
        resolving of the interpolation).
        """
        pass
