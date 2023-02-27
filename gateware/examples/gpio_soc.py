from soc.musesoc import MuseSoC

from amaranth              import C, Cat, Elaboratable, Module, Signal
from amaranth.hdl.rec      import Record
from amaranth_boards.ulx3s import ULX3S_85F_Platform

from lambdasoc.periph import Peripheral

import logging
import os
import sys


# - LedPeripheral -------------------------------------------------------------

class LedPeripheral(Peripheral, Elaboratable):
    """ Example peripheral that controls the board's LEDs. """

    def __init__(self):
        super().__init__()

        # peripheral control register
        self._output = self.csr_bank().csr(8, "w")

        # peripheral bus
        self._bridge = self.bridge(data_width=32, granularity=8, alignment=2)
        self.bus     = self._bridge.bus


    def elaborate(self, platform):
        m = Module()

        # platform
        leds = Cat(platform.request("led", i) for i in range(8))

        # sync
        with m.If(self._output.w_stb):
            m.d.sync += leds.eq(self._output.w_data)

        # submodules
        m.submodules.bridge = self._bridge

        return m


# - GpioPeripheral ------------------------------------------------------------

class GpioInputPeripheral(Peripheral, Elaboratable):
    """ GPIO input peripheral. """

    def __init__(self, pins):
        super().__init__()

        self.pins = pins

        # peripheral control register
        self._csr  = self.csr_bank().csr(8, "r")

        # peripheral bus
        self._bridge = self.bridge(data_width=32, granularity=8, alignment=2)
        self.bus     = self._bridge.bus

    def elaborate(self, platform):
        m = Module()

        # sync
        with m.If(self._csr.r_stb):
            m.d.sync += self._csr.r_data.eq(self.pins)

        # submodules
        m.submodules.bridge = self._bridge

        return m


class GpioOutputPeripheral(Peripheral, Elaboratable):
    """ GPIO output peripheral. """

    def __init__(self, pins):
        super().__init__()

        self.pins = pins

        # peripheral control register
        self._csr  = self.csr_bank().csr(8, "rw")

        # peripheral bus
        self._bridge = self.bridge(data_width=32, granularity=8, alignment=2)
        self.bus     = self._bridge.bus

    def elaborate(self, platform):
        m = Module()

        # sync
        with m.If(self._csr.w_stb):
            m.d.sync += self.pins.eq(self._csr.w_data)
        with m.If(self._csr.r_stb):
            m.d.sync += self._csr.r_data.eq(self.pins)

        # submodules
        m.submodules.bridge = self._bridge

        return m


class GpioPeripheral(Peripheral, Elaboratable):
    """ GPIO peripheral. """

    def __init__(self, pins=None):
        super().__init__()

        self.pins = pins
        self.width = len(pins)
        print("WIDTH: {}", self.width)

        # peripheral control register
        self._mode = self.csr_bank().csr(14, "rw")
        self._csr_r = self.csr_bank().csr(14, "r")
        self._csr_w = self.csr_bank().csr(14, "w")

        # peripheral bus
        self._bridge = self.bridge(data_width=32, granularity=8, alignment=2)
        self.bus     = self._bridge.bus

    def elaborate(self, platform):
        m = Module()

        # TODO
        self.pins = platform.request("pmod", 0)

        # pin modes - https://github.com/RobertBaruch/nmigen-tutorial/blob/master/9_synthesis.md
        pin_modes = Signal(14) # direction: 0=input, 1=output
        with m.If(self._csr_w.w_stb):
            m.d.sync += pin_modes.eq(self._mode.w_data)
        #for index, (name, pin) in enumerate(self.pins.fields.items()):
        #    m.d.comb += pin.oe.eq(pin_modes[index])
        m.d.comb += map_resource(
            self.pins,
            lambda index, name, pin:
                pin.oe.eq(pin_modes[index])
        )

        # set pin output states
        reg_out = Signal(14)
        with m.If(self._csr_w.w_stb):
            m.d.sync += reg_out.eq(self._csr_w.w_data)
        m.d.comb += map_resource(
            self.pins,
            lambda index, name, pin:
                pin.o.eq(reg_out[index])
        )

        # get pin input states
        reg_in = Signal(14)
        m.d.comb += map_resource(
            self.pins,
            lambda index, name, pin:
                reg_in[index].eq(pin.i)
        )
        with m.If(self._csr_r.r_stb):
            m.d.sync += self._csr_r.r_data.eq(~reg_in)

        # submodules
        m.submodules.bridge = self._bridge

        return m

def map_resource(resource, f):
    return [f(index, name, pin) for index, (name, pin) in enumerate(resource.fields.items())]

# - Top -----------------------------------------------------------------------

class Top(Elaboratable):
    def __init__(self, clock_frequency=int(50e6)):
        self.clock_frequency = clock_frequency

        # uart pins
        self.uart_pins = Record([
            ('rx', [('i', 1)]),
            ('tx', [('o', 1)])
        ])

        # soc + bios
        self.soc = MuseSoC(clock_frequency, internal_sram_size=65536)
        self.soc.add_bios_and_peripherals(uart_pins=self.uart_pins)

        # leds
        self.leds = LedPeripheral()
        self.soc.add_peripheral(self.leds)

        # pmod0, pmod1
        self.pmod0_pins = Signal(14)
        self.pmod1_pins = Signal(8)

        self.pmod0 = GpioPeripheral(pins=self.pmod0_pins)
        self.pmod1 = GpioOutputPeripheral(pins=self.pmod1_pins)
        self.soc.add_peripheral(self.pmod0)
        self.soc.add_peripheral(self.pmod1)


    def elaborate(self, platform):
        m = Module()
        m.submodules.soc = self.soc

        # clock domain
        if  isinstance(platform, ULX3S_85F_Platform):
            from car import ClockDomainGenerator
            m.submodules.car = ClockDomainGenerator(sync_clk_freq=self.clock_frequency)
        else:
            logging.error("Unsupported platform: {}".format(platform))
            sys.exit()

        # pmod0, pmod1
        platform_pmod0 = None #platform.request("pmod", 0)
        platform_pmod1 = platform.request("pmod", 1)
        m.d.comb += [
            #platform_pmod0.eq(self.pmod0_pins),
            platform_pmod1.eq(self.pmod1_pins),
        ]

        # uart
        uart_io = platform.request("uart", 0)
        m.d.comb += [
            uart_io.tx.o.eq(self.uart_pins.tx),
            self.uart_pins.rx.eq(uart_io.rx)
        ]
        if hasattr(uart_io.tx, 'oe'):
            m.d.comb += uart_io.tx.oe.eq(~self.soc.uart._phy.tx.rdy),

        return m


# - main ----------------------------------------------------------------------


if __name__ == "__main__":
    from soc.generate import Generate, Introspect

    from amaranth.build import Attrs, Pins, Resource, Subsignal

    build_dir = os.path.join("build")

    # configure logging
    LOG_FORMAT_COLOR = "\u001b[37;1m%(levelname)-8s| \u001b[0m\u001b[1m%(module)-12s|\u001b[0m %(message)s"
    LOG_FORMAT_PLAIN = "%(levelname)-8s:n%(module)-12s>%(message)s"
    if sys.stdout.isatty():
        log_format = LOG_FORMAT_COLOR
    else:
        log_format = LOG_FORMAT_PLAIN
    logging.basicConfig(level=logging.DEBUG, format=log_format)

    # disable UnusedElaborable warnings
    from amaranth._unused import MustUse
    MustUse._MustUse__silence = True

    # fix litex build
    thirdparty = os.path.join(build_dir, "lambdasoc.soc.cpu/bios/3rdparty/litex")
    if not os.path.exists(thirdparty):
        logging.info("Fixing build, creating output directory: {}".format(thirdparty))
        os.makedirs(thirdparty)

    # select platform
    #platform = luna.gateware.platform.get_appropriate_platform()
    #platform = LUNAPlatformRev0D4()
    platform = ULX3S_85F_Platform()

    # add resources for ulx3s pmods
    platform.add_resources([
        Resource("pmod", 0,
            Subsignal("gn0", Pins("0-", conn=("gpio", 0), dir="io")),
            Subsignal("gn1", Pins("1-", conn=("gpio", 0), dir="io")),
            Subsignal("gn2", Pins("2-", conn=("gpio", 0), dir="io")),
            Subsignal("gn3", Pins("3-", conn=("gpio", 0), dir="io")),
            Subsignal("gn4", Pins("4-", conn=("gpio", 0), dir="io")),
            Subsignal("gn5", Pins("5-", conn=("gpio", 0), dir="io")),
            Subsignal("gn6", Pins("6-", conn=("gpio", 0), dir="io")),
            Subsignal("gp0", Pins("0+", conn=("gpio", 0), dir="io")),
            Subsignal("gp1", Pins("1+", conn=("gpio", 0), dir="io")),
            Subsignal("gp2", Pins("2+", conn=("gpio", 0), dir="io")),
            Subsignal("gp3", Pins("3+", conn=("gpio", 0), dir="io")),
            Subsignal("gp4", Pins("4+", conn=("gpio", 0), dir="io")),
            Subsignal("gp5", Pins("5+", conn=("gpio", 0), dir="io")),
            Subsignal("gp6", Pins("6+", conn=("gpio", 0), dir="io")),
        ),

        # TODO this is convenient, but it's not a great interpretation
        Resource("pmod", 1,
            Subsignal("gp10", Pins("10+", conn=("gpio", 0), dir="o")),
            Subsignal("gn10", Pins("10-", conn=("gpio", 0), dir="o")),
            Subsignal("gp11", Pins("11+", conn=("gpio", 0), dir="o")),
            Subsignal("gn11", Pins("11-", conn=("gpio", 0), dir="o")),
            Subsignal("gp12", Pins("12+", conn=("gpio", 0), dir="o")),
            Subsignal("gn12", Pins("12-", conn=("gpio", 0), dir="o")),
            Subsignal("gp13", Pins("13+", conn=("gpio", 0), dir="o")),
            Subsignal("gn13", Pins("13-", conn=("gpio", 0), dir="o")),
        )
    ])

    # instantiate design
    if isinstance(platform, ULX3S_85F_Platform):
        logging.info("Instantiating design for ULX3s")
        top = Top(clock_frequency=int(20e6))
    else:
        logging.error("Unsupported platform: {}".format(platform))
        sys.exit()

    # build litex bios
    logging.info("Building bios")
    top.soc.build(name="soc", build_dir=build_dir, do_init=True)

    # generate soc artifacts
    generate = Generate(top.soc)

    # generate: svd file
    path = os.path.join(build_dir, "gensvd")
    if not os.path.exists(path):
        os.makedirs(path)
    logging.info("Generating svd file: {}".format(path))
    with open(os.path.join(path, "musesoc.svd"), "w") as f:
        generate.svd(file=f)

    # generate: rust memory.x file
    path = os.path.join(build_dir, "genrust")
    if not os.path.exists(path):
        os.makedirs(path)
    logging.info("Generating memory.x file: {}".format(path))
    with open(os.path.join(path, "memory.x"), "w") as f:
        generate.memory_x(file=f)

    # synthesize design
    logging.info("Synthesizing design")
    platform.build(top, do_program=False)

    # log resources
    Introspect(top.soc).log_resources()

    print("Synthesis completed. Use 'make gpio_soc_load' to load bitsream to device.")
