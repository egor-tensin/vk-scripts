VK scripts
==========

[![Test](https://github.com/egor-tensin/vk-scripts/actions/workflows/test.yml/badge.svg)](https://github.com/egor-tensin/vk-scripts/actions/workflows/test.yml)

A collection of scripts abusing VK.com API.

Prerequisites
-------------

* Python 3.4 or higher
* [matplotlib] (required by [online_sessions.py])
* [numpy] (required by [matplotlib])

The versions below have been verified to work properly.

| Software   | Version
| ---------- | -------
| CPython    | 3.5.1
| numpy      | 1.11.0
| matplotlib | 1.5.1

Windows binaries for CPython can be acquired at
http://www.lfd.uci.edu/~gohlke/pythonlibs/.

[matplotlib]: http://matplotlib.org/
[numpy]: http://www.numpy.org/

Usage
-----

The main package resides in the "vk/" directory.

Also, a few scripts are supplied in the "bin/" directory to showcase the
package's capabilities.
Run the scripts from the top-level directory using `python -m`.
Pass the `--help` flag to a script to examine its detailed usage information.
The supplied scripts are listed below.

* [mutual_friends.py] &mdash; Learn who your ex and her new boyfriend are both
friends with.
* [track_status.py] &mdash; Track when people go online/offline.
* [online_sessions.py] &mdash; View/visualize the amount of time people spend
online.

[mutual_friends.py]: docs/mutual_friends.md
[track_status.py]: docs/track_status.md
[online_sessions.py]: docs/online_sessions.md

Development
-----------

### Linting

Requires [Pylint].
To lint everything, run from the top-level directory:

    > pylint vk
    ...

    > pylint bin
    ...

[Pylint]: https://www.pylint.org/

License
-------

Distributed under the MIT License.
See [LICENSE.txt] for details.

[LICENSE.txt]: LICENSE.txt
