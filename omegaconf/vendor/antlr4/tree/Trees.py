#
# Copyright (c) 2012-2017 The ANTLR Project. All rights reserved.
# Use of this file is governed by the BSD 3-clause license that
# can be found in the LICENSE.txt file in the project root.
#


# A set of utility routines useful for all kinds of ANTLR trees.#
from io import StringIO
from ..Token import Token
from ..Utils import escapeWhitespace
from ..tree.Tree import RuleNode, ErrorNode, TerminalNode, Tree, ParseTree

# need forward declaration
Parser  = None

class Trees(object):

     # Print out a whole tree in LISP form. {@link #getNodeText} is used on the
    #  node payloads to get the text for the nodes.  Detect
    #  parse trees and extract data appropriately.
    @classmethod
    def toStringTree(cls, t:Tree, ruleNames:list=None, recog:Parser=None):
        if recog is not None:
            ruleNames = recog.ruleNames
        s = escapeWhitespace(cls.getNodeText(t, ruleNames), False)
        if t.getChildCount()==0:
            return s
        with StringIO() as buf:
            buf.write("(")
            buf.write(s)
            buf.write(' ')
            for i in range(0, t.getChildCount()):
                if i > 0:
                    buf.write(' ')
                buf.write(cls.toStringTree(t.getChild(i), ruleNames))
            buf.write(")")
            return buf.getvalue()

    @classmethod
    def getNodeText(cls, t:Tree, ruleNames:list=None, recog:Parser=None):
        if recog is not None:
            ruleNames = recog.ruleNames
        if ruleNames is not None:
            if isinstance(t, RuleNode):
                if t.getAltNumber()!=0: # should use ATN.INVALID_ALT_NUMBER but won't compile
                    return ruleNames[t.getRuleIndex()]+":"+str(t.getAltNumber())
                return ruleNames[t.getRuleIndex()]
            elif isinstance( t, ErrorNode):
                return str(t)
            elif isinstance(t, TerminalNode):
                if t.symbol is not None:
                    return t.symbol.text
        # no recog for rule names
        payload = t.getPayload()
        if isinstance(payload, Token ):
            return payload.text
        return str(t.getPayload())


    # Return ordered list of all children of this node
    @classmethod
    def getChildren(cls, t:Tree):
        return [ t.getChild(i) for i in range(0, t.getChildCount()) ]

    # Return a list of all ancestors of this node.  The first node of
    #  list is the root and the last is the parent of this node.
    #
    @classmethod
    def getAncestors(cls, t:Tree):
        pass

    @classmethod
    def findAllTokenNodes(cls, t:ParseTree, ttype:int):
        pass

    @classmethod
    def findAllRuleNodes(cls, t:ParseTree, ruleIndex:int):
        pass

    @classmethod
    def findAllNodes(cls, t:ParseTree, index:int, findTokens:bool):
        pass

    @classmethod
    def _findAllNodes(cls, t:ParseTree, index:int, findTokens:bool, nodes:list):
        pass

    @classmethod
    def descendants(cls, t:ParseTree):
        pass
