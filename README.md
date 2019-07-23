res2soap
--------

Tool to compute SOAP descriptors for a folder of `res` files.

Usage
-----

Invoke by `python res2soap.py <FOLDER_NAME> OPTION`. At the moment you must pass the 
atomic number of the centre atoms (`-z`) and the environment atoms (`-sz`). Note that
each option can be specified multiple times.

You can get a list of options by passing `--help` flag.


Requirement
------------

Installation of `airss` and `quippy` packages.


Limitations
-----------

* Not able to output to STDOUT at the moment
* Fast reader may be used for the `res` files to create `quippy.Atoms` objects directly.


