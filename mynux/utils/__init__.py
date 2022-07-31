from importlib.metadata import entry_points
from argparse import ArgumentParser


def get_mynux_arg_parser(prog: str) -> ArgumentParser:
    return ArgumentParser(prog=f'mynux {prog}')
    

def ask_to_confirm(msg, default=True):
    """ask user boolean question"""
    if default:
        result = input(msg + '[Y/n] ') or 'y'
    else:
        result = input(msg + '[y/N] ') or 'n'
    return result.lower() in ['y', 'yes']


def iter_cmds():
    for entry_point in entry_points()['mynux.cmd']:
        yield entry_point.name, entry_point


