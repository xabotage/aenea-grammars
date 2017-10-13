import aenea
from aenea import (
    Grammar,
    MappingRule,
    Text,
    Key,
    Alternative,
    RuleRef,
    Repetition,
    Sequence,
    Literal,
    CompoundRule,
    AppContext,
)

import lib.contexts as ctx

def WrapInRepeatRule(rule, name):
    return Repetition(RuleRef(rule=rule), min=1, max=10, name=name)

def recurse_values(node, types):
    value = ''
    for child in node.children:
        if child.actor.__class__ in types:
            value += child.value()
        value += recurse_values(child, types)
    return value


class HgCommitOptionRule(MappingRule):
    exported = False
    mapping = aenea.configuration.make_grammar_commands('hg_commit_options', {
        'add remove': '--addremove ',
        'close branch': '--close-branch ',
        'reuse message': '--reuse-message ',
        'interactive': '--interactive ',
        'fix up': '--fixup ',
        'user': '--user ',
        'date': '--date ',
        'message': '--message ',
        'edit': '--edit ',
        'amend': '--amend ',
        'include': '--include ',
        # Add as needed
    })
commit_options = WrapInRepeatRule(HgCommitOptionRule(), 'commit_options')


class HgCommitRule(CompoundRule):
    exported = False
    spec = 'commit [<commit_options>]'
    extras = [commit_options]

    def value(self, node):
        return 'commit ' + recurse_values(node, [HgCommitOptionRule])
commit_rule = RuleRef(name='commit_rule', rule=HgCommitRule())


class HgStatusRuleOption(MappingRule):
    exported = False
    mapping = aenea.configuration.make_grammar_commands('hg_status_options', {
        "all": "--all",
        # Add as needed
    })
status_options = WrapInRepeatRule(HgStatusRuleOption(), 'status_options')


class HgStatusRule(CompoundRule):
    exported = False
    spec = "status [<status_options>]"
    extras = [status_options]

    def value(self, node):
        return "status " + recurse_values(node, [HgStatusRuleOption])
status_rule = RuleRef(name="status_rule", rule=HgStatusRule())


class HgPullOption(MappingRule):
    exported = False
    mapping = aenea.configuration.make_grammar_commands(
        "hg_pull_options", {
            "update": "--update ",
            "bookmark": "--bookmark ",
            "rebase": "--rebase ",
            "force": "--force ",
            # Add as needed
        }
    )
pull_options = WrapInRepeatRule(HgPullOption(), 'pull_options')


# Quick stubs for rules that I haven't bothered to create additional options for yet.
# Wrapped in Sequence class so that the nesting works out in the top level rule evaluation
remove_rule = Sequence([Literal("remove", value="remove ")], name="remove_rule")
diff_rule = Sequence([Literal("diff", value="diff ")], name="diff_rule")
shelve_rule = Sequence([Literal("shelf", value="shelve ")], name="shelve_rule")
unshelve_rule = Sequence([Literal("unshelf", value="unshelve ")], name="unshelve_rule")


class HgPullRule(CompoundRule):
    exported = False
    spec = "pull [<pull_options>]"
    extras = [pull_options]

    def value(self, node):
        return "pull " + recurse_values(node, [HgPullOption])
pull_rule = RuleRef(name="pull_rule", rule=HgPullRule())

hg_commands = [
    #add_rule,
    commit_rule,
    #checkout_rule,
    #push_rule,
    status_rule,
    #log_rule,
    #branch_rule,
    pull_rule,
    remove_rule,
    diff_rule,
    shelve_rule,
    unshelve_rule,
]

class HgHelpRule(CompoundRule):
    exported = False
    spec = "help [<command>]"
    extras = [Alternative(name='command', children=hg_commands)]

    def value(self, node):
        val = ''
        try:
            val = node.children[0].children[0].children[1].children[0].children[0].value()
        except:
            pass
        return "help " + val

hg_commands.append(RuleRef(name="help_rule", rule=HgHelpRule()))


class MercurialRule(CompoundRule):
    spec = 'merck <command>'
    extras = [Alternative(name='command', children=hg_commands)]

    def process_recognition(self, node):
        self.value(node).execute()

    def value(self, node):
        cmd = node.children[0].children[0].children[1].children[0].children[0]
        value = Text('hg ' + cmd.value())
        return value

grammar = Grammar('mercurial', context=(ctx.terminal_context & ~ctx.vim_context))
grammar.add_rule(MercurialRule())
grammar.load()

def unload():
    global grammar
    if grammar:
        grammar.unload()
    grammar = None
