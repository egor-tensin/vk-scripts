# VK tools

A collection of scripts abusing VK.com API.

## Usage

To use this software, you need to be able to run Python 3 scripts (3.4 or higher
is required).

### track_status.py

Track when people go online/offline.

    usage: track_status.py [-h] [-t TIMEOUT] [-l LOG] UID [UID ...]

For example,

    > track_status.py egor.tensin id1

### mutual_friends.py

Learn who your ex and her new boyfriend are both friends with.

    usage: mutual_friends.py [-h] UID [UID ...]

For example,

    > mutual_friends.py egor.tensin durov

## Licensing

This project, including all of the files and their contents, is licensed under
the terms of the MIT License.
See LICENSE.txt for details.
