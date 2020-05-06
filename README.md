# res2desc

Compute descriptors for AIRSS style SHELX files

## Installation

```text
git clone git@github.com:zhubonan/res2desc.git
pip install -e ./res2desc
```

## Usage

Invoke by `cat *.res | res2desc soap`.

You can get a list of options by passing `--help` flag.

```text
Usage: res2desc [OPTIONS] COMMAND [ARGS]...

  Commandline tool for converting SHELX files to descriptors

Options:
  -in, --input_source FILENAME  [default: -]
  -out, --output FILENAME       [default: (STDOUT)]
  --cryan / --no-cryan          Call cryan internally to obtain fully
                                compatible output. Should be disabled if cryan
                                is not avaliable.  [default: True]

  --cryan-style [1|2]           Style of the cryan output, 1 for 3 lines for
                                structure, 2 for 2 lines per structure.
                                Automatically fallback to 1 if 2 does not
                                work.  [default: 2]

  --cryan-args TEXT             A string of the arges that should be passed to
                                cryan, as if in the shell  [default: -v -dr 0]

  --help                        Show this message and exit.

Commands:
  soap  Compute SOAP descriptors
  xyz   Create concatenated xyz files

```

Note that `input-source` and `output` default to STDIN and STDOUT by default, but you can still
specify file names.

### SOAP descriptors

Again, help can be obtained using the `echo '' | res2desc soap --help` flag.
Note that by default, `res2desc` take input from STDIN, so you have to use `echo`
to obtain the help string (subject to change in the future).

```text
Usage: res2desc soap [OPTIONS]

  Compute SOAP descriptors

Options:
  -np, --nprocs INTEGER         Number of processes for parallelisation.
  --l-max INTEGER               [default: 4]
  --n-max INTEGER               [default: 8]
  --cutoff INTEGER              [default: 5]
  --atom-sigma FLOAT            [default: 0.1]
  --crossover / --no-crossover  Whether do the crossover for multiple species
                                [default: True]

  -sn, --species-names TEXT     Symbols of all species to be considered,
                                should be a list

  -cn, --centres-name TEXT      Centres where the descriptor should be
                                computed. If not specified, defaults to all
                                atomic sites. NOT IMPLEMENTED FOR NOW

  --average / --no-average      Averaging descriptors for each structrure,
                                rather than output those for individual sites.
                                [default: True]

  --periodic / --no-periodic    Whether assuming periodic boundary conditions
                                or not  [default: True]

  --help                        Show this message and exit.
```

### xyz output

Concatenate all structures in the xyz format, and write the labels in separate files.
This can be used when using [ASAP](https://github.com/BingqingCheng/ASAP) for analysing AIRSS search results.

```text
Usage: res2desc xyz [OPTIONS]

  Create concatenated xyz files

Options:
  --label-file TEXT               Filename for writing out the labels
  --label-style [label|short_label|short_symm|symm|enthalpy|volume|spin|spin_abs|pressure]
                                  Style of the labels
  --help                          Show this message and exit.

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

* Only SOAP is implemented at the moment
* Filtering species is not avaliable for now
* Descripters are only computed once all files are read, this could cause problems for large number of input structures

## TODO

* Allow computing more types of descriptors other than SOAP
* Allow buffering input structures and avoid stressing the memory
