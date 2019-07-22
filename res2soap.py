#!/usr/bin/env python2

from multiprocessing import Pool
import quippy
import click


class Atoms2Soap(object):
    """
    Class for converting atoms to soap.
    Works with multiprocessing
    """

    def __init__(self, desc_dict):
        """
        Initialise the object
        """
        self.desc_settings = desc_dict
        self._desc = True

    @property
    def desc_string(self):
        settings = []
        for key, value in self.desc_settings.items():
            settings.append('{}={}'.format(key, value))
        return 'soap ' + ' '.join(settings)

    def init_desc(self):
        """Initialize the descriptor object"""
        # Set the module level parameter for parallelisation
        # It seems that we cannot pass the descriptor to the subprocess
        # Hence for any subprocess the descriptor object needs to be
        # reconstructed
        self._desc = quippy.descriptors.Descriptor(self.desc_string)

    @property
    def desc(self):
        if self._desc is None:
            self.init_desc()
        return self._desc

    def get_desc_wrap(self, args):
        """
        Wrapper to get_desc with single argument.
        Usefully for parallel processing
        """
        n, atoms = args
        return n, self.get_soap_desc(atoms)

    def get_desc(self, atoms):
        """
        Return the soap descriptor vectors for an Atoms
        """

        if not isinstance(atoms, quippy.Atoms):
            atoms = quippy.Atoms(atoms)
        cut_off = int(self.desc_settings['cutoff']) + 1
        atoms.set_cutoff(cut_off)
        atoms.calc_connect()
        return self.desc.calc(atoms)['descriptor']


def save_file(savename, desc_arrays, info):
    size = desc_arrays[0].size
    with open(savename, 'w') as fh:
        fh.write('{} {}\n'.format(len(desc_arrays), size))
        for desc in desc_arrays:
            fh.write(' '.join(map(str, desc[0])) + '\n')
        for line in info:
            fh.write(line + '\n')


def get_res_paths(workdir=None):
    """
    Get the paths of the res files
    """
    import os
    from subprocess import check_output
    if workdir is None:
        workdir = './'
    output = check_output(['ca', '-v'], cwd=workdir).split(
        '\n')  # Run ca -v in shell and get outputs
    num_struct, _ = output[0].split()
    airss_info = output[int(num_struct) + 1:-1]
    fnames = [
        os.path.join(workdir,
                     l.split('\t')[0] + '.res') for l in airss_info
    ]
    return fnames, airss_info


@click.command('res2soap')
@click.argument('workdir')
@click.option('--nprocs',
              '-np',
              help='Number of processes for parallelisation.',
              default=4)
@click.option('--save-name',
              '-s',
              help='Save file name',
              default='soap_desc.xyz')
@click.option('--l-max', default=15)
@click.option('--n-max', default=15)
@click.option('--atoms-sigma', default=0.01)
@click.option('--Z', '-z', required=True, type=int)
@click.option('--species_Z', '-sz', required=True, type=int, multiple=True)
def res2soap(cutoff, workdir, l_max, n_max, atoms_sigma, Z, nprocs, save_name,
             species_Z):
    """
    Compute SOAP descriptors for res files, get the order or files from
    the `ca -v` commands for consistency.
    """
    from ase.io import read
    from tqdm import tqdm
    desc_settings = {
        'cutoff': cutoff,
        'l_max': l_max,
        'n_max': n_max,
        'atoms_sigma': atoms_sigma,
        'average': 'T',
        'n_species': len(species_Z),
        'Z': Z,
        'species_Z': ','.join(species_Z)
    }
    click.echo('Reading res files')
    fnames, airss_info = get_res_paths(workdir)
    atom_list = [[n, read(fn)] for n, fn in enumerate(tqdm(fnames))]

    click.echo('Computing descriptors in {} way parallel'.format(nprocs))
    comp = Atoms2Soap(desc_settings)
    pool = Pool(nprocs)
    par_res = list(pool.imap_unordered(comp.get_soap_desc, tqdm(atom_list)))

    click.echo('Re-ordering descriptor arrays')
    par_res.sort(key=lambda x: x[0])
    _, descs = zip(*par_res)  # This is the python2 zip

    click.echo('Saving results to {}'.format(save_name))
    save_file(save_name, descs, airss_info)


if __name__ == '__main__':
    res2soap()
