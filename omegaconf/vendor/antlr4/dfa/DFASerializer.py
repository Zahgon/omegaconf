#
# Copyright (c) 2012-2017 The ANTLR Project. All rights reserved.
# Use of this file is governed by the BSD 3-clause license that
# can be found in the LICENSE.txt file in the project root.
#/

# A DFA walker that knows how to dump them to serialized strings.#/
from io import StringIO
from .. import DFA
from ..Utils import str_list
from ..dfa.DFAState import DFAState


class DFASerializer(object):
    __slots__ = ('dfa', 'literalNames', 'symbolicNames')

    def __init__(self, dfa:DFA, literalNames:list=None, symbolicNames:list=None):
        self.dfa = dfa
        self.literalNames = literalNames
        self.symbolicNames = symbolicNames

    def __str__(self):
        if self.dfa.s0 is None:
            return None
        with StringIO() as buf:
            for s in self.dfa.sortedStates():
                n = 0
                if s.edges is not None:
                    n = len(s.edges)
                for i in range(0, n):
                    t = s.edges[i]
                    if t is not None and t.stateNumber != 0x7FFFFFFF:
                        buf.write(self.getStateString(s))
                        label = self.getEdgeLabel(i)
                        buf.write("-")
                        buf.write(label)
                        buf.write("->")
                        buf.write(self.getStateString(t))
                        buf.write('\n')
            output = buf.getvalue()
            if len(output)==0:
                return None
            else:
                return output

    def getEdgeLabel(self, i:int):
        pass

    def getStateString(self, s:DFAState):
        pass

class LexerDFASerializer(DFASerializer):

    def __init__(self, dfa:DFA):
        super().__init__(dfa, None)

    def getEdgeLabel(self, i:int):
        pass
