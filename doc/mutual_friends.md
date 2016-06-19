mutual_friends.py
=================

Learn who your ex and her new boyfriend are both friends with.

Usage
-----

Run from the top-level directory using `python -m`.
For example:

    > python -m bin.mutual_friends -h
    usage: mutual_friends.py [-h] [--output-format {csv,json}] UID [UID ...]
    ...

For example (using made up user IDs/"screen names"),

    > python -m bin.mutual_friends john.doe jane.doe
    89497105,John,Smith,john.smith
    3698577,Jane,Smith,jane.smith

In the example above, both "John Doe" and "Jane Doe" are friends with "John
Smith" and "Jane Smith", whose user IDs are 89497105 and 3698577 respectively.
Their "screen names" (the part after "vk.com/" of their personal page URLs) are
"john.smith" and "jane.smith".

The output format is CSV (comma-separated values) by default.
You can also get a JSON document:

    > python -m bin.mutual_friends --output-format json john.doe jane.doe
    [
       {
          "uid": 89497105,
          "first_name": "John",
          "last_name": "Smith",
          "screen_name": "john.smith"
       },
       {
          "uid": 3698577,
          "first_name": "Jane",
          "last_name": "Smith",
          "screen_name": "jane.smith"
       }
    ]

See also
--------

* [License]

[License]: ../README.md#license
