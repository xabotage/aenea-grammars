# This file is a command-module for Dragonfly.
#
# (based on the multiedit module from dragonfly-modules project)
# (heavily modified)
# (the original copyright notice is reproduced below)
#
# (c) Copyright 2008 by Christo Butcher
# Licensed under the LGPL, see <http://www.gnu.org/licenses/>
#

import aenea
import aenea.misc
import aenea.vocabulary
import aenea.configuration
import aenea.format

from aenea import (
    AeneaContext,
    AppContext,
    Alternative,
    CompoundRule,
    Dictation,
    DictList,
    DictListRef,
    Grammar,
    IntegerRef,
    Literal,
    ProxyAppContext,
    MappingRule,
    NeverContext,
    Repetition,
    RuleRef,
    Sequence
    )

from aenea import (
    Key,
    Text
    )

# Multiedit wants to take over dynamic vocabulary management.
MULTIEDIT_TAGS = ['multiedit', 'multiedit.count']
aenea.vocabulary.inhibit_global_dynamic_vocabulary('multiedit', MULTIEDIT_TAGS)

#---------------------------------------------------------------------------
# Set up this module's configuration.


command_table = aenea.configuration.make_grammar_commands('multiedit', {
    #### Cursor manipulation
    'up [<n>]':    Key('up:%(n)d'),
    'down [<n>]':  Key('down:%(n)d'),
    'left [<n>]':  Key('left:%(n)d'),
    'right [<n>]': Key('right:%(n)d'),

    'gope [<n>]':  Key('pgup:%(n)d'),
    'drop [<n>]':  Key('pgdown:%(n)d'),

    'lope [<n>]':  Key('c-left:%(n)d'),
    'yope [<n>]':  Key('c-right:%(n)d'),

    'care':        Key('home'),
    'doll':        Key('end'),

    'file top':    Key('c-home'),
    'file toe':    Key('c-end'),

    #### Various keys
    'ace [<n>]':         Key('space:%(n)d'),
    'act':               Key('escape'),
    'chuck [<n>]':       Key('del:%(n)d'),
    'scratch [<n>]':     Key('backspace:%(n)d'),
    'slap [<n>]':        Key('enter:%(n)d'),
    'tab [<n>]':         Key('tab:%(n)d'),

    #### Lines
    'line down [<n>]': Key('home:2, shift:down, end:2, shift:up, c-x, del, down:%(n)d, home:2, enter, up, c-v'),
    'lineup [<n>]':    Key('home:2, shift:down, end:2, shift:up, c-x, del, up:%(n)d, home:2, enter, up, c-v'),
    'nab [<n>]':       Key('home:2, shift:down, down:%(n)d, up, end:2, shift:up, c-c, end:2'),
    'plop [<n>]':      Key('c-v:%(n)d'),
    'squishy [<n>]':   Key('end:2, del, space'),
    'strip':           Key('s-end:2, del'),
    'striss':          Key('s-home:2, del'),
    'trance [<n>]':    Key('home:2, shift:down, down:%(n)d, up, end:2, shift:up, c-c, end:2, enter, c-v'),
    'wipe [<n>]':      Key('home:2, shift:down, down:%(n)d, up, end:2, del, shift:up, backspace'),

    #### Words
    'bump [<n>]':      Key('cs-right:%(n)d, del'),
    'whack [<n>]':     Key('cs-left:%(n)d, del'),
    }, config_key='commands')


class FormatRule(CompoundRule):
    exported = False
    spec = ('[upper | natural] ( proper | camel | rel-path | abs-path | score | sentence | '
            'scope-resolve | jumble | dotword | dashword | sayo | natword | snakeword | brooding-narrative) [<dictation>]')
    extras = [Dictation(name='dictation')]

    def value(self, node):
        words = node.words()

        uppercase = words[0] == 'upper'
        lowercase = words[0] not in ('natural', 'sentence', 'sayo')

        if lowercase:
            words = [word.lower() for word in words]
        if uppercase:
            words = [word.upper() for word in words]

        words = [word.split('\\', 1)[0].replace('-', '') for word in words]
        if words[0].lower() in ('upper', 'natural'):
            del words[0]

        # Saying 'natword' sucks, using 'sayo' as an alias
        if words[0].lower() == 'sayo': words[0] = 'natword'
        function = getattr(aenea.format, 'format_%s' % words[0].lower())
        formatted = function(words[1:])

        return Text(formatted)

format_rule = RuleRef(name='format_rule', rule=FormatRule(name='i'))


# TODO: fork aenea and stick this in aenea.misc
quick_letter_mapping = {
    'A': 'a',
    'B': 'b',
    'C': 'c',
    'D': 'd',
    'E': 'e',
    'F': 'f',
    'G': 'g',
    'H': 'h',
    'I': 'i',
    'J': 'j',
    'K': 'k',
    'L': 'l',
    'M': 'm',
    'N': 'n',
    'O': 'o',
    'P': 'p',
    'Q': 'q',
    'R': 'r',
    'S': 's',
    'T': 't',
    'U': 'u',
    'V': 'v',
    'W': 'w',
    'X': 'x',
    'Y': 'y',
    'Z': 'z'
    }


# Ugly workaround since dragonfly whines when a rule is owned by
# more than one grammar
def generateQuickSpellExtras():
    return [Repetition(
        RuleRef(
            QuickLetterRule(extras=[RuleRef(
                MappingRule(mapping=quick_letter_mapping),
                name='quick_letter'
                )])
            ),
        min=1,
        max=20,
        name='letters'
        )]


class QuickLetterRule(CompoundRule):
    exported = False
    spec = '[cap|capital] <quick_letter>'
    # see generateQuickSpellExtras for <quick_letter>

    def value(self, node):
        letter = node.children[0].children[0].children[1].value() #sigh
        cap = node.words()[0] in ('cap', 'capital')
        if cap: letter = letter.upper()
        return letter

class QuickSpellRule(CompoundRule):
    exported = False
    spec = 'letters <letters>'
    # see generateQuickSpellExtras for <letters>

    def value(self, node):
        letters = node.children[0].children[0].children[1].value() #sigh
        word = ''
        for l in letters: word += l
        return Text(word)


# TODO: this can NOT be the right way to do this...
class NumericDelegateRule(CompoundRule):
    exported = False
    def value(self, node):
        delegates = node.children[0].children[0].children
        value = delegates[0].value()
        if delegates[-1].value() is not None:
            return value * int(delegates[-1].value())
        else:
            return value


def get_static_count_rule():
    return NumericDelegateRule(
        name='SomeCrapHereToAppeaseDragonfly_2',
        spec='<static> [<n>]',
        extras=[
            IntegerRef('n', 1, 100),
            DictListRef(
                'static',
                DictList(
                    'static multiedit.count',
                    aenea.vocabulary.get_static_vocabulary('multiedit.count')
                    )),
        ],
        defaults={'n': 1}
    )

def get_dynamic_count_rule():
    return NumericDelegateRule(
        name='SomeCrapHereToAppeaseDragonfly_1',
        spec='<dynamic> [<n>]',
        extras=[
            IntegerRef('n', 1, 100),
            DictListRef('dynamic', aenea.vocabulary.register_dynamic_vocabulary('multiedit.count')),
        ],
        defaults={'n': 1}
    )

class DigitInsertion(MappingRule):
    exported = False
    mapping = dict(('dig ' + key, val) for (key, val) in aenea.misc.DIGITS.iteritems())

    def value(self, node):
        return Text(MappingRule.value(self, node))

alphabet_mapping = dict((key, Text(value))
                        for (key, value) in aenea.misc.LETTERS.iteritems())

#---------------------------------------------------------------------------
# Generates an element that represents a single keystroke or action.
# Import this function into whatever grammar requires multiedit dictation
# (See the _terminal.py grammar for an example)
def get_multiedit_single_action():
    return Alternative([
        RuleRef(rule=MappingRule(
            mapping=command_table,
            name='c',
            exported=False,
            extras=[
                IntegerRef('n', 1, 100),
                Dictation('text'),
                Dictation('text2'),
            ],
            defaults={
                'n': 1,
            },
        )),
        DictListRef(
           'dynamic multiedit',
           aenea.vocabulary.register_dynamic_vocabulary('multiedit')
           ),
        DictListRef(
           'static multiedit',
           DictList(
               'static multiedit',
               aenea.vocabulary.get_static_vocabulary('multiedit')
               ),
           ),
        RuleRef(rule=get_dynamic_count_rule(), name='SomeCrapHereToAppeaseDragonfly_1a'),
        RuleRef(rule=get_static_count_rule(), name='SomeCrapHereToAppeaseDragonfly_2a'),
        RuleRef(name='x', rule=MappingRule(name='t', mapping=alphabet_mapping)),
        RuleRef(DigitInsertion(), name='DigitInsertion'),
        RuleRef(name='format_rule', rule=FormatRule(name='format_rule')),
        RuleRef(QuickSpellRule(extras=generateQuickSpellExtras()), name='spell_rule'),
        ])

# Can only be used as the last element (as part of finishes), cannot be a
# part of the above single action alternative list because apparently
# dragonfly chokes on a repetition within a repetition

numbers_mapping = dict((key, Text(value))
                        for (key, value) in aenea.misc.DIGITS.iteritems())
alphanumeric_mapping = dict((key, Text(value))
                            for (key, value) in aenea.misc.ALPHANUMERIC.iteritems())

numbers_rule = Sequence([Literal('digits'), Repetition(RuleRef(name='y', rule=MappingRule(name='u', mapping=numbers_mapping)), min=1, max=20)])
alphanumeric_rule = Sequence([Literal('alphanumeric'), Repetition(RuleRef(name='z', rule=MappingRule(name='v', mapping=alphanumeric_mapping)), min=1, max=20)])
finishes = [numbers_rule, alphanumeric_rule]

# Second we create a repetition of keystroke elements.
#  This element will match anywhere between 1 and 16 repetitions
#  of the keystroke elements.  Note that we give this element
#  the name 'sequence' so that it can be used as an extra in
#  the rule definition below.
# Note: when processing a recognition, the *value* of this element
#  will be a sequence of the contained elements: a sequence of
#  actions.
sequence = Repetition(get_multiedit_single_action(), min=1, max=16, name='sequence')


#---------------------------------------------------------------------------
# Here we define the top-level rule which the user can say.


class LiteralRule(CompoundRule):
    spec = 'literal <format_rule>'

    extras = [format_rule]

    def _process_recognition(self, node, extras):
        extras['format_rule'].execute(extras)

# This is the rule that actually handles recognitions.
#  When a recognition occurs, it's _process_recognition()
#  method will be called.  It receives information about the
#  recognition in the 'extras' argument: the sequence of
#  actions and the number of times to repeat them.

class RepeatRule(CompoundRule):
    # Here we define this rule's spoken-form and special elements.
    spec = '[ <sequence> ] [ ( literal <format_rule> )  | <finish> ] [repeat <n> times]'

    extras = [
        sequence,  # Sequence of actions defined above.
        format_rule,
        IntegerRef('n', 1, 100),  # Times to repeat the sequence.
        Alternative(finishes, name='finish'),
    ]

    defaults = {
        'n': 1, # Default repeat count.
        }

    # This method gets called when this rule is recognized.
    # Arguments:
    #  - node -- root node of the recognition parse tree.
    #  - extras -- dict of the 'extras' special elements:
    #   . extras['sequence'] gives the sequence of actions.
    #   . extras['n'] gives the repeat count.
    def _process_recognition(self, node, extras):
        sequence = extras.get('sequence', [])
        count = extras['n']
        for i in range(count):
            for action in sequence:
                action.execute(extras)
            if 'format_rule' in extras:
                extras['format_rule'].execute(extras)
            if 'finish' in extras:
                for action in extras['finish'][1]:
                    action.execute(extras)

#---------------------------------------------------------------------------
# Create and load this module's grammar.

conf = aenea.configuration.ConfigWatcher(('grammar_config', 'multiedit')).conf

local_disable_setting = conf.get('local_disable_context', None)
local_disable_context = NeverContext()
if local_disable_setting is not None:
    if not isinstance(local_disable_setting, basestring):
        print 'Local disable context may only be a string.'
    else:
        local_disable_context = AppContext(str(local_disable_setting))



proxy_disable_setting = conf.get('proxy_disable_context', None)
proxy_disable_context = NeverContext()
if proxy_disable_setting is not None:
    if isinstance(proxy_disable_setting, dict):
        d = {}
        for k, v in proxy_disable_setting.iteritems():
            d[str(k)] = str(v)
        proxy_disable_context = ProxyAppContext(**d)
    else:
        proxy_disable_context = ProxyAppContext(
            title=str(proxy_disable_setting),
            match='substring'
            )


context = AeneaContext(proxy_disable_context, local_disable_context)

grammar = Grammar('multiedit', context=~context)
grammar.add_rule(RepeatRule(name='a'))
grammar.add_rule(LiteralRule())

grammar.load()


# Unload function which will be called at unload time.
def unload():
    global grammar
    aenea.vocabulary.uninhibit_global_dynamic_vocabulary(
        'multiedit',
        MULTIEDIT_TAGS
        )
    for tag in MULTIEDIT_TAGS:
        aenea.vocabulary.unregister_dynamic_vocabulary(tag)
    if grammar:
        grammar.unload()
    grammar = None
