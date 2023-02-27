#[doc = r"Register block"]
#[repr(C)]
pub struct RegisterBlock {
    #[doc = "0x00 - pmod1 csr register"]
    pub csr: CSR,
}
#[doc = "csr (rw) register accessor: an alias for `Reg<CSR_SPEC>`"]
pub type CSR = crate::Reg<csr::CSR_SPEC>;
#[doc = "pmod1 csr register"]
pub mod csr;
