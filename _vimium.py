# Created for aenea using libraries from the Dictation Toolbox
# https://github.com/dictation-toolbox/dragonfly-scripts
#
# Commands for interatcting with Chrome. Requires the Vimium extension.
# http://vimium.github.io/
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


chrome_context = aenea.ProxyCustomAppContext(executable="/opt/google/chrome/chrome")
grammar = dragonfly.Grammar('chrome', context=chrome_context)
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
    'page <n>': Key("c-%(n)d"),
    'page new': Key("c-t"),
    'page reopen': Key("cs-t"),
    'page close': Key("c-w"),
    'screw this': Key("c-w"),
    'page back': Key("escape") + Key("s-h"),
    'page forward': Key("escape") + Key("s-l"),
    'refresh': Key("escape") + Key("r"),
    'link': Key("escape") + Key("f"),
    'link new': Key("escape") + Key("s-f"),

    #  Moving around
    'more': Key("escape") + Key("j:10"),
    'much more': Key("escape") + Key("j:20"),
    'more <count>': Key("escape") + Key("j:%(count)d"),
    'less': Key("escape") + Key("k:10"),
    'much less': Key("escape") + Key("k:20"),
    'less <count>': Key("escape") + Key("k:%(count)d"),
    'top': Key("escape") + Key("g, g"),
    'bottom': Key("escape") + Key("s-g"),

    #  Searching
    'find <text>': Key("escape, slash") + Text("%(text)s") + Key("enter"),
    'find': Key("escape, slash"),
    'next': Key("n"),
    'prev|previous': Key("N"),

    #  Miscellaneous
    'address': Key("c-l"),
    'address <text>': Key("c-l") + Text("%(text)s"),
    'zoom': Key("c-equals"),
    'zoom out': Key("c-minus"),
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
    defaults = {'count': 1}

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
