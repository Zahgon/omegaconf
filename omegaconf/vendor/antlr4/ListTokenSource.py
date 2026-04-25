#
# Copyright (c) 2012-2017 The ANTLR Project. All rights reserved.
# Use of this file is governed by the BSD 3-clause license that
# can be found in the LICENSE.txt file in the project root.
#

#
# Provides an implementation of {@link TokenSource} as a wrapper around a list
# of {@link Token} objects.
#
# <p>If the final token in the list is an {@link Token#EOF} token, it will be used
# as the EOF token for every call to {@link #nextToken} after the end of the
# list is reached. Otherwise, an EOF token will be created.</p>
#
from .CommonTokenFactory import CommonTokenFactory
from .Lexer import TokenSource
from .Token import Token


class ListTokenSource(TokenSource):
    __slots__ = ('tokens', 'sourceName', 'pos', 'eofToken', '_factory')

    # Constructs a new {@link ListTokenSource} instance from the specified
    # collection of {@link Token} objects and source name.
    #
    # @param tokens The collection of {@link Token} objects to provide as a
    # {@link TokenSource}.
    # @param sourceName The name of the {@link TokenSource}. If this value is
    # {@code null}, {@link #getSourceName} will attempt to infer the name from
    # the next {@link Token} (or the previous token if the end of the input has
    # been reached).
    #
    # @exception NullPointerException if {@code tokens} is {@code null}
    #
    def __init__(self, tokens:list, sourceName:str=None):
        if tokens is None:
            raise ReferenceError("tokens cannot be null")
        self.tokens = tokens
        self.sourceName = sourceName
        # The index into {@link #tokens} of token to return by the next call to
        # {@link #nextToken}. The end of the input is indicated by this value
        # being greater than or equal to the number of items in {@link #tokens}.
        self.pos = 0
        # This field caches the EOF token for the token source.
        self.eofToken = None
        # This is the backing field for {@link #getTokenFactory} and
        self._factory = CommonTokenFactory.DEFAULT


    #
    # {@inheritDoc}
    #
    @property
    def column(self):
        pass

    #
    # {@inheritDoc}
    #
    def nextToken(self):
        if self.pos >= len(self.tokens):
            if self.eofToken is None:
                start = -1
                if len(self.tokens) > 0:
                    previousStop = self.tokens[len(self.tokens) - 1].stop
                    if previousStop != -1:
                        start = previousStop + 1
                stop = max(-1, start - 1)
                self.eofToken = self._factory.create((self, self.getInputStream()),
                            Token.EOF, "EOF", Token.DEFAULT_CHANNEL, start, stop, self.line, self.column)
            return self.eofToken
        t = self.tokens[self.pos]
        if self.pos == len(self.tokens) - 1 and t.type == Token.EOF:
            self.eofToken = t
        self.pos += 1
        return t

    #
    # {@inheritDoc}
    #
    @property
    def line(self):
        pass

    #
    # {@inheritDoc}
    #
    def getInputStream(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos].getInputStream()
        elif self.eofToken is not None:
            return self.eofToken.getInputStream()
        elif len(self.tokens) > 0:
            return self.tokens[len(self.tokens) - 1].getInputStream()
        else:
            # no input stream information is available
            return None

    #
    # {@inheritDoc}
    #
    def getSourceName(self):
        pass
