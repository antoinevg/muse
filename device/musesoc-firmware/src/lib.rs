#![feature(error_in_core)]
#![feature(panic_info_message)]
#![no_std]

// - modules ------------------------------------------------------------------

pub mod log;
pub mod panic_log;

// - aliases ------------------------------------------------------------------

pub use musesoc_hal as hal;
pub use musesoc_pac as pac;

// - constants ----------------------------------------------------------------

pub const SYSTEM_CLOCK_FREQUENCY: u32 = pac::clock::sysclk();

// - messages -----------------------------------------------------------------

#[derive(Debug)]
pub enum Message {
    // interrupts
    HandleInterrupt(pac::Interrupt),
    HandleUnknownInterrupt(usize),

    // TODO
    HandleGpioEvent(u32),
    HandleTimerEvent(u32),
}

// - Error --------------------------------------------------------------------
/*
#[derive(Debug, Copy, Clone, Eq, PartialEq, Ord, PartialOrd, Hash)]
pub enum ErrorKind {
    Unknown,
}

// trait: core::error::Error
impl core::error::Error for ErrorKind {
    #[allow(deprecated)]
    fn description(&self) -> &str {
        use ErrorKind::*;
        match self {
            Unknown => "TODO Unknown",
        }
    }
}

// trait:: core::fmt::Display
impl core::fmt::Display for ErrorKind {
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        core::fmt::Debug::fmt(&self, f)
    }
}

// trait: libgreat::error::Error
impl libgreat::error::Error for ErrorKind {
    type Error = Self;
    fn kind(&self) -> Self::Error {
        *self
    }
}
*/
