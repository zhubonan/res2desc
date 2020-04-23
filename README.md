# res2desc

Compute descriptors for AIRSS style SHELX files

## Usage

Invoke by `cat *.res | res2desc soap`.

You can get a list of options by passing `--help` flag.

```text
Usage: res2desc [OPTIONS] COMMAND [ARGS]...

  Commandline tool for converting SHELX files to descriptors

Options:
  --input-source FILENAME
  --output FILENAME
  --cryan / --no-cryan
  --cryan-args TEXT        A string of the arges that should be passed to
                           cryan, as if in the shell

  --help                   Show this message and exit.

Commands:
  soap  Compute SOAP descriptors
```

### SOAP descriptors

Again, help can be obtained using the `echo '' | res2desc soap --help` flag.
Note that by default, `res2desc` take input from STDIN, so you have to use `echo`
to obtain the help string (subject to change in the future).

```text
Usage: res2desc soap [OPTIONS]

  Compute SOAP descriptors

Options:
  -np, --nprocs INTEGER         Number of processes for parallelisation.
  --l-max INTEGER
  --n-max INTEGER
  --cutoff INTEGER
  --atom-sigma FLOAT
  --crossover / --no-crossover  Whether do the crossover for multiple species
  -sn, --species-names TEXT     Symbols of all species to be considered,
                                should be a list

  -cn, --centres-name TEXT      Centres where the descriptor should be
                                computed. If not specified, defaults to all
                                atomic sites

  --average / --no-average      Averaging descriptors for each structrure,
                                rather than output those for individual sites.

  --periodic / --no-periodic    Whether assuming periodic boundary conditions
                                or not

  --help                        Show this message and exit.
```

## Requirement

* `DScribe` for computing descriptors
* `click` for commandline interface

## Testing

```text
git clone git@github.com:zhubonan/res2desc.git
pytest ./res2desc
```

## Limitations

* Not able to output to STDOUT at the moment
* Fast reader may be used for the `res` files to create `quippy.Atoms` objects directly.

## TODO

* Add support of  DScribe library
* Allow computing more types of descriptors other than SOAP
