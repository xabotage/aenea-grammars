# Dragonfly module for controlling vim on Linux modelessly. All verbal commands
# start and end in command mode, making it effective to combine voice and
# keyboard.
#

LEADER = 'comma'

import aenea.config
import aenea.misc
import aenea.vocabulary
import lib.contexts as ctx

from aenea import (
    Key,
    NoAction,
    Text,
    Function
    )

from dragonfly import (
    Alternative,
    AppContext,
    CompoundRule,
    Dictation,
    Grammar,
    MappingRule,
    Repetition,
    RuleRef,
    DictListRef,
    )

grammar = Grammar('vim', context=ctx.vim_context)

VIM_TAGS = ['vim.insertions.code', 'vim.insertions']
aenea.vocabulary.inhibit_global_dynamic_vocabulary('vim', VIM_TAGS, ctx.vim_context)

modeless_engaged = False
def toggle_modeless():
    global modeless_engaged
    print "Toggling modeless state: " + str(not modeless_engaged)
    modeless_engaged = not modeless_engaged

# TODO: this can NOT be the right way to do this...
class NumericDelegateRule(CompoundRule):
    def value(self, node):
        delegates = node.children[0].children[0].children
        value = delegates[-1].value()
        if delegates[0].value() is not None:
            return Text('%s' % delegates[0].value()) + value
        else:
            return value


class _DigitalIntegerFetcher(object):
    def __init__(self):
        self.cached = {}

    def __getitem__(self, length):
        if length not in self.cached:
            self.cached[length] = aenea.misc.DigitalInteger('count', 1, length)
        return self.cached[length]
ruleDigitalInteger = _DigitalIntegerFetcher()


class LetterMapping(MappingRule):
    mapping = aenea.misc.LETTERS
ruleLetterMapping = RuleRef(LetterMapping(), name='LetterMapping')


allCharacterMapping = aenea.misc.ALPHANUMERIC.copy()
for (char, value) in aenea.vocabulary.register_dynamic_vocabulary('vim.insertions').iteritems():
    allCharacterMapping.update({char: value._spec})
class AllCharMapping(MappingRule):
    mapping = allCharacterMapping
ruleAllCharacterMapping = RuleRef(AllCharMapping(), 'AllCharacter')


non_canceling_entries = ('slash', 'question', 'shift')
def execute_insertion_buffer(insertion_buffer):
    if not insertion_buffer:
        return

    global modeless_engaged
    mode_entry = insertion_buffer[0][0] or Key('a')
    skip_escape = modeless_engaged
    if not modeless_engaged:
        mode_entry.execute()
        if mode_entry._spec in non_canceling_entries:
            skip_escape = True # Skip insertion mode exit

    for insertion in insertion_buffer:
        insertion[1].execute()

    if not skip_escape:
        Key('escape:2').execute()

# ****************************************************************************
# IDENTIFIERS
# ****************************************************************************


class InsertModeEntry(MappingRule):
    mapping = {
        #'inns': Key('i'),
        'squeeze': Key('i'),
        'syn': Key('a'),
        'phyllo': Key('o'),
        'phyhigh': Key('O'),
        'finder': Key('slash'),
        'refinder': Key('question'),
        'nicked': Key('shift'), # Placeholder for no-op, will not impact insertion
        }
ruleInsertModeEntry = RuleRef(InsertModeEntry(), name='InsertModeEntry')


def format_snakeword(text):
    formatted = text[0][0].upper()
    formatted += text[0][1:]
    formatted += ('_' if len(text) > 1 else '')
    formatted += format_score(text[1:])
    return formatted


def format_score(text):
    return '_'.join(text)


def format_camel(text):
    return text[0] + ''.join([word[0].upper() + word[1:] for word in text[1:]])


def format_proper(text):
    return ''.join(word.capitalize() for word in text)


def format_relpath(text):
    return '/'.join(text)


def format_abspath(text):
    return '/' + format_relpath(text)


def format_scoperesolve(text):
    return '::'.join(text)


def format_jumble(text):
    return ''.join(text)


def format_dotword(text):
    return '.'.join(text)


def format_dashword(text):
    return '-'.join(text)


def format_natword(text):
    return ' '.join(text)


def format_broodingnarrative(text):
    return ''


def format_sentence(text):
    return ' '.join([text[0].capitalize()] + text[1:])


class IdentifierInsertion(CompoundRule):
    spec = ('[upper | natural] ( proper | camel | rel-path | abs-path | score | sentence |'
            'scope-resolve | jumble | dotword | dashword | natword | snakeword | brooding-narrative) [<dictation>]')
    extras = [Dictation(name='dictation')]

    def value(self, node):
        words = node.words()

        uppercase = words[0] == 'upper'
        lowercase = words[0] != 'natural'

        if lowercase:
            words = [word.lower() for word in words]
        if uppercase:
            words = [word.upper() for word in words]

        words = [word.split('\\', 1)[0].replace('-', '') for word in words]
        if words[0].lower() in ('upper', 'natural'):
            del words[0]

        function = globals()['format_%s' % words[0].lower()]
        formatted = function(words[1:])

        return Text(formatted)
ruleIdentifierInsertion = RuleRef(
    IdentifierInsertion(),
    name='IdentifierInsertion'
    )


class LiteralIdentifierInsertion(CompoundRule):
    spec = '[<InsertModeEntry>] literal <IdentifierInsertion>'
    extras = [ruleIdentifierInsertion, ruleInsertModeEntry]

    def value(self, node):
        children = node.children[0].children[0].children
        return [('i', (children[0].value(), children[2].value()))]
ruleLiteralIdentifierInsertion = RuleRef(
    LiteralIdentifierInsertion(),
    name='LiteralIdentifierInsertion'
    )


# ****************************************************************************
# INSERTIONS
# ****************************************************************************

class KeyInsertion(MappingRule):
    mapping = {
        'ace [<count>]':        Key('space:%(count)d'),
        'tab [<count>]':        Key('tab:%(count)d'),
        'slap [<count>]':       Key('enter:%(count)d'),
        'chuck [<count>]':      Key('del:%(count)d'),
        'scratch [<count>]':    Key('backspace:%(count)d'),
        'ack':                  Key('escape'),
        }
    extras = [ruleDigitalInteger[3]]
    defaults = {'count': 1}
ruleKeyInsertion = RuleRef(KeyInsertion(), name='KeyInsertion')


class SpellingInsertion(MappingRule):
    mapping = dict(('dig ' + key, val) for (key, val) in aenea.misc.DIGITS.iteritems())
    mapping.update(aenea.misc.LETTERS)

    def value(self, node):
        return Text(MappingRule.value(self, node))
ruleSpellingInsertion = RuleRef(SpellingInsertion(), name='SpellingInsertion')


class ArithmeticInsertion(MappingRule):
    mapping = {
        'assign':           Text('= '),
        'compare eek':      Text('== '),
        'compare not eek':  Text('!= '),
        'compare greater':  Text('> '),
        'compare less':     Text('< '),
        'compare geck':     Text('>= '),
        'compare lack':     Text('<= '),
        'bit ore':          Text('| '),
        'bit and':          Text('& '),
        'bit ex or':        Text('^ '),
        'times':            Text('* '),
        'divided':          Text('/ '),
        'plus':             Text('+ '),
        'minus':            Text('- '),
        'plus equal':       Text('+= '),
        'minus equal':      Text('-= '),
        'times equal':      Text('*= '),
        'divided equal':    Text('/= '),
        'mod equal':        Text('%%= '),
        }
ruleArithmeticInsertion = RuleRef(
    ArithmeticInsertion(),
    name='ArithmeticInsertion'
    )


primitive_insertions = [
    ruleKeyInsertion,
    ruleIdentifierInsertion,
    DictListRef(
        'dynamic vim.insertions.code',
        aenea.vocabulary.register_dynamic_vocabulary('vim.insertions.code')
        ),
    DictListRef(
        'dynamic vim.insertions',
        aenea.vocabulary.register_dynamic_vocabulary('vim.insertions')
        ),
    ruleArithmeticInsertion,
    ruleSpellingInsertion,
    ]


static_code_insertions = aenea.vocabulary.get_static_vocabulary('vim.insertions.code')
static_insertions = aenea.vocabulary.get_static_vocabulary('vim.insertions')

if static_code_insertions:
    primitive_insertions.append(
        RuleRef(
            MappingRule(
                'static vim.insertions.code mapping',
                mapping=aenea.vocabulary.get_static_vocabulary('vim.insertions.code')
                ),
            'static vim.insertions.code'
            )
        )

if static_insertions:
    primitive_insertions.append(
        RuleRef(
            MappingRule(
                'static vim.insertions mapping',
                mapping=aenea.vocabulary.get_static_vocabulary('vim.insertions')
                ),
            'static vim.insertions'
            )
        )


class PrimitiveInsertion(CompoundRule):
    spec = '<insertion>'
    extras = [Alternative(primitive_insertions, name='insertion')]

    def value(self, node):
        children = node.children[0].children[0].children
        return children[0].value()
rulePrimitiveInsertion = RuleRef(
    PrimitiveInsertion(),
    name='PrimitiveInsertion'
    )


class PrimitiveInsertionRepetition(CompoundRule):
    spec = '<PrimitiveInsertion> [ parrot <count> ]'
    extras = [rulePrimitiveInsertion, ruleDigitalInteger[3]]

    def value(self, node):
        children = node.children[0].children[0].children
        holder = children[1].value()[1] if children[1].value() else 1
        value = children[0].value() * holder
        return value
rulePrimitiveInsertionRepetition = RuleRef(
    PrimitiveInsertionRepetition(),
    name='PrimitiveInsertionRepetition'
    )


class Insertion(CompoundRule):
    spec = '[<InsertModeEntry>] <PrimitiveInsertionRepetition>'
    extras = [rulePrimitiveInsertionRepetition, ruleInsertModeEntry]

    def value(self, node):
        children = node.children[0].children[0].children
        return [('i', (children[0].value(), children[1].value()))]
ruleInsertion = RuleRef(Insertion(), name='Insertion')


# ****************************************************************************
# MOTIONS
# ****************************************************************************


class PrimitiveMotion(MappingRule):
    mapping = {
        'up': Text('k'),
        'down': Text('j'),
        'left': Text('h'),
        'right': Text('l'),

        'lope': Text('b'),
        'yope': Text('w'),
        'elope': Text('ge'),
        'iyope': Text('e'),

        'lopert': Text('B'),
        'yopert': Text('W'),
        'elopert': Text('gE'),
        'eyopert': Text('E'),

        'apla': Text('{'),
        'anla': Text('}'),
        'sapla': Text('('),
        'sanla': Text(')'),

        'care': Text('^'),
        'hard care': Text('0'),
        'doll': Text('$'),

        'screecare': Text('g^'),
        'screedoll': Text('g$'),

        'scree up': Text('gk'),
        'scree down': Text('gj'),

        'wynac': Text('G'),

        'wynac top': Text('H'),
        'wynac toe': Text('L'),

        # CamelCaseMotion plugin
        'calalope': Text(',b'),
        'calayope': Text(',w'),
        'end calayope': Text(',e'),
        'inner calalope': Text('i,b'),
        'inner calayope': Text('i,w'),
        'inner end calayope': Text('i,e'),

        # EasyMotion
        'easy lope': Key('%s:2, b' % LEADER),
        'easy yope': Key('%s:2, w' % LEADER),
        'easy elope': Key('%s:2, g, e' % LEADER),
        'easy iyope': Key('%s:2, e' % LEADER),

        'easy lopert': Key('%s:2, B' % LEADER),
        'easy yopert': Key('%s:2, W' % LEADER),
        'easy elopert': Key('%s:2, g, E' % LEADER),
        'easy eyopert': Key('%s:2, E' % LEADER),
        }

    for (spoken_object, command_object) in (('(lope | yope)', 'w'),
                                            ('(lopert | yopert)', 'W')):
        for (spoken_modifier, command_modifier) in (('inner', 'i'),
                                                    ('outer', 'a')):
            map_action = Text(command_modifier + command_object)
            mapping['%s %s' % (spoken_modifier, spoken_object)] = map_action
rulePrimitiveMotion = RuleRef(PrimitiveMotion(), name='PrimitiveMotion')


class UncountedMotion(MappingRule):
    mapping = {
        'tect': Text('%%'),
        'matu': Text('M'),
        }
ruleUncountedMotion = RuleRef(UncountedMotion(), name='UncountedMotion')


class SearchMotion(MappingRule):
    mapping = {
            'next': Text('n'),
            'preeve': Text('N'),
            }
ruleSearchMotion = RuleRef(SearchMotion(), name='SearchMotion')


class MotionParameterMotion(MappingRule):
    mapping = {
        'phytic': 'f',
        'fitton': 'F',
        'pre phytic': 't',
        'pre fitton': 'T',
        'marker': '\'', # TODO: make this only work with letters
        }
ruleMotionParameterMotion = RuleRef(
    MotionParameterMotion(),
    name='MotionParameterMotion'
    )


class ParameterizedMotion(CompoundRule):
    spec = '<MotionParameterMotion> <AllCharacter>'
    extras = [ruleAllCharacterMapping, ruleMotionParameterMotion]

    def value(self, node):
        children = node.children[0].children[0].children
        return Text(children[0].value()) + Key(children[1].value())
ruleParameterizedMotion = RuleRef(
    ParameterizedMotion(),
    name='ParameterizedMotion'
    )


class CountedMotion(NumericDelegateRule):
    spec = '[<count>] <motion>'
    extras = [ruleDigitalInteger[3],
              Alternative([
                  rulePrimitiveMotion,
                  ruleParameterizedMotion,
                  ruleSearchMotion], name='motion')]
ruleCountedMotion = RuleRef(CountedMotion(), name='CountedMotion')


class Motion(CompoundRule):
    spec = '<motion>'
    extras = [Alternative(
        [ruleCountedMotion, ruleUncountedMotion],
        name='motion'
        )]

    def value(self, node):
        return node.children[0].children[0].children[0].value()

ruleMotion = RuleRef(Motion(), name='Motion')


# ****************************************************************************
# OPERATORS
# ****************************************************************************

_OPERATORS = {
    'relo': '',
    'dell': 'd',
    'chaos': 'c',
    'nab': 'y',
    'swap case': 'g~',
    'uppercase': 'gU',
    'lowercase': 'gu',
    'external filter': '!',
    'external format': '=',
    'format text': 'gq',
    'rotate thirteen': 'g?',
    'indent left': '<',
    'indent right': '>',
    'define fold': 'zf',
    }


class PrimitiveOperator(MappingRule):
    mapping = dict((key, Text(val)) for (key, val) in _OPERATORS.iteritems())
    # tComment
    mapping['comm nop'] = Text('gc')
rulePrimitiveOperator = RuleRef(PrimitiveOperator(), name='PrimitiveOperator')


class Operator(NumericDelegateRule):
    spec = '[<count>] <PrimitiveOperator>'
    extras = [ruleDigitalInteger[3],
              rulePrimitiveOperator]
ruleOperator = RuleRef(Operator(), name='Operator')


class OperatorApplicationMotion(CompoundRule):
    spec = '[<Operator>] <Motion>'
    extras = [ruleOperator, ruleMotion]

    def value(self, node):
        children = node.children[0].children[0].children
        return_value = children[1].value()
        if children[0].value() is not None:
            return_value = children[0].value() + return_value
        return return_value
ruleOperatorApplicationMotion = RuleRef(
    OperatorApplicationMotion(),
    name='OperatorApplicationMotion'
    )


class OperatorSelfApplication(MappingRule):
    mapping = dict(('%s [<count>] %s' % (key, key), Text('%s%%(count)d%s' % (value, value)))
                   for (key, value) in _OPERATORS.iteritems())
    # tComment
    # string not action intentional dirty hack.
    mapping['comm nop [<count>] comm nop'] = 'tcomment'
    extras = [ruleDigitalInteger[3]]
    defaults = {'count': 1}

    def value(self, node):
        value = MappingRule.value(self, node)
        if value == 'tcomment':
            # ugly hack to get around tComment's not allowing ranges with gcc.
            value = node.children[0].children[0].children[0].children[1].value()
            if value in (1, '1', None):
                return Text('gcc')
            else:
                return Text('gc%dj' % (int(value) - 1))
        else:
            return value

ruleOperatorSelfApplication = RuleRef(
    OperatorSelfApplication(),
    name='OperatorSelfApplication'
    )

ruleOperatorApplication = Alternative([ruleOperatorApplicationMotion,
                                       ruleOperatorSelfApplication],
                                      name='OperatorApplication')


# ****************************************************************************
# COMMANDS
# ****************************************************************************


class PrimitiveCommand(MappingRule):
    mapping = {
        'vim scratch': Key('X'),
        'vim chuck': Key('x'),
        '(vim undo | oops)': Key('u'),
        'vim redo': Key('c-r'),
        'plap': Key('P'),
        'plop': Key('p'),
        'ditto': Text('.'),
        'ripple': 'macro',
        'trite': Key('g,t'), # Move forward a tab or go to specified tab
        '(track | trek)': Key('g,T'), # Move backward the specified number of tabs
        }
rulePrimitiveCommand = RuleRef(PrimitiveCommand(), name='PrimitiveCommand')


class Command(CompoundRule):
    spec = '[<count>] [reg <LetterMapping>] <command>'
    extras = [Alternative([ruleOperatorApplication,
                           rulePrimitiveCommand,
                           ], name='command'),
              ruleDigitalInteger[3],
              ruleLetterMapping]

    def value(self, node):
        delegates = node.children[0].children[0].children
        value = delegates[-1].value()
        prefix = ''
        if delegates[0].value() is not None:
            prefix += str(delegates[0].value())
        if delegates[1].value() is not None:
            # Hack for macros
            reg = delegates[1].value()[1]
            if value == 'macro':
                prefix += '@' + reg
                value = None
            else:
                prefix += "'" + reg
        if prefix:
            if value is not None:
                value = Text(prefix) + value
            else:
                value = Text(prefix)
        # TODO: ugly hack; should fix the grammar or generalize.
        if 'chaos' in zip(*node.results)[0]:
            return [('c', value), ('i', (NoAction(),) * 2)]
        else:
            return [('c', value)]
ruleCommand = RuleRef(Command(), name='Command')


# ****************************************************************************
# SESSION
# ****************************************************************************

class BufferCommand(MappingRule):
    mapping = {
            'save': Key('colon, w, enter'),
            'save as': Key('colon, w, space'),
            'really save': Key('colon, w, exclamation, enter'),
            'save all': Key('colon, w, a, enter'),
            'quit': Key('colon, q, enter'),
            'really quit': Key('colon, q, exclamation, enter'),
            'quit all': Key('colon, q, a, enter'),
            'suspend': Key('colon, s, u, s, enter'),
            'buff next': Key('colon, b, n, enter'),
            'buff back': Key('colon, b, p, enter'),
            'buff list': Key('colon, l, s, enter'),
            'buff <count>': Key('colon') + Text('b %(count)d\n'),
            'buff close': Key('colon') + Text('Bclose\n'),
            }
    extras = [ruleDigitalInteger[3]]

class SplitCommand(MappingRule):
    mapping = {
            # Vertical or horizontal split
            'hotdog': Key('colon, v, s, enter'),
            'hamburger': Key('colon, s, p, enter'),
            # Go to split right, left, up, down when proper key bindings are set in vimrc
            'sprite': Key('c-l'),
            'splat': Key('c-h'),
            'slup': Key('c-k'),
            'sloan': Key('c-j'),
            }

class SearchCommand(MappingRule):
    mapping = {
            'search this': Key('asterisk'),
            'search this up': Key('hash'),
            }
    extras = [ruleIdentifierInsertion]

class MarkCommand(MappingRule):
    mapping = {
            'bookmark <LetterMapping>': Key('m') + Text('%(LetterMapping)s'),
            }
    extras = [ruleLetterMapping]

# Use this to disable/enable automatic insertion mode entry.
# Useful for using any vim functionality not covered by this grammar,
# i.e. CtrlP, Fugitive, etc without always having to specify the 'nicked' entry
class ModelessCommand(MappingRule):
    mapping = {
            'no mode': Function(toggle_modeless),
            }

class NERDTreeCommand(MappingRule):
    mapping = {
            'nerdy': Text(':NERDTreeToggle\n'),
            }

class ScrollCommand(MappingRule):
    mapping = {
            'gope [<count>]': Key('c-u:%(count)d'),
            'drop [<count>]': Key('c-d:%(count)d'),
            }
    extras = [ruleDigitalInteger[3]]
    defaults = {'count': 1}

# ****************************************************************************


class VimCommand(CompoundRule):
    spec = ('([<app>] [<literal>] | [<session>])')
    extras = [
            Repetition(Alternative([ruleCommand, RuleRef(Insertion())]), max=10, name='app'),
            RuleRef(LiteralIdentifierInsertion(), name='literal'),
            Alternative([
                  RuleRef(BufferCommand()),
                  RuleRef(SplitCommand()),
                  RuleRef(SearchCommand()),
                  RuleRef(MarkCommand()),
                  RuleRef(ModelessCommand()),
                  RuleRef(NERDTreeCommand()),
                  RuleRef(ScrollCommand()),
                ], name='session')
              ]

    def _process_recognition(self, node, extras):
        insertion_buffer = []
        commands = []
        if 'session' in extras:
            extras['session'].execute()
            return
        if 'app' in extras:
            for chunk in extras['app']:
                commands.extend(chunk)
        if 'literal' in extras:
            commands.extend(extras['literal'])
        for command in commands:
            mode, command = command
            if mode == 'i':
                insertion_buffer.append(command)
            else:
                execute_insertion_buffer(insertion_buffer)
                insertion_buffer = []
                command.execute(extras)
        execute_insertion_buffer(insertion_buffer)

grammar.add_rule(VimCommand())

grammar.load()
print "Grammar loaded (vim)"

def unload():
    aenea.vocabulary.uninhibit_global_dynamic_vocabulary('vim', VIM_TAGS)
    for tag in VIM_TAGS:
        aenea.vocabulary.unregister_dynamic_vocabulary(tag)
    global grammar
    if grammar:
        grammar.unload()
    grammar = None
