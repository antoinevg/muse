#[doc = "Register `csr_r` reader"]
pub struct R(crate::R<CSR_R_SPEC>);
impl core::ops::Deref for R {
    type Target = crate::R<CSR_R_SPEC>;
    #[inline(always)]
    fn deref(&self) -> &Self::Target {
        &self.0
    }
}
impl From<crate::R<CSR_R_SPEC>> for R {
    #[inline(always)]
    fn from(reader: crate::R<CSR_R_SPEC>) -> Self {
        R(reader)
    }
}
#[doc = "Field `csr_r` reader - pmod0 csr_r register field"]
pub type CSR_R_R = crate::FieldReader<u16, u16>;
impl R {
    #[doc = "Bits 0:13 - pmod0 csr_r register field"]
    #[inline(always)]
    pub fn csr_r(&self) -> CSR_R_R {
        CSR_R_R::new((self.bits & 0x3fff) as u16)
    }
}
#[doc = "pmod0 csr_r register\n\nThis register you can [`read`](crate::generic::Reg::read). See [API](https://docs.rs/svd2rust/#read--modify--write-api).\n\nFor information about available fields see [csr_r](index.html) module"]
pub struct CSR_R_SPEC;
impl crate::RegisterSpec for CSR_R_SPEC {
    type Ux = u32;
}
#[doc = "`read()` method returns [csr_r::R](R) reader structure"]
impl crate::Readable for CSR_R_SPEC {
    type Reader = R;
}
#[doc = "`reset()` method sets csr_r to value 0"]
impl crate::Resettable for CSR_R_SPEC {
    const RESET_VALUE: Self::Ux = 0;
}
