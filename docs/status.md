vk-status
=========

Track when people go online/offline.

Usage
-----

    > vk-status -h
    usage: vk-status [-h] [-t SECONDS] [-O] [-l PATH] [-f {csv,log,null}]
                     [-o PATH]
                     UID [UID ...]
    ...

For example (using made up user IDs/"screen names"),

    > vk-status john.doe jane.smith
    [2016-06-18 01:43:34] John Doe is ONLINE.
    [2016-06-18 01:43:34] John Doe was last seen at 2016-06-18 01:33:58+03:00 using the official iPhone app.
    [2016-06-18 01:43:34] Jane Smith is OFFLINE.
    [2016-06-18 01:43:34] Jane Smith was last seen at 2016-06-18 01:15:47+03:00 using the web version (or an unrecognized app).
    [2016-06-18 01:59:09] Jane Smith went ONLINE.
    [2016-06-18 01:59:09] Jane Smith was last seen at 2016-06-18 01:59:07+03:00 using the official Android app.
    [2016-06-18 02:10:00] John Doe went OFFLINE.
    [2016-06-18 02:10:00] John Doe was last seen at 2016-06-18 01:54:58+03:00 using the official iPhone app.
    ...

By default, the script produces a human-readable log.
Use the `--log` parameter to write the log to a file.
If you want to record when people go online/offline for further analysis using
[vk-sessions], specify the path to a database using the `--output` parameter.

[vk-sessions]: sessions.md

See also
--------

* [License]

[License]: ../README.md#license
