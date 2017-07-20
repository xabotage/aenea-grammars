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
    AppContext,
)

class LayoutCommand(MappingRule):
	mapping = {
			'left': Key('cw-left'),
			'right': Key('cw-right'),
			'max': Key('cw-up'),
			'min': Key('cw-down'),
			}

class SwitchCommand(MappingRule):
	mapping = {
			'switch [<n>]': Key('alt:down, tab:%(n)d/15, alt:up'),
			'swap [<n>]': Key('alt:down, backtick:%(n)d/15, alt:up'),
			}
	extras = [
        IntegerRef('n', 1, 9),
	]
	defaults = {
			'n': 1,
			}

class DashCommand(MappingRule):
	mapping = {
			'alt [<text>]': Key('alt') + Text('%(text)s'),
			'launch': Key('win'),
			'launch app <n>': Key('w-%(n)d/15'),
			}
	extras = [
        IntegerRef('n', 0, 9),
        Dictation('text'),
	]
	defaults = {
			'n': 1,
			'text': ''
			}

class WorkspaceCommand(CompoundRule):
	spec = 'work <dir>'
	extras = [Choice('dir', {
		'up': 'up',
		'down': 'down',
		'left': 'left',
		'right': 'right',
		})]

	def value(self, node):
		direction = node.children[0].children[0].children[1].value()
		return Key('ca-%s' % direction)

class UnityCommand(CompoundRule):
	spec = ('yoonie <desktop>')
	extras = [Alternative([
		RuleRef(LayoutCommand()),
		RuleRef(SwitchCommand()),
		RuleRef(DashCommand()),
		RuleRef(WorkspaceCommand()),
		], name='desktop')
	]

	def _process_recognition(self, node, extras):
		print ''
		if extras['desktop'] is not None:
			extras['desktop'].execute()


grammar = Grammar('UnityDesktop')
grammar.add_rule(UnityCommand())
grammar.load()

def unload():
	global grammar
	if grammar:
		grammar.unload()
	grammar = None
