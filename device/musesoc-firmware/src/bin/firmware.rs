#![allow(unused_imports)] // TODO

#![no_std]
#![no_main]

use firmware::{hal, pac};
use musesoc_firmware as firmware;

use pac::csr::interrupt;

use log::{debug, error, info, trace, warn};

use riscv_rt::entry;

// - global static state ------------------------------------------------------

use firmware::Message;
use heapless::mpmc::MpMcQueue as Queue;
static MESSAGE_QUEUE: Queue<Message, 128> = Queue::new();

// - MachineExternal interrupt handler ----------------------------------------

#[allow(non_snake_case)]
#[no_mangle]
fn MachineExternal() {
    // peripherals
    let peripherals = unsafe { pac::Peripherals::steal() };
    let leds = &peripherals.LEDS;

    // debug
    let pending = interrupt::reg_pending();
    leds.output
        .write(|w| unsafe { w.output().bits(pending as u8) });

    // - usb1 interrupts - "host_phy" --
    let message = if false {

        // - GPIO Peripheral interrupts --
        Message::HandleGpioEvent(0)

    // - Unknown interrupt --
    } else {
        Message::HandleUnknownInterrupt(pending)
    };

    MESSAGE_QUEUE
        .enqueue(message)
        .expect("MachineExternal - message queue overflow")
}

// - main entry point ---------------------------------------------------------

#[entry]
fn main() -> ! {
    let peripherals = pac::Peripherals::take().unwrap();
    let leds = &peripherals.LEDS;
    leds.output.write(|w| unsafe { w.output().bits(0x0) });

    // initialize logging
    let serial = hal::Serial::new(peripherals.UART);
    firmware::log::init(serial);
    info!("logging initialized");

    // interrupts
    //gpio.enable_interrupts();
    unsafe {
        // set mstatus register: interrupt enable
        riscv::interrupt::enable();

        // set mie register: machine external interrupts enable
        riscv::register::mie::set_mext();

        // write csr: enable interrupts
        //interrupt::enable(pac::Interrupt::GPIO);
    }

    loop {
        while let Some(message) = MESSAGE_QUEUE.dequeue() {
            match message {
                // gpio interrupts
                //Message::HandleInterrupt(pac::Interrupt::GPIO0) => {
                //    trace!("MachineExternal - GPIO0\n");
                //}

                // unhandled
                _ => {
                    warn!("Unhandled message: {:?}\n", message);
                }
            }
        }
    }
}
