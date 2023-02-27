#[doc = r"Register block"]
#[repr(C)]
pub struct RegisterBlock {
    #[doc = "0x00 - pmod0 mode register"]
    pub mode: MODE,
    _reserved1: [u8; 0x04],
    #[doc = "0x08 - pmod0 csr_r register"]
    pub csr_r: CSR_R,
    _reserved2: [u8; 0x04],
    #[doc = "0x10 - pmod0 csr_w register"]
    pub csr_w: CSR_W,
}
#[doc = "mode (rw) register accessor: an alias for `Reg<MODE_SPEC>`"]
pub type MODE = crate::Reg<mode::MODE_SPEC>;
#[doc = "pmod0 mode register"]
pub mod mode;
#[doc = "csr_r (r) register accessor: an alias for `Reg<CSR_R_SPEC>`"]
pub type CSR_R = crate::Reg<csr_r::CSR_R_SPEC>;
#[doc = "pmod0 csr_r register"]
pub mod csr_r;
#[doc = "csr_w (w) register accessor: an alias for `Reg<CSR_W_SPEC>`"]
pub type CSR_W = crate::Reg<csr_w::CSR_W_SPEC>;
#[doc = "pmod0 csr_w register"]
pub mod csr_w;
