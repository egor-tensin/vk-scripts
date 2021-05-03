vk-mutuals
==========

Learn who your ex and her new boyfriend are both friends with.

Usage
-----

    > vk-mutuals -h
    usage: vk-mutuals [-h] [-f {csv,json}] [-o PATH] UID [UID ...]
    ...

For example (using made up user IDs/"screen names"),

    > vk-mutuals john.doe jane.doe
    89497105,John,Smith
    3698577,Jane,Smith

In the example above, both "John Doe" and "Jane Doe" are friends with "John
Smith" and "Jane Smith", whose user IDs are 89497105 and 3698577 respectively.

The output format is CSV (comma-separated values) by default.
You can also get a JSON document:

    > vk-mutuals --format json john.doe jane.doe
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
