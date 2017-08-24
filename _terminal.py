# Created for aenea using libraries from the Dictation Toolbox
# https://github.com/dictation-toolbox/dragonfly-scripts
#
# Commands for interacting with terminal and desktop environment
#
# Author: Tony Grosinger
#
# Licensed under LGPL

import aenea
import aenea.configuration
import aenea.misc
from aenea.lax import Key, Text
import dragonfly
from dragonfly import (
        MappingRule,
        CompoundRule,
        Dictation,
        Repetition,
        Literal,
        Alternative,
        RuleRef,
        )

import lib.contexts as ctx

try:
    import aenea.communications
except ImportError:
    print 'Unable to import Aenea client-side modules.'
    raise

grammar = dragonfly.Grammar('terminal', context=(ctx.terminal_context & ~ctx.vim_context))
ruleDigitalInteger = aenea.misc.DigitalInteger('count', 1, 3)

terminal_mapping = aenea.configuration.make_grammar_commands('terminal', {
    # Terminal commands
    # dir is hard to say and recognize. Use something else
    'deer up': Text("cd ..") + Key("enter"),
    'deer list': Text("ls") + Key("enter"),
    'deer list all': Text("ls -lha") + Key("enter"),
    'deer list details': Text("ls -lh") + Key("enter"),
    'deer into': Text("cd "),

    '(terminal|term) clear': Text("clear") + Key("enter"),
    '(terminal|term) left': Key("c-pgup"),
    '(terminal|term) right': Key("c-pgdown"),
    '(terminal|term) new [tab]': Key("cs-t"),
    '(terminal|term) (close|exit)': Key("c-c") + Text("exit") + Key("enter"),

    # Common words
    '(pseudo|sudo|pseudo-)': Text("sudo "),
    '(apt|app) get': Text("sudo apt-get "),
    '(apt|app) get install': Text("sudo apt-get install "),

    'grep': Text("grep "),
    'ack grep': Text("ack-grep "),
    'cat': Text("cat "),
    'pipe [into]': Text(" | "),
    'edit': Text("vim "),
    'tea mucks': Text("tmux "),

    'proc list': Text("ps -e\n"),
    'jobs': Text("jobs\n"),
    'resume': Text("fg\n"),
    'resume [<count>]': Text("fg \%%(count)d\n"),

    'auto comm': Key("tab:2"),
    'scan history': Key("c-r"),
})


class Mapping(dragonfly.MappingRule):
    mapping = terminal_mapping
    extras = [ruleDigitalInteger]

grammar.add_rule(Mapping())
grammar.load()


def unload():
    global grammar
    if grammar:
        grammar.unload()
    grammar = None
