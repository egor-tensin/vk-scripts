mutual_friends.py
=================

Learn who your ex and her new boyfriend are both friends with.

Usage
-----

Run from the top-level directory using `python -m`:

    > python -m bin.mutual_friends -h
    usage: mutual_friends.py [-h] [--output-format {csv,json}] [-o PATH]
                             UID [UID ...]
    ...

For example (using made up user IDs/"screen names"),

    > python -m bin.mutual_friends john.doe jane.doe
    89497105,John,Smith
    3698577,Jane,Smith

In the example above, both "John Doe" and "Jane Doe" are friends with "John
Smith" and "Jane Smith", whose user IDs are 89497105 and 3698577 respectively.

The output format is CSV (comma-separated values) by default.
You can also get a JSON document:

    > python -m bin.mutual_friends --output-format json john.doe jane.doe
    [
       {
          "uid": 89497105,
          "first_name": "John",
          "last_name": "Smith"
       },
       {
          "uid": 3698577,
          "first_name": "Jane",
          "last_name": "Smith"
       }
    ]

See also
--------

* [License]

[License]: ../README.md#license
