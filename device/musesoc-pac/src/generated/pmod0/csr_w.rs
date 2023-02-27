#[doc = "Register `csr_w` writer"]
pub struct W(crate::W<CSR_W_SPEC>);
impl core::ops::Deref for W {
    type Target = crate::W<CSR_W_SPEC>;
    #[inline(always)]
    fn deref(&self) -> &Self::Target {
        &self.0
    }
}
impl core::ops::DerefMut for W {
    #[inline(always)]
    fn deref_mut(&mut self) -> &mut Self::Target {
        &mut self.0
    }
}
impl From<crate::W<CSR_W_SPEC>> for W {
    #[inline(always)]
    fn from(writer: crate::W<CSR_W_SPEC>) -> Self {
        W(writer)
    }
}
#[doc = "Field `csr_w` writer - pmod0 csr_w register field"]
pub type CSR_W_W<'a, const O: u8> = crate::FieldWriter<'a, u32, CSR_W_SPEC, u16, u16, 14, O>;
impl W {
    #[doc = "Bits 0:13 - pmod0 csr_w register field"]
    #[inline(always)]
    #[must_use]
    pub fn csr_w(&mut self) -> CSR_W_W<0> {
        CSR_W_W::new(self)
    }
    #[doc = "Writes raw bits to the register."]
    #[inline(always)]
    pub unsafe fn bits(&mut self, bits: u32) -> &mut Self {
        self.0.bits(bits);
        self
    }
}
#[doc = "pmod0 csr_w register\n\nThis register you can [`write_with_zero`](crate::generic::Reg::write_with_zero), [`reset`](crate::generic::Reg::reset), [`write`](crate::generic::Reg::write). See [API](https://docs.rs/svd2rust/#read--modify--write-api).\n\nFor information about available fields see [csr_w](index.html) module"]
pub struct CSR_W_SPEC;
impl crate::RegisterSpec for CSR_W_SPEC {
    type Ux = u32;
}
#[doc = "`write(|w| ..)` method takes [csr_w::W](W) writer structure"]
impl crate::Writable for CSR_W_SPEC {
    type Writer = W;
    const ZERO_TO_MODIFY_FIELDS_BITMAP: Self::Ux = 0;
    const ONE_TO_MODIFY_FIELDS_BITMAP: Self::Ux = 0;
}
#[doc = "`reset()` method sets csr_w to value 0"]
impl crate::Resettable for CSR_W_SPEC {
    const RESET_VALUE: Self::Ux = 0;
}
