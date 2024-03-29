VK scripts
==========

[![CI](https://github.com/egor-tensin/vk-scripts/actions/workflows/ci.yml/badge.svg)](https://github.com/egor-tensin/vk-scripts/actions/workflows/ci.yml)

Scripts to stalk people on VK.

Installation
------------

    pip install vk-scripts


Python 3.4 or higher is required.
`vk-sessions` uses [matplotlib].

[matplotlib]: http://matplotlib.org/

Usage
-----

* [vk-mutuals] &mdash; Learn who your ex and her new boyfriend are both friends
with.
* [vk-status] &mdash; Track when people go online/offline.
* [vk-sessions] &mdash; View/visualize the amount of time people spend online.

[vk-mutuals]: docs/mutuals.md
[vk-status]: docs/status.md
[vk-sessions]: docs/sessions.md

Development
-----------

### Linting

Requires [Pylint].

    pylint vk

[Pylint]: https://www.pylint.org/

### Releases

Make a git tag:

    git tag "v$( python -m setuptools_scm --strip-dev )"

You can then review that the tag is fine and push w/ `git push --tags`.

License
-------

Distributed under the MIT License.
See [LICENSE.txt] for details.

[LICENSE.txt]: LICENSE.txt
