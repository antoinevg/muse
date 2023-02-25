from amaranth import *


# - module: DomainGenerator ---------------------------------------------------

from amaranth.lib.cdc import ResetSynchronizer
from car import EHXPLL

class DomainGenerator(Elaboratable):
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


# - module: Blinky ------------------------------------------------------------

class Blinky(Elaboratable):
    def __init__(self, clock_divisor=21):
        self.clock_divisor = clock_divisor

        # registers
        self.slow_clk = Signal(self.clock_divisor + 1)

        # ports
        self.clk_out = Signal()

    def elaborate(self, platform):
        m = Module()

        # sync
        m.d.sync += self.slow_clk.eq(self.slow_clk + 1)

        # comb
        m.d.comb += self.clk_out.eq(self.slow_clk[self.clock_divisor])

        return m

    def ports(self):
        return [self.clk_out]


# - module: Top ---------------------------------------------------------------

from daqnet.ethernet.mac import MAC
from daqnet.ethernet.ip import IPStack


class Top(Elaboratable):
    def __init__(self):
        # configuration
        self.mac_addr = "02:44:4E:30:76:9E"
        self.ip4_addr = "192.168.20.250"

        # peripherals
        self.leds = Signal(8)
        self.rmii = Signal(7)
        self.mdio = Signal(2)
        self.button_pwr = Signal()

        # submodules
        self.blinky = Blinky(clock_divisor=25)

    def elaborate(self, platform):
        m = Module()

        # clock domain
        m.submodules.car = DomainGenerator(sync_clk_freq = 100_000_000)

        # resources
        if platform is not None:
            self.leds = Cat(platform.request("led", i) for i in range(6))
            self.rmii = platform.request("rmii", 0)
            self.mdio = platform.request("mdio", 0)
            self.phy  = platform.request("phy", 0)
            self.button_pwr = platform.request("button_pwr", 0)

        # Ethernet MAC
        mac = MAC(100e6, 0, self.mac_addr, self.rmii, self.mdio, self.phy.rst, self.leds[1])
        m.d.comb += [
            # Explicitly zero unused inputs in MAC
            mac.phy_reset.eq(0),
        ]

        # Daqnet "User" endpoint
        from daqnet.user import User
        user = User()

        # # IP Stack
        ipstack = IPStack(
            self.mac_addr,
            self.ip4_addr,
            16,
            1735,
            mac.rx_port,
            mac.tx_port,
            user.mem_r_port, # TODO
            user.mem_w_port, # TODO
        )
        m.d.comb += [
            mac.tx_start.eq(ipstack.tx_start),
            mac.tx_len.eq(ipstack.tx_len),
            mac.tx_offset.eq(ipstack.tx_offset),
            ipstack.rx_valid.eq(mac.rx_valid),
            ipstack.rx_len.eq(mac.rx_len),
            ipstack.rx_offset.eq(mac.rx_offset),
            mac.rx_ack.eq(ipstack.rx_ack),
            ipstack.user_tx.eq(user.transmit_packet),
            user.transmit_ready.eq(ipstack.user_ready),
            user.packet_received.eq(ipstack.user_rx),
        ]

        # connections
        m.d.comb += [
            self.leds[0].eq(self.blinky.clk_out),
        ]

        # submodules
        m.submodules += [
            self.blinky,
            mac,
            ipstack,
            user, # TODO
        ]

        return m

    def ports(self):
        return []


# - entry point ---------------------------------------------------------------

if __name__ == "__main__":
    from amaranth.build import Attrs, Pins, Resource, Subsignal
    from amaranth_boards.ulx3s import *

    # platform
    platform = ULX3S_85F_Platform()
    platform.add_resources([
        Resource("rmii", 0,
            Subsignal("txd1",    Pins("9-",  conn=("gpio", 0), dir="o")),
            Subsignal("txd0",    Pins("10+", conn=("gpio", 0), dir="o")),
            Subsignal("txen",    Pins("10-", conn=("gpio", 0), dir="o")), # tx_en
            Subsignal("rxd1",    Pins("11+", conn=("gpio", 0), dir="i")),
            Subsignal("rxd0",    Pins("11-", conn=("gpio", 0), dir="i")),
            Subsignal("crs_dv",  Pins("12+", conn=("gpio", 0), dir="i")),
            Subsignal("ref_clk", Pins("12-", conn=("gpio", 0), dir="i")), # r_rxclk
        ),
        Resource("mdio", 0,
            Subsignal("mdc",  Pins("13+", conn=("gpio", 0), dir="o")),
            Subsignal("mdio", Pins("13-", conn=("gpio", 0), dir="io")),
        ),
        Resource("phy", 0,
            Subsignal("rst",     Pins("9+",  conn=("gpio", 0), dir="o")),
        ),
        # alias these for daqnet's User module
        Resource("user_led", 0, Pins("E1", dir="o"), Attrs(IO_TYPE="LVCMOS33", DRIVE="4")),
        Resource("user_led", 1, Pins("H3", dir="o"), Attrs(IO_TYPE="LVCMOS33", DRIVE="4")),
    ])

    top = Top()
    platform.build(top, do_program=True)
