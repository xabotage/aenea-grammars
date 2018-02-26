import aenea
import aenea.wrappers
from aenea.proxy_contexts import (
		ProxyAppContext,
		ProxyCustomAppContext,
		)
from dragonfly import AppContext

vim_context = aenea.wrappers.AeneaContext(
		ProxyAppContext(match='regex', title='.*VIM.*', case_sensitive=True),
		AppContext(title='VIM')
		)

atom_context = aenea.wrappers.AeneaContext(
		ProxyAppContext(match='regex', title='.*Atom$', case_sensitive=True),
		AppContext(title='Atom')
		)

terminal_context = aenea.ProxyCustomAppContext(executable="gnome-terminal")

tmux_context = aenea.ProxyAppContext(match='regex', title='.*\d+:\d+\.\d+.*')
