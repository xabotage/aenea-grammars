import aenea.configuration

from aenea import Key

from aenea.proxy_contexts import ProxyAppContext

from dragonfly import (
        Grammar,
        MappingRule,
        )

import lib.contexts as ctx

nerd_mapping = aenea.configuration.make_grammar_commands('NERD_tree', {
    # File node mappings
    'open': Key('o'),
    'peek': Key('g, o'),
    'tabbit': Key('t'),
    'throw tab': Key('T'),
    'split': Key('i'),
    'peek split': Key('g, i'),
    'vee split': Key('s'),
    'peek vee split': Key('g, s'),

    # Directory node mappings
    'unfold': Key('O'),
    'fold': Key('x'),
    'fold kids': Key('X'),
    'explore': Key('e'),

    # Bookmark table mappings
    'delete bookmark': Key('D'),

    # Tree navigation mappings
    'root': Key('P'),
    'parent': Key('p'),
    'top child': Key('K'),
    'bot child': Key('J'),
    'child': Key('c-j'),
    'chup': Key('c-k'),

    # Filesystem mappings
    'make root': Key('C'),
    'uprooter': Key('u'),
    'uprooter leave': Key('U'),
    'fresh': Key('r'),
    'fresh root': Key('R'),
    'menu': Key('m'),
    'deer into': Key('c, d'),
    'restore root': Key('C, D'),

    # Tree filtering mappings
    'toggle hidden': Key('I'),
    'toggle filters': Key('f'),
    'toggle files': Key('F'),
    'toggle bookmarks': Key('B'),

    # Other mappings
    'close': Key('q'),
    'zoom': Key('A'),
    'help': Key('question'),
    })

nerd_tree_context = ProxyAppContext(
        match='regex',
        title='.*NERD_tree_[0-9]*.*',
        case_sensitive=True
        ) & ctx.vim_context

nerd_grammar = Grammar('NERD_tree', context=nerd_tree_context)
nerd_grammar.add_rule(MappingRule('NERD_tree_mapping', mapping=nerd_mapping))
nerd_grammar.load()

def unload():
    global nerd_grammar
    if nerd_grammar:
        nerd_grammar.unload()
    nerd_grammar = None
