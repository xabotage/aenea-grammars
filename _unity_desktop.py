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
	exported = False
	mapping = {
			'left': Key('cw-left'),
			'right': Key('cw-right'),
			'max': Key('cw-up'),
			'min': Key('cw-down'),
			}

class SwitchCommand(MappingRule):
	exported = False
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
	exported = False
	mapping = {
			'alt [<text>]': Key('alt') + Text('%(text)s'),
			'launch': Key('win'),
			# Press and release shift as workaround for xdotool bug.
			'app <n>': Key('win:down, shift:down, shift:up, %(n)d, win:up'),
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
	exported = False
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

class WindowWorkspaceCommand(CompoundRule):
	exported = False
	spec = 'bring <dir>'
	extras = [Choice('dir', {
		'up': 'up',
		'down': 'down',
		'left': 'left',
		'right': 'right',
		})]

	def value(self, node):
		direction = node.children[0].children[0].children[1].value()
		return Key('csa-%s' % direction)

class PutCommand(MappingRule):
	exported = False
        mapping = { 'put window': Key('caw-right'), }

class UnityCommand(CompoundRule):
	spec = ('yoonie <desktop>')
	extras = [Alternative([
		RuleRef(LayoutCommand()),
		RuleRef(SwitchCommand()),
		RuleRef(DashCommand()),
		RuleRef(WorkspaceCommand()),
		RuleRef(WindowWorkspaceCommand()),
		RuleRef(PutCommand()),
		], name='desktop')
	]

	def _process_recognition(self, node, extras):
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
