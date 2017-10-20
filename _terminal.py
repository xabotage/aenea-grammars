# Created for aenea using libraries from the Dictation Toolbox
# https://github.com/dictation-toolbox/dragonfly-scripts
#
# Commands for interacting with terminal and desktop environment
#
# Author: Tony Grosinger
#
# Licensed under LGPL

from _multiedit import get_multiedit_single_action
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

    '(terminal|term) clear': Text("clear") + Key("enter"),
    '(terminal|term) (left|track)': Key("c-pgup"),
    '(terminal|term) (right|trite)': Key("c-pgdown"),
    '(terminal|term) new [tab]': Key("cs-t"),
    '(terminal|term) (close|exit)': Key("c-c") + Text("exit") + Key("enter"),
    '(terminal|term) abort': Key("c-c"),
    '(terminal|term) edit': Key("c-x") + Key("c-e"),

    'top': Text("top\n"),
    'hey top': Text("htop\n"),
    'jobs': Text("jobs\n"),
    'resume': Text("fg\n"),
    'resume [<count>]': Text("fg %(count)d\n"),

    'auto comm': Key("tab:2"),
    'scan history': Key("c-r"),
})

class LetterMapping(MappingRule):
    exported = False
    mapping = aenea.misc.LETTERS
rule_letter = RuleRef(LetterMapping(), name='letter')


class SudoRule(MappingRule):
    exported = False
    mapping = {'(pseudo|sudo|pseudo-)': Text('sudo ')}
sudo_rule = RuleRef(SudoRule(), name='sudo')


class FlowRule(MappingRule):
    exported = False
    mapping = {
            'pipe [into]': Text(' | '),
            'and (then|also)': Text(' && '),
            '[in the] background': Text(' & '),
            }
flow_rule = RuleRef(FlowRule(), name='flow_rule')


class ProgramMapping(MappingRule):
    exported = False
    mapping = {
            'deer into': Text("cd "),
            'make deer': Text("mkdir "),
            'man': Text("man "),
            'copy': Text("cp "),
            'secure copy': Text("scp "),
            'move': Text("mv "),
            'please remove': Text("rm "),
            'make': Text("make "),
            'ping': Text("ping "),
            'shell': Text("ssh "),
            'mosh': Text("mosh "),
            'change owner': Text("chown "),
            'change mod': Text("chmod "),
            'grep': Text("grep "),
            'ack grep': Text("ack-grep "),
            'eff bags': Text("fbgs "),
            'tea bags': Text("tbgs "),
            'cat': Text("cat "),
            'less': Text("less "),
            'edit': Text("vim "),
            'tea mucks': Text("tmux "),
            'sort': Text("sort "),
            'proc list': Text("ps "),
            'tar': Text("tar "),
            'link': Text("ln "),
            'yum': Text("yum "),
            'yum install': Text("yum install "),
            '(apt|app)': Text("apt "),
            '(apt|app) get': Text("apt-get "),
            '(apt|app) get install': Text("apt-get install "),
            '(apt|app) cash': Text("apt-cache "),
            '(apt|app) install': Text("apt install "),
            '(apt|app) show': Text("apt show "),
            }
program_rule = RuleRef(ProgramMapping(), name='program_rule')


class FlagRule(CompoundRule):
    exported = False
    spec = 'flag [<letters>]'
    extras = [Repetition(rule_letter, min=0, max=5, name='letters'), ]

    def value(self, node):
        letters = node.children[0].children[0].children[1].children[0].value()
        return Text('-' + ''.join(letters) + ' ')
flag_rule = RuleRef(FlagRule(), name='flags')


# Toplevel rule for one-off terminal commands
class Mapping(MappingRule):
    mapping = terminal_mapping
    extras = [ruleDigitalInteger]


# Toplevel rule that harnesses multiedit to allow a comprehensive terminal command
# to be entered without pausing.
class TerminalCommand(CompoundRule):
    spec = ('[<flow1>] [<sudo>] <program> [<flags>] [<multiedit_dictation>] [<flow2>]')
    extras = [
            Alternative([
                flow_rule,
                ], name='flow1'),
            sudo_rule,
            Alternative([
                program_rule,
                ], name='program'),
            flag_rule,
            Repetition(get_multiedit_single_action(), min=1, max=16, name='multiedit_dictation'),
            Alternative([
                flow_rule,
                ], name='flow2'),
            ]

    def _process_recognition(self, node, extras):
        command = Text('')
        order = ('flow1', 'sudo', 'program', 'flags', 'multiedit_dictation', 'flow2')
        for extra in order:
            if extra in extras:
                if extra is 'multiedit_dictation':
                    for action in extras[extra]: command += action
                else:
                    command += extras[extra]
        command.execute()


grammar.add_rule(Mapping())
grammar.add_rule(TerminalCommand())
grammar.load()

def unload():
    global grammar
    if grammar:
        grammar.unload()
    grammar = None
