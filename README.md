res2soap
--------

Tool to compute SOAP descriptors for a folder of `res` files.

Usage
-----

Invoke by `python res2soap.py <FOLDER_NAME> OPTION`. At the moment you must pass the 
atomic number of the centre atoms (`-z`) and the environment atoms (`-sz`). Note that
each option can be specified multiple times.

You can get a list of options by passing `--help` flag.

```text
Usage: res2soap.py [OPTIONS] WORKDIR

  Compute descriptors of the results uisng the quippy package and output in
  a cryan format (e.g the same as ca -v)

Options:
  -np, --nprocs INTEGER     Number of processes for parallelisation.
  -s, --save-name TEXT      Save file name
  --l-max INTEGER
  --n-max INTEGER
  --cutoff INTEGER
  --desc-kind TEXT
  --atom-sigma FLOAT
  -z, --centre-z INTEGER    Atomic numbers of the atoms that the local
                            descriptor should be computed  [required]
  -sz, --species-z INTEGER  Atomic numbers of the enironment atoms that should
                            be inlcuded  [required]
  --help                    Show this message and exit.
```


Requirement
------------

Installation of `airss` and `quippy` packages.


Testing
-------

Type `pytest`!

Limitations
-----------

* Not able to output to STDOUT at the moment
* Fast reader may be used for the `res` files to create `quippy.Atoms` objects directly.


