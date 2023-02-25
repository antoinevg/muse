# muse.git

Be excellent to each other.

## Setup

### Environment
    # pyenv
    curl https://pyenv.run | bash

    # environment
    pyenv install 3.11.1
    pyenv virtualenv 3.11.1 flowdsp-amaranth
    pyenv local flowdsp-amaranth
    python3.11 -m pip install --upgrade pip

    # amaranth
    (cd toolchain/amaranth.git && pip install .)
    (cd toolchain/amaranth-boards.git && pip install .)
    (cd toolchain/amaranth-soc.git && pip install .)
    (cd toolchain/amaranth-stdio.git && pip install .)

    # lambdasoc
    pip install "git+https://github.com/lambdaconcept/minerva"
    pip install "git+https://github.com/enjoy-digital/litex"
    pip install "git+https://github.com/enjoy-digital/litedram"
    # waiting for https://github.com/lambdaconcept/lambdasoc/pull/18
    # pip install "git+https://github.com/lambdaconcept/lambdasoc"
    pip install "git+https://github.com/mndza/lambdasoc"

    # TODO just for lxterm - find a replacement
    mkdir toolchain
    wget https://raw.githubusercontent.com/enjoy-digital/litex/master/litex_setup.py
    python ./litex_setup.py --init --install --config=minimal

    # enable yosys
    source toolchain/oss-cad-suite/environment


### Test Installation

    python3 -m amaranth_boards.ulx3s 85F


### Uninstall

    pip uninstall -y -r <(pip freeze)

    pyenv uninstall flowdsp-amaranth
    pyenv uninstall 3.11.1


## Connections

### LAN8720

| Pin | Function |     | Pin | Function  |
| --- | -------- | --- | --- | --------- |
| 14  | TXD1     |     | 13  | n/c       |
| 12  | TX_EN    |     | 11  | TXD0      |
| 10  | RXD0     |     | 09  | RXD1      |
| 08  | R_RXCLK  |     | 07  | CRS_DV    |
| 06  | MDIO     |     | 05  | MDC       |
| 04  | GND      |     | 03  | GND       |
| 02  | VCC      |     | 01  | VCC       |


* Had to bodge nRST to pin 13.
* Not strictly a PMOD as it has one more pin for TXD1.


### ULX3S

*Use the connector next to the SDCARD*

| Pin  | Function |     | Pin  | Function  |
| ---- | -------- | --- | ---- | --------- |
| GN9  | TXD1     |     | GP9  | n/c       |
| GN10 | TX_EN    |     | GP10 | TXD0      |
| GN11 | RXD0     |     | GP11 | RXD1      |
| GN12 | R_RXCLK  |     | GP12 | CRS_DV    |
| GN13 | MDIO     |     | GP13 | MDC       |
| GND  | GND      |     | GND  | GND       |
| VCC  | VCC      |     | VCC  | VCC       |
