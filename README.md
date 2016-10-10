VK scripts
==========

A collection of scripts abusing VK.com API.

Prerequisites
-------------

Python 3.4 or higher is required.
Additionally, [online_sessions.py] uses the excellent [matplotlib] plotting
library.
The versions below have been verified to work properly.

Software     | Version
------------ | -------
Python       | 3.5.1
[matplotlib] | 1.5.1

[matplotlib]: http://matplotlib.org/

Usage
-----

The main package resides in the "vk/" directory.

Also, a few scripts are supplied in the "bin/" directory to showcase the
package's capabilities.
Run the scripts from the top-level directory using `python -m`.
Pass the `--help` flag to a script to see its detailed usage information.
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

Requires [PyLint].

    > cd
    D:\workspace\personal\vk-scripts

    > pylint vk
    ...

    > set PYTHONPATH=%CD%

    > pylint bin\mutual_friends.py
    ...

    > pylint bin\online_sessions.py
    ...

    > pylint bin\track_status.py
    ...

[PyLint]: https://www.pylint.org/

License
-------

Distributed under the MIT License.
See [LICENSE.txt] for details.

[LICENSE.txt]: LICENSE.txt
