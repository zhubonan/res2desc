"""
Run tests
"""
from pathlib import Path
import pytest

from click.testing import CliRunner
from res2desc.cli import cmd_res2soap

from ase.build import molecule, bulk
from res2desc import Atoms2Soap
from res2desc.res import read_res, read_stream


@pytest.fixture
def data_folder():
    this_file = Path(__file__)
    folder = this_file.parent.parent / 'test_data'
    return folder


@pytest.fixture
def water():
    """Test fixture water molecules"""
    return molecule('H2O')


@pytest.fixture
def Cu():
    """Test fixture Cu FCC"""
    return bulk('Cu', 'fcc', a=3.6, cubic=True)


def test_read(data_folder):
    res_file = list(data_folder.glob('*.res'))[0]
    with open(res_file) as fh:
        data = fh.readlines()
    read_res(data)


def test_read_many(data_folder):
    from fileinput import FileInput
    res_files = list(data_folder.glob('*.res'))[:3]
    with FileInput(files=res_files) as fh:
        data = read_stream(fh)
    assert len(data) == 3


def test_soap(water):
    initd = {
        'rcut': 10,
        'sigma': 0.1,
        'lmax': 2,
        'nmax': 2,
        'species': ['H', 'O']
    }
    soap = Atoms2Soap(initd)
    res = soap.get_desc(water, 1)
    assert res.shape[0] == 3


def test_soap_avg(Cu):
    initd = {
        'rcut': 10,
        'sigma': 0.1,
        'lmax': 2,
        'nmax': 2,
        'species': ['Cu'],
        'average': True
    }
    soap = Atoms2Soap(initd)
    res = soap.get_desc(Cu, 1)
    assert res.shape[0] == 1


def _test_command():
    runner = CliRunner()
    result = runner.invoke(cmd_res2soap,
                           ['test_data', '-z', '13', '-sz', '13'])
    print(result)
    assert result.exit_code == 0
