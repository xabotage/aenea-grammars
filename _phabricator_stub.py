from aenea import (
    Grammar,
    MappingRule,
    Text,
    Key,
    Function,
    Dictation,
    Choice,
    Window,
    Config,
    Section,
    Item,
    IntegerRef,
    Alternative,
    RuleRef,
    Repetition,
    CompoundRule,
)
import lib.contexts as ctx

class ArcRule(CompoundRule):
    exported = False
    spec = 'arc <command>'
    extras = [Choice('command', {
        'pull': 'pull',
        'feature': 'feature ',
        'build': 'build',
        'diff': 'diff',
        'canary': 'canary ',
        'land': 'land',
        'lint': 'lint',
        'unit': 'unit',
        })]

    def _process_recognition(self, node, extras):
        Text('arc ' + extras['command']).execute()


grammar = Grammar('phabricator', context=ctx.terminal_context)
grammar.add_rule(ArcRule())
grammar.load()

def unload():
    global grammar
    if grammar:
        grammar.unload()
    grammar = None
