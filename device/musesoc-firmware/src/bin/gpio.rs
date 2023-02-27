#![allow(unused_imports, unused_variables)]

#![no_std]
#![no_main]

use riscv_rt::entry;

use firmware::hal;
use firmware::pac;
use musesoc_firmware as firmware;

use hal::Serial;

use hal::hal::delay::DelayUs;
use hal::Timer;

use log::{debug, info};

#[entry]
fn main() -> ! {
    let peripherals = pac::Peripherals::take().unwrap();

    // initialize logging
    let serial = Serial::new(peripherals.UART);
    firmware::log::init(serial);

    let leds = &peripherals.LEDS;
    let pmod0 = &peripherals.PMOD0;
    let pmod1 = &peripherals.PMOD1;
    let mut timer = Timer::new(peripherals.TIMER, firmware::SYSTEM_CLOCK_FREQUENCY);

    // configure pmod0 - pin 0-3: input, 4: output
    pmod0.mode.write(|w| unsafe {
        w.mode().bits(0b1_0000)
    });

    info!("Peripherals initialized, entering main loop.");

    let mut counter = 0;
    let mut direction = true;
    let mut led_state = 0b11000000;

    loop {
        timer.delay_ms(1000).unwrap();

        // pmod1, leds
        leds.output.write(|w| unsafe { w.output().bits(led_state) });
        pmod1.csr.write(|w| unsafe { w.csr().bits(led_state) });
        //let bits1: u32 = pmod1.csr.read().bits();
        //info!("bits1: {bits1:#010b}");
        //info!("leds:  {led_state:#010b}\n");
        if direction {
            led_state >>= 1;
            if led_state == 0b00000011 {
                direction = false;
                //info!("left: {}", counter);
            }
        } else {
            led_state <<= 1;
            if led_state == 0b11000000 {
                direction = true;
                //debug!("right: {}", counter);
            }
        }

        // pmod0
        let bits0: u32 = pmod0.csr_r.read().bits();
        info!("bits0: {bits0:#018b}");

        if counter % 2 == 0 {
            info!("on");
            pmod0.csr_w.write(|w| unsafe { w.csr_w().bits(0b0000_0000_0001_0000) });
        } else {
            info!("off");
            pmod0.csr_w.write(|w| unsafe { w.csr_w().bits(0b0000_0000_0000_0000) });
        }

        counter += 1;
    }
}
