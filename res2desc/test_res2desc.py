"""
Run tests
"""

from click.testing import CliRunner
from res2desc import res2desc


def test_command():
    runner = CliRunner()
    result = runner.invoke(res2desc, ['test_data', '-z', '13', '-sz', '13'])
    assert result.exit_code == 0
