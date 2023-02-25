//! Peripheral access API for MUSE SoC designs generated using svd2rust.

#![no_std]

#[macro_use]
mod macros;

pub mod cpu;
pub mod csr;
pub mod register {
    pub use crate::cpu::minerva;
}

pub mod clock {
    const SYSTEM_CLOCK_FREQUENCY: u32 = 60_000_000;

    pub const fn sysclk() -> u32 {
        SYSTEM_CLOCK_FREQUENCY
    }
}

#[deny(dead_code)]
#[deny(improper_ctypes)]
#[deny(missing_docs)]
#[deny(no_mangle_generic_items)]
#[deny(non_shorthand_field_patterns)]
#[deny(overflowing_literals)]
#[deny(path_statements)]
#[deny(patterns_in_fns_without_body)]
#[deny(private_in_public)]
#[deny(unconditional_recursion)]
#[deny(unused_allocation)]
#[deny(unused_comparisons)]
#[deny(unused_parens)]
#[deny(while_true)]
#[allow(non_camel_case_types)]
#[allow(non_snake_case)]
mod generated;

pub use generated::generic::*;
pub use generated::*;
