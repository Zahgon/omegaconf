#
# Copyright (c) 2012-2017 The ANTLR Project. All rights reserved.
# Use of this file is governed by the BSD 3-clause license that
# can be found in the LICENSE.txt file in the project root.
#

from io import StringIO
from .Token import Token

from .CommonTokenStream import CommonTokenStream


class TokenStreamRewriter(object):
    __slots__ = ('tokens', 'programs', 'lastRewriteTokenIndexes')

    DEFAULT_PROGRAM_NAME = "default"
    PROGRAM_INIT_SIZE = 100
    MIN_TOKEN_INDEX = 0

    def __init__(self, tokens):
        """
        :type  tokens: antlr4.BufferedTokenStream.BufferedTokenStream
        :param tokens:
        :return:
        """
        super(TokenStreamRewriter, self).__init__()
        self.tokens = tokens
        self.programs = {self.DEFAULT_PROGRAM_NAME: []}
        self.lastRewriteTokenIndexes = {}

    def getTokenStream(self):
        return self.tokens

    def rollback(self, instruction_index, program_name):
        pass

    def deleteProgram(self, program_name=DEFAULT_PROGRAM_NAME):
        pass

    def insertAfterToken(self, token, text, program_name=DEFAULT_PROGRAM_NAME):
        pass

    def insertAfter(self, index, text, program_name=DEFAULT_PROGRAM_NAME):
        pass

    def insertBeforeIndex(self, index, text):
        pass

    def insertBeforeToken(self, token, text, program_name=DEFAULT_PROGRAM_NAME):
        pass

    def insertBefore(self, program_name, index, text):
        pass

    def replaceIndex(self, index, text):
        pass

    def replaceRange(self, from_idx, to_idx, text):
        pass

    def replaceSingleToken(self, token, text):
        pass

    def replaceRangeTokens(self, from_token, to_token, text, program_name=DEFAULT_PROGRAM_NAME):
        pass

    def replace(self, program_name, from_idx, to_idx, text):
        if any((from_idx > to_idx, from_idx < 0, to_idx < 0, to_idx >= len(self.tokens.tokens))):
            raise ValueError(
                'replace: range invalid: {}..{}(size={})'.format(from_idx, to_idx, len(self.tokens.tokens)))
        op = self.ReplaceOp(from_idx, to_idx, self.tokens, text)
        rewrites = self.getProgram(program_name)
        op.instructionIndex = len(rewrites)
        rewrites.append(op)

    def deleteToken(self, token):
        pass

    def deleteIndex(self, index):
        pass

    def delete(self, program_name, from_idx, to_idx):
        pass

    def lastRewriteTokenIndex(self, program_name=DEFAULT_PROGRAM_NAME):
        pass

    def setLastRewriteTokenIndex(self, program_name, i):
        pass

    def getProgram(self, program_name):
        return self.programs.setdefault(program_name, [])

    def getDefaultText(self):
        pass

    def getText(self, program_name, start:int, stop:int):
        """
        :return: the text in tokens[start, stop](closed interval)
        """
        rewrites = self.programs.get(program_name)

        # ensure start/end are in range
        if stop > len(self.tokens.tokens) - 1:
            stop = len(self.tokens.tokens) - 1
        if start < 0:
            start = 0

        # if no instructions to execute
        if not rewrites: return self.tokens.getText(start, stop)
        buf = StringIO()
        indexToOp = self._reduceToSingleOperationPerIndex(rewrites)
        i = start
        while all((i <= stop, i < len(self.tokens.tokens))):
            op = indexToOp.pop(i, None)
            token = self.tokens.get(i)
            if op is None:
                if token.type != Token.EOF: buf.write(token.text)
                i += 1
            else:
                i = op.execute(buf)

        if stop == len(self.tokens.tokens)-1:
            for op in indexToOp.values():
                if op.index >= len(self.tokens.tokens)-1: buf.write(op.text)

        return buf.getvalue()

    def _reduceToSingleOperationPerIndex(self, rewrites):
        # Walk replaces
        for i, rop in enumerate(rewrites):
            if any((rop is None, not isinstance(rop, TokenStreamRewriter.ReplaceOp))):
                continue
            # Wipe prior inserts within range
            inserts = [op for op in rewrites[:i] if isinstance(op, TokenStreamRewriter.InsertBeforeOp)]
            for iop in inserts:
                if iop.index == rop.index:
                    rewrites[iop.instructionIndex] = None
                    rop.text = '{}{}'.format(iop.text, rop.text)
                elif all((iop.index > rop.index, iop.index <= rop.last_index)):
                    rewrites[iop.instructionIndex] = None

            # Drop any prior replaces contained within
            prevReplaces = [op for op in rewrites[:i] if isinstance(op, TokenStreamRewriter.ReplaceOp)]
            for prevRop in prevReplaces:
                if all((prevRop.index >= rop.index, prevRop.last_index <= rop.last_index)):
                    rewrites[prevRop.instructionIndex] = None
                    continue
                isDisjoint = any((prevRop.last_index<rop.index, prevRop.index>rop.last_index))
                if all((prevRop.text is None, rop.text is None, not isDisjoint)):
                    rewrites[prevRop.instructionIndex] = None
                    rop.index = min(prevRop.index, rop.index)
                    rop.last_index = min(prevRop.last_index, rop.last_index)
                    print('New rop {}'.format(rop))
                elif (not(isDisjoint)):
                    raise ValueError("replace op boundaries of {} overlap with previous {}".format(rop, prevRop))

        # Walk inserts
        for i, iop in enumerate(rewrites):
            if any((iop is None, not isinstance(iop, TokenStreamRewriter.InsertBeforeOp))):
                continue
            prevInserts = [op for op in rewrites[:i] if isinstance(op, TokenStreamRewriter.InsertBeforeOp)]
            for prev_index, prevIop in enumerate(prevInserts):
                if prevIop.index == iop.index and type(prevIop) is TokenStreamRewriter.InsertBeforeOp:
                    iop.text += prevIop.text
                    rewrites[prev_index] = None
                elif prevIop.index == iop.index and type(prevIop) is TokenStreamRewriter.InsertAfterOp:
                    iop.text = prevIop.text + iop.text
                    rewrites[prev_index] = None
            # look for replaces where iop.index is in range; error
            prevReplaces = [op for op in rewrites[:i] if isinstance(op, TokenStreamRewriter.ReplaceOp)]
            for rop in prevReplaces:
                if iop.index == rop.index:
                    rop.text = iop.text + rop.text
                    rewrites[i] = None
                    continue
                if all((iop.index >= rop.index, iop.index <= rop.last_index)):
                    raise ValueError("insert op {} within boundaries of previous {}".format(iop, rop))

        reduced = {}
        for i, op in enumerate(rewrites):
            if op is None: continue
            if reduced.get(op.index): raise ValueError('should be only one op per index')
            reduced[op.index] = op

        return reduced

    class RewriteOperation(object):
        __slots__ = ('tokens', 'index', 'text', 'instructionIndex')

        def __init__(self, tokens, index, text=""):
            """
            :type tokens: CommonTokenStream
            :param tokens:
            :param index:
            :param text:
            :return:
            """
            self.tokens = tokens
            self.index = index
            self.text = text
            self.instructionIndex = 0

        def execute(self, buf):
            """
            :type buf: StringIO.StringIO
            :param buf:
            :return:
            """
            return self.index

        def __str__(self):
            return '<{}@{}:"{}">'.format(self.__class__.__name__, self.tokens.get(self.index), self.text)

    class InsertBeforeOp(RewriteOperation):

        def __init__(self, tokens, index, text=""):
            super(TokenStreamRewriter.InsertBeforeOp, self).__init__(tokens, index, text)

        def execute(self, buf):
            buf.write(self.text)
            if self.tokens.get(self.index).type != Token.EOF:
                buf.write(self.tokens.get(self.index).text)
            return self.index + 1

    class InsertAfterOp(InsertBeforeOp):
        pass

    class ReplaceOp(RewriteOperation):
        __slots__ = 'last_index'

        def __init__(self, from_idx, to_idx, tokens, text):
            super(TokenStreamRewriter.ReplaceOp, self).__init__(tokens, from_idx, text)
            self.last_index = to_idx

        def execute(self, buf):
            if self.text:
                buf.write(self.text)
            return self.last_index + 1

        def __str__(self):
            if self.text:
                return '<ReplaceOp@{}..{}:"{}">'.format(self.tokens.get(self.index), self.tokens.get(self.last_index),
                                                        self.text)
