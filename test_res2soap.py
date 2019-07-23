from click.testing import CliRunner
from res2soap import res2soap


def test_command():
    runner = CliRunner()
    result = runner.invoke(res2soap, ['test_data', '-z', '13', '-sz', '13'])
    assert result.exit_code == 0
