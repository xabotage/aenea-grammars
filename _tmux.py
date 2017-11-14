# Created for aenea using libraries from the Dictation Toolbox
# https://github.com/dictation-toolbox/dragonfly-scripts
#
# Commands for interacting with tmux
#
# Author: Tony Grosinger
#
# Licensed under LGPL

import aenea
import aenea.configuration
from aenea import (
        Key,
        IntegerRef,
        MappingRule,
        )
import dragonfly
import lib.contexts as ctx

grammar = dragonfly.Grammar('tmux', context=ctx.tmux_context)

prefix = 'c-b'

tmux_mapping = aenea.configuration.make_grammar_commands('tmux', {
    'team (right|next)': Key("n"),
    'team (left|previous)': Key("p"),
    'team create': Key("c"),
    'team <n>': Key("%(n)d"),
    'team rename': Key("comma"),
    'team exit': Key("backslash"),
    'team detach': Key("d"),

    'team [pane] vertical': Key("percent"),
    'team [pane] horizontal': Key("dquote"),
    'team swap': Key("o"),
    'team pane up': Key("up"),
    'team pane down': Key("down"),
    'team pane left': Key("left"),
    'team pane right': Key("right"),
    'team pane close': Key("x")
})


class TmuxCommand(MappingRule):
    mapping = tmux_mapping
    extras = [
        IntegerRef('n', 0, 10)
    ]

    def _process_recognition(self, node, extras):
        global prefix
        (Key(prefix) + node.value()).execute()

grammar.add_rule(TmuxCommand())
grammar.load()


def unload():
    global grammar
    if grammar:
        grammar.unload()
    grammar = None
