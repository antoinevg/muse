#![feature(error_in_core)]
#![feature(panic_info_message)]
#![no_std]

// - modules ------------------------------------------------------------------

pub mod gpio;
pub mod serial;
pub mod timer;


// - export peripherals -------------------------------------------------------

pub use serial::Serial;
pub use timer::Timer;


// - Result -------------------------------------------------------------------

/// Result<T>
pub type Result<T> = core::result::Result<T, &'static (dyn core::error::Error + 'static)>;


// - re-export dependencies ---------------------------------------------------

pub use musesoc_pac as pac;

pub use embedded_hal as hal;
pub use embedded_hal_0 as hal_0;
pub(crate) use embedded_hal_nb as hal_nb;

pub use nb;
