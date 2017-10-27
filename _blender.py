import aenea.misc
from aenea import (
    Grammar,
    MappingRule,
    Text,
    Key,
    Choice,
    Alternative,
    Literal,
    RuleRef,
    Repetition,
    CompoundRule,
    ProxyCustomAppContext,
)

blender_context = ProxyCustomAppContext(executable='blender')
grammar = Grammar('blender', context=blender_context)

ruleDigitalInteger = aenea.misc.DigitalInteger('count', 1, 4)
axisElement = Choice('axis', {
    'ex': 'x',
    'why': 'y',
    # I'm not Canadian, but "zee" sounds too much like "see"
    'zed': 'z',
    'all but ex': 'X',
    'all but why': 'Y',
    'all but zed': 'Z',
    })

class FloatRule(CompoundRule):
    exported = False
    spec = '[<minus>] <count> [<dot>] [<count>]'
    extras = [
            Literal('minus', name='minus', value='-'),
            ruleDigitalInteger,
            Literal('dot', name='dot', value='.'),
            ]

    def value(self, node):
        delegates = node.children[0].children[0].children
        minus, count1, dot, count2 = [d.value() for d in delegates]
        ret = ''
        if minus is not None: ret += minus
        ret += str(count1)
        if dot is not None: ret += dot
        if count2 is not None: ret += str(count2)
        print 'The return float is: ' + str(ret)
        return ret
floatElement  = RuleRef(name='float', rule=FloatRule())

class TransformOperator(CompoundRule):
    exported = False
    spec = '<trans> [<axis>] [<float>]'
    extras = [
            Choice('trans', {
                'grab': 'g',
                'rote': 'r',
                'scale': 's',
                }),
            axisElement,
            floatElement,
            ]

    def value(self, node):
        delegates = node.children[0].children[0].children
        trans, axis, number = [d.value() for d in delegates]
        ret = trans
        if axis is not None: ret += axis
        if number is not None: ret += number + '\r'
        print 'The return value is: ' + ret
        return Text(ret)


# This is the only high-level rule that is executed
class BlenderRule(CompoundRule):
    spec = '<operator>'
    extras = [
            Repetition(Alternative([
                RuleRef(TransformOperator()),
                ]), max=10, name='operator'),
            ]

    def _process_recognition(self, node, extras):
        commands = []
        print str(extras['operator'])
        if 'operator' in extras:
            # unpack from Repetition element
            for chunk in extras['operator']:
                commands.append(chunk)
        print 'Commands are: ' + str(commands)
        for command in commands:
            command.execute(extras)

grammar.add_rule(BlenderRule())
grammar.load()

def unload():
    global grammar
    if grammar:
        grammar.unload()
    grammar = None
