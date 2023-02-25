from soc.musesoc import MuseSoC

from amaranth              import Elaboratable, Module, Cat
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

# - Top -----------------------------------------------------------------------

class Top(Elaboratable):
    def __init__(self, clock_frequency=int(50e6)):
        self.clock_frequency = clock_frequency

        # uart
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

    # instantiate design
    if isinstance(platform, ULX3S_85F_Platform):
        logging.info("Instantiating design for ULX3s")
        top = Top(clock_frequency=int(50e6))
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
