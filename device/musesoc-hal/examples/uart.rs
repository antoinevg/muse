#![no_std]
#![no_main]

use panic_halt as _;
use riscv_rt::entry;

use musesoc_hal as hal;
use musesoc_pac as pac;

use hal::hal::delay::DelayUs;
use hal::Timer;

use core::fmt::Write;
use hal::Serial;

const SYSTEM_CLOCK_FREQUENCY: u32 = 10_000_000;

#[entry]
fn main() -> ! {
    let peripherals = pac::Peripherals::take().unwrap();

    let leds = &peripherals.LEDS;
    let mut serial = Serial::new(peripherals.UART);
    let mut timer = Timer::new(peripherals.TIMER, SYSTEM_CLOCK_FREQUENCY);

    writeln!(serial, "Peripherals initialized, entering main loop.").unwrap();

    let mut direction = true;
    let mut led_state = 0b11000000;
    let mut uptime = 0;

    loop {
        timer.delay_ms(100_u32).unwrap();

        if uptime % 10 == 0 {
            writeln!(serial, "Uptime: {} seconds", uptime / 10).unwrap();
        }
        uptime += 1;

        if direction {
            led_state >>= 1;
            if led_state == 0b00000011 {
                direction = false;
                writeln!(serial, "left").unwrap();
            }
        } else {
            led_state <<= 1;
            if led_state == 0b11000000 {
                direction = true;
                writeln!(serial, "right").unwrap();
            }
        }

        leds.output.write(|w| unsafe { w.output().bits(led_state) });
    }
}
