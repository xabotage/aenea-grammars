from aenea import (
        Key,
        Mouse,
        )

from dragonfly import (
        MappingRule,
        Grammar,
        )

mouse_rule = MappingRule(name='mouse', mapping={
    '[left] click': Mouse('left'),
    'right click': Mouse('right'),
    'middle click': Mouse('middle'),
    'double click': Mouse('left:2'),

    'see click': Key('ctrl:down') + Mouse('left') + Key('ctrl:up'),
    '(shiff|shift) click': Key('shift:down') + Mouse('left') + Key('shift:up'),
    '(all|alt) click': Key('alt:down') + Mouse('left') + Key('alt:up'),

    'drag': Mouse('left:down'),
    'see drag': Key('ctrl:down') + Mouse('left:down'),
    '(shiff|shift) drag': Key('shift:down') + Mouse('left:down'),
    '(all|alt) drag': Key('alt:down') + Mouse('left:down'),
    'release': Mouse('left:up, right:up, middle:up') + Key('ctrl:up, shift:up, alt:up'),

    # Key to switch on and off mouse tracking for LinuxTrack
    'mouse (on|off)': Key('f8'),
    })

grammar = Grammar('mouse')
grammar.add_rule(mouse_rule)
grammar.load()

def unload():
    global grammar
    if grammar:
        grammar.unload()
    grammar = None
