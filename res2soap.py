#!/usr/bin/env python2

from ase.io import read
import quippy
from tqdm import tqdm
import numpy as np
import glob
import sys
import os
from multiprocessing import Pool
from subprocess import check_output

try:
    WORKDIR = sys.argv[1]
except KeyError:
    WORKDIR = './'

desc = quippy.descriptors.Descriptor(
    "soap cutoff=5 l_max=15 n_max=15 atom_sigma=0.1 average=T n_species=1 species_Z=13 Z=13"
)


def get_soap_desc(args):
    """Function returns the descript """
    n, atoms = args
    if not isinstance(atoms, quippy.Atoms):
        atoms = quippy.Atoms(atoms)
    atoms.set_cutoff(10)
    atoms.calc_connect()
    return n, desc.calc(atoms)['descriptor']


def save_file(savename, desc_arrays, info):
    size = desc_arrays[0].size
    with open(savename, 'w') as fh:
        fh.write('{} {}\n'.format(len(desc_arrays), size))
        for desc in desc_arrays:
            fh.write(' '.join(map(str, desc[0])) + '\n')
        for line in info:
            fh.write(line + '\n')


if __name__ == '__main__':

    # compute the descriptors in the same order as the cryan output
    output = check_output(['ca', '-v'], cwd=WORKDIR).split(
        '\n')  # Run ca -v in shell and get outputs
    num_struct, _ = output[0].split()
    lines = output[int(num_struct) + 1:-1]
    fnames = [os.path.join(WORKDIR, l.split('\t')[0] + '.res') for l in lines]
    pool = Pool(4)
    print('Reading res files')
    atom_list = [[n, read(fn)] for n, fn in enumerate(tqdm(fnames))]
    print('Computing descriptors')
    par_res = list(pool.imap_unordered(get_soap_desc, tqdm(atom_list)))
    par_res.sort(key=lambda x: x[0])
    _, descs = zip(*par_res)

    # descs = [get_soap_desc(atoms) for atoms in tqdm(atom_list)]
    print('Saving results')
    save_file('soap_desc.xyz', descs, lines)
