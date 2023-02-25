#![no_std]
#![no_main]

use panic_halt as _;
use riscv_rt::entry;

use musesoc_pac as pac;

const SYSTEM_CLOCK_FREQUENCY: u32 = 10_000_000;

#[entry]
fn main() -> ! {
    let peripherals = pac::Peripherals::take().unwrap();
    let leds = &peripherals.LEDS;
    let timer = &peripherals.TIMER;

    let mut direction = true;
    let mut led_state = 0b11000000;

    loop {
        delay_ms(timer, SYSTEM_CLOCK_FREQUENCY, 100);

        if direction {
            led_state >>= 1;
            if led_state == 0b00000011 {
                direction = false;
            }
        } else {
            led_state <<= 1;
            if led_state == 0b11000000 {
                direction = true;
            }
        }

        leds.output.write(|w| unsafe { w.output().bits(led_state) });
    }
}

fn delay_ms(timer: &pac::TIMER, sys_clk: u32, ms: u32) {
    let cycles: u32 = sys_clk / 1_000 * ms;

    timer.en.write(|w| w.en().bit(true));
    timer.reload.write(|w| unsafe { w.reload().bits(cycles) });

    while timer.ctr.read().ctr().bits() > 0 {
        unsafe {
            riscv::asm::nop();
        }
    }

    timer.en.write(|w| w.en().bit(false));
    timer.reload.write(|w| unsafe { w.reload().bits(0) });
}
