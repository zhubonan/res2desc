"""
Converting from RES to SOAP
"""
from dscribe.descriptors import SOAP


def _instance_method_alias(obj, arg):
    """
    Alias for instance method that allows the method to be called in a
    multiprocessing pool
    """
    res = obj.get_desc_wrap(arg)
    return res


class Atoms2Desc:
    """Computing SOAP descriptor using DScribe"""
    def __init__(self, desc_dict):

        self.desc_settings = desc_dict
        self._desc = None  # The actual descriptor object

        self.setup_desc()

    def setup_desc(self):

        raise NotImplementedError

    def get_desc(self, atoms, n_jobs=1):
        """
        Get descriptor for a list of atoms
        """
        return self._desc.create(atoms, n_jobs=n_jobs)


class Atoms2Soap(Atoms2Desc):
    def setup_desc(self):

        self._desc = SOAP(**self.desc_settings)


# if __name__ == '__main__':
#     # pylint: disable=no-value-for-parameter
#     res2soap()
