"""Generate programming support files from SoC designs."""

from .gensvd import GenSVD
from .genrust import GenRust

from lambdasoc.soc.cpu import CPUSoC, BIOSBuilder


class Generate:
    # TODO add params: vendor, design_name, description, build_dir
    def __init__(self, soc: CPUSoC):
        self._soc = soc


    # - integration.gensvd --

    def svd(self, file=None):
        """ Generates a svd file for the given SoC that can be used by external tools such as 'svdrust'.
        Parameters:
            file       -- Optional. If provided, this will be treated as the file= argument to the print()
                          function. This can be used to generate file content instead of printing to the terminal.
        """

        GenSVD(self._soc).generate_svd(file=file)


    # - integration.genrust --

    def memory_x(self, file=None):
        """ Generates a svd file for the given SoC that can be used by external tools such as 'svdrust'.
        Parameters:
            file       -- Optional. If provided, this will be treated as the file= argument to the print()
                          function. This can be used to generate file content instead of printing to the terminal.
        """

        GenRust(self._soc).generate_memory_x(file=file)
