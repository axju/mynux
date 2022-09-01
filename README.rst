mynux - My Linux
================
!!!Work in progress!!!

Just a dotfile manager with some extras.

Install
-------
???

Quickstart
----------
If you only want to install a single dotfile directory to your home directory,
you can run::

    mynux install path/to/directory/or/git/url

Any repo will be clone into "~/.config/mynux/repos/". After the files will
be linked or copy to your home directory. With the mynux.toml file you can also
install package.

Multi storage setup
-------------------
Add a repo or directory to the local config directory::

    mynux add git@github.com/axju/dotfiles.git
    mynux add /path/to/dir
    mynux add --name my-dotfile git@github.com/axju/dotfiles.git

The command::

    mynux install

will install all mynux storage from the mynux config directory. To change the order
you can uses the argument "--sort=name1,name2..." or change the config file
"~./config/mynux/config.toml".

poetry
------
This is the first project I uses poetry. Some nodes::

    poetry run mynux
