# Created for aenea using libraries from the Dictation Toolbox
# https://github.com/dictation-toolbox/dragonfly-scripts
#
# Commands for interatcting with Firefox. Requires the Vimfx extension.
#
# Author: Tony Grosinger
#
# Licensed under LGPL

import aenea
import aenea.configuration
from aenea.lax import Key, Text, Dictation
from aenea import (
    IntegerRef
)
import dragonfly


firefox_context = aenea.ProxyCustomAppContext(executable="/usr/lib/firefox/firefox")
grammar = dragonfly.Grammar('firefox', context=firefox_context)
ruleDigitalInteger = aenea.misc.DigitalInteger('count', 1, 3)

window_mapping = {
    # Tab navigation
    '(track|trek)': Key("cs-tab"),
    '(track|trek) <n>': Key("cs-tab:%(n)d"),
    'trite': Key("c-tab"),
    'trite <n>': Key("c-tab:%(n)d"),
    'page left': Key("cs-tab"),
    'page left <n>': Key("cs-tab:%(n)d"),
    'page right': Key("c-tab"),
    'page right <n>': Key("c-tab:%(n)d"),
    'page <n>': Key("a-%(n)d"),
    'page new': Key("c-t"),
    'page reopen': Key("cs-t"),
    'page close': Key("c-w"),
    'screw this': Key("c-w"),
    'page back': Key("escape, s-h"),
    'page forward': Key("escape, s-l"),
    'refresh': Key("c-r"),
    'link': Key("escape/100:2, f"),
    'link new': Key("escape, s-f"),

    #  Moving around
    'more': Key("escape, d"),
    'much more': Key("escape, d:2"),
    'more <count>': Key("escape, d:%(count)d"),
    'less': Key("escape, u"),
    'much less': Key("escape, u:2"),
    'less <count>': Key("escape, u:%(count)d"),
    'top': Key("escape, g, g"),
    'bottom': Key("escape, s-g"),

    #  Searching
    'find <text>': Key("escape, slash") + Text("%(text)s") + Key("enter"),
    'find': Key("escape, slash"),
    'next': Key("n"),
    'prev|previous': Key("N"),

    #  Miscellaneous
    'address': Key("c-l"),
    'address <text>': Key("c-l") + Text("%(text)s"),
}

gmail_mapping = {
    'open': Key("o"),
    'inbox': Key("g, i"),
    '[go to] label <text>': Key("g, l") + Text("%(text)s") + Key("enter"),
    'trash': Key("hash"),
    'archive': Key("e"),
    '(earl|early|earlier)': Key("j"),
    '(late|later)': Key("k"),
}


class Mapping(dragonfly.MappingRule):
    mapping = window_mapping
    extras = [
        IntegerRef('n', 1, 99),
        Dictation('text'),
        ruleDigitalInteger,
    ]

class MappingMail(dragonfly.MappingRule):
     mapping = gmail_mapping
     extras = [
        Dictation('text')
     ]


grammar.add_rule(Mapping())
grammar.add_rule(MappingMail())
grammar.load()


def unload():
    global grammar
    if grammar:
        grammar.unload()
    grammar = None
