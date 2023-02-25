UART := /dev/cu.usbserial-D00137

PYTHON := python
SHELL := /bin/zsh

YOSYS_ENV := source toolchain/oss-cad-suite/environment
YOSYS_BIN := toolchain/oss-cad-suite/bin

AR := riscv64-unknown-elf-ar
AS := riscv64-unknown-elf-as
CC := riscv64-unknown-elf-gcc
LD := riscv64-unknown-elf-ld

OBJCOPY := riscv64-unknown-elf-objcopy
OBJDUMP := riscv64-unknown-elf-objdump


# - gateware ------------------------------------------------------------------

top: gateware/top.py
	$(YOSYS_ENV) && $(PYTHON) $<

test:
	$(YOSYS_ENV) && $(PYTHON) -m amaranth_boards.ulx3s 85F

blinky: gateware/examples/blinky.py
	$(YOSYS_ENV) && $(PYTHON) $<


# - gateware: soc -------------------------------------------------------------

gpio_soc: gateware/examples/gpio_soc.py
	$(YOSYS_ENV) && AR=$(AR) $(PYTHON) -m gateware.examples.$@

gpio_soc_load:
	PATH=$(PATH):$(YOSYS_BIN) openFPGALoader --board ulx3s build/top.bit


# - utilties ------------------------------------------------------------------

netcat:
	nc -u 192.168.20.250 1735

picocom:
	picocom --imap lfcrlf -b 115200 $(UART)
