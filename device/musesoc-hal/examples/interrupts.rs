#![no_std]
#![no_main]

use panic_halt as _;
use riscv_rt::entry;

use musesoc_hal as hal;
use musesoc_pac as pac;

use core::fmt::Write;

#[entry]
fn main() -> ! {
    let peripherals = pac::Peripherals::take().unwrap();
    let mut serial = hal::Serial::new(peripherals.UART);

    // configure and enable timer
    let one_second = pac::clock::sysclk();
    let mut timer = hal::Timer::new(peripherals.TIMER, one_second);
    timer.set_timeout_ticks(one_second / 2);
    timer.enable();

    // enable timer events
    timer.listen(hal::timer::Event::TimeOut);

    // enable interrupts
    unsafe {
        // set mstatus register: interrupt enable
        riscv::interrupt::enable();

        // set mie register: machine external interrupts enable
        riscv::register::mie::set_mext();

        // write csr: enable timer interrupt
        pac::csr::interrupt::enable(pac::Interrupt::TIMER)
    }

    writeln!(serial, "Peripherals initialized, entering main loop.").unwrap();

    let mut uptime = 1;
    loop {
        writeln!(serial, "Uptime: {} seconds", uptime).unwrap();

        unsafe {
            riscv::asm::delay(pac::clock::sysclk());
        }
        uptime += 1;
    }
}

// interrupt handler
#[allow(non_snake_case)]
#[no_mangle]
fn MachineExternal() {
    static mut TOGGLE: bool = true;

    let mut serial = unsafe { hal::Serial::summon() };

    if pac::csr::interrupt::pending(pac::Interrupt::TIMER) {
        let mut timer = unsafe { hal::Timer::summon() };
        timer.clear_pending();

        writeln!(serial, "MachineExternal - timer interrupt").unwrap();

        // blinkenlights
        let peripherals = unsafe { pac::Peripherals::steal() };
        let leds = &peripherals.LEDS;

        if unsafe { TOGGLE } {
            leds.output.write(|w| unsafe { w.output().bits(255) });
        } else {
            leds.output.write(|w| unsafe { w.output().bits(0) });
        }
        unsafe { TOGGLE = !TOGGLE };
    } else {
        writeln!(serial, "MachineExternal - unknown interrupt").unwrap();
    }
}
