"""
Run tests
"""
# pylint: disable=redefined-outer-name, import-outside-toplevel
from pathlib import Path
import pytest

from click.testing import CliRunner

from ase.build import molecule, bulk
from res2desc import Atoms2Soap
from res2desc.cli import cli
from res2desc.res import read_res, read_stream


@pytest.fixture
def data_folder():
    this_file = Path(__file__)
    folder = this_file.parent.parent / 'test_data'
    return folder


@pytest.fixture
def water_atoms():
    """Test fixture water_atoms molecules"""
    return molecule('H2O')


@pytest.fixture
def cu_atoms():
    """Test fixture cu_atoms FCC"""
    return bulk('Cu', 'fcc', a=3.6, cubic=True)


@pytest.fixture
def res_files_handle(data_folder):
    """Fixture to give a file handle of concatnated files"""
    import fileinput
    from io import StringIO
    res_files = list(data_folder.glob('*.res'))[:3]
    buf = StringIO()
    with fileinput.input(files=res_files) as fhandle:
        for line in fhandle:
            buf.write(line)
    buf.seek(0)
    return buf


def test_read(data_folder):
    """Test reading a single res"""
    res_file = list(data_folder.glob('*.res'))[0]
    with open(res_file) as fhd:
        data = fhd.readlines()
    titl, _ = read_res(data)
    assert len(titl) > 0


def test_read_many(res_files_handle):
    """Test reading many res files"""
    _, data = read_stream(res_files_handle)
    res_files_handle.close()
    assert len(data) == 3


def test_soap(water_atoms):
    """Test building SOAP descripters"""
    initd = {
        'rcut': 10,
        'sigma': 0.1,
        'lmax': 2,
        'nmax': 2,
        'species': ['H', 'O']
    }
    soap = Atoms2Soap(initd)
    res = soap.get_desc(water_atoms, 1)
    assert res.shape[0] == 3


def test_soap_avg(cu_atoms):
    """Test building SOAP descripters"""
    initd = {
        'rcut': 10,
        'sigma': 0.1,
        'lmax': 2,
        'nmax': 2,
        'species': ['Cu'],
        'average': True
    }
    soap = Atoms2Soap(initd)
    res = soap.get_desc(cu_atoms, 1)
    assert res.shape[0] == 1


def test_command_soap(res_files_handle):
    """Test the commandline interface"""
    runner = CliRunner()
    inp = res_files_handle.read()
    res_files_handle.close()
    for style in ['1', '2']:
        result = runner.invoke(
            cli, ['--no-cryan', '--cryan-style-out', style, 'soap'], input=inp)
        assert result.exit_code == 0


def test_command_xyz(res_files_handle):
    """Test the xyz command"""
    runner = CliRunner()
    result = runner.invoke(cli, ['--no-cryan', 'xyz'],
                           input=res_files_handle.read())
    res_files_handle.close()
    assert result.exit_code == 0
