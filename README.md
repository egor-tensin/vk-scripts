# VK scripts

A collection of scripts abusing VK.com API.

## Prerequisites

* Python (3.4 or higher)

## Usage

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

## License

This project, including all of the files and their contents, is licensed under
the terms of the MIT License.
See [LICENSE.txt] for details.

[LICENSE.txt]: LICENSE.txt
