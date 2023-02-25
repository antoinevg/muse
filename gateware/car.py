# - instance: EHXPLL ----------------------------------------------------------

from amaranth import *

class EHXPLL(Elaboratable):
    def __init__(self, i_domain, i_reset_less, o_domain, i_freq=25_000_000, o_freq=100_000_000):
        self.i_domain = i_domain
        self.i_reset_less = i_reset_less
        self.o_domain = o_domain
        self.i_freq = i_freq
        self.o_freq = o_freq

        # TODO
        self.fb_internal = False

        self.parameters = _calculate_parameters(i_freq, o_freq)

        # signals
        self.o_locked = Signal()

    def elaborate(self, platform):
        m = Module()

        pll_kwargs = {
            "a_ICP_CURRENT"            : 12,
            "a_LPF_RESISTOR"           : 8,
            "a_MFG_ENABLE_FILTEROPAMP" : 1,
            "a_MFG_GMCREF_SEL"         : 2,

            "p_INTFB_WAKE"             : "DISABLED",
            "p_STDBY_ENABLE"           : "DISABLED",
            "p_DPHASE_SOURCE"          : "DISABLED",
            "p_OUTDIVIDER_MUXA"        : "DIVA",
            "p_OUTDIVIDER_MUXB"        : "DIVB",
            "p_OUTDIVIDER_MUXC"        : "DIVC",
            "p_OUTDIVIDER_MUXD"        : "DIVD",

            "i_PHASESEL0"              : Const(0),
            "i_PHASESEL1"              : Const(0),
            "i_PHASEDIR"               : Const(1),
            "i_PHASESTEP"              : Const(1),
            "i_PHASELOADREG"           : Const(1),
            "i_PLLWAKESYNC"            : Const(0),
            "i_ENCLKOP"                : Const(0),

            "o_LOCK"                   : self.o_locked,

            "a_FREQUENCY_PIN_CLKI"     : int(self.i_freq / 1e6),
            "p_CLKI_DIV"               : self.parameters.i_div,
            "i_CLKI"                   : ClockSignal(self.i_domain),

            "a_FREQUENCY_PIN_CLKOP"    : int(self.parameters.op_freq / 1e6),
            "p_CLKOP_ENABLE"           : "ENABLED",
            "p_CLKOP_DIV"              : self.parameters.op_div,
            "p_CLKOP_CPHASE"           : self.parameters.cphase,
            "p_CLKOP_FPHASE"           : self.parameters.fphase,
            "o_CLKOP"                  : ClockSignal(self.o_domain),
        }

        # reset
        if not self.i_reset_less:
            pll_kwargs.update({
                "p_PLLRST_ENA" : "ENABLED",
                "i_RST"        : ResetSignal(self.i_domain),
            })
        else:
            pll_kwargs.update({
                "p_PLLRST_ENA" : "DISABLED",
                "i_RST"        : Const(0),
            })

        # feedback
        pll_kwargs.update({
            "p_CLKFB_DIV" : int(self.parameters.fb_div),
        })

        if self.fb_internal:
            clkintfb = Signal()
            pll_kwargs.update({
                "p_FEEDBK_PATH" : "INT_OP",
                "i_CLKFB"       : clkintfb,
                "o_CLKINTFB"    : clkintfb,
            })
        else:
            pll_kwargs.update({
                "p_FEEDBK_PATH" : "CLKOP",
                "i_CLKFB"       : ClockSignal(self.o_domain),
                "o_CLKINTFB"    : Signal(),
            })

        return Instance("EHXPLLL", **pll_kwargs)


# - helpers -------------------------------------------------------------------

class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)


def _calculate_parameters(i_freq, o_freq):
    i_div, fb_div, op_div, pfd_freq, op_freq = min(
        list(_variants(i_freq)),
        key=lambda v: _error(v, o_freq)
    )

    vco_freq = pfd_freq * fb_div * op_div
    op_shift = (1 / op_freq) * 0.5

    return Struct(**{
        "i_div"   : i_div,
        "fb_div"  : fb_div,
        "op_div"  : op_div,
        "op_freq" : op_freq,
        "cphase"  : op_shift * vco_freq,
        "fphase"  : 0
    })


def _variants(i_freq):
    for i_div in range(1, 128 + 1):
        pfd_freq = i_freq / i_div
        if not 3.125e6 <= pfd_freq <= 400e6:
            continue
        for fb_div in range(1, 80 + 1):
            for op_div in range(1, 128 + 1):
                vco_freq = pfd_freq * fb_div * op_div
                if not 400e6 <= vco_freq <= 800e6:
                    continue
                op_freq = vco_freq / op_div
                if not 10e6 <= op_freq <= 400e6:
                    continue
                yield (i_div, fb_div, op_div, pfd_freq, op_freq)


def _error(variant, o_freq):
    i_div, fb_div, op_div, pfd_freq, op_freq = variant
    vco_freq = pfd_freq * fb_div * op_div
    return abs(op_freq - o_freq), abs(vco_freq - 600e6), abs(pfd_freq - 200e6)


# - DomainGenerator -----------------------------------------------------------

from amaranth.lib.cdc import ResetSynchronizer
from amaranth_boards.ulx3s import ULX3S_85F_Platform

class ClockDomainGenerator(Elaboratable):
    def __init__(self, *, sync_clk_freq):
        self.sync_clk_freq = sync_clk_freq

    def elaborate(self, platform):
        m = Module()

        # TODO generate a separate domain for "eth"
        m.domains += [
            ClockDomain("_ref", reset_less=platform.default_rst is None, local=True),
            ClockDomain("sync"),
        ]

        m.d.comb += ClockSignal("_ref").eq(platform.request(platform.default_clk, 0).i)
        if platform.default_rst is not None:
            m.d.comb += ResetSignal("_ref").eq(platform.request(platform.default_rst, 0).i)

        if isinstance(platform, ULX3S_85F_Platform):
            m.submodules.sync_pll = sync_pll = EHXPLL(
                i_domain     = "_ref",
                i_reset_less = platform.default_rst is None,
                o_domain     = "sync",
                i_freq       = platform.default_clk_frequency,
                o_freq       = self.sync_clk_freq,
            )
        else:
            assert False

        if platform.default_rst is not None:
            sync_pll_arst = ~sync_pll.o_locked | ResetSignal("_ref")
        else:
            sync_pll_arst = ~sync_pll.o_locked

        m.submodules += ResetSynchronizer(sync_pll_arst, domain="sync")

        return m



# - main ----------------------------------------------------------------------

def main():

    i_freq = 25_000_000
    o_freq = 100_000_000

    variants = list(_variants(i_freq))
    #i_div, fb_div, op_div, pfd_freq, op_freq = min(variants, key=error)
    min_error = i_div, fb_div, op_div, pfd_freq, op_freq = min(variants, key=lambda v: _error(v, o_freq))
    print(min_error)

if __name__ == "__main__":
    main()
