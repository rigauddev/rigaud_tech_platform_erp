import pytest

from app.modules.companies.application.validators import (
    is_valid_cnpj,
    normalize_code,
    normalize_document,
    normalize_email,
    normalize_phone,
    normalize_slug,
)
from app.modules.companies.domain.exceptions import InvalidCompanyDataError


@pytest.mark.unit
def test_normalize_document_accepts_valid_cnpj() -> None:
    assert normalize_document("11.222.333/0001-81") == "11222333000181"


@pytest.mark.unit
def test_rejects_invalid_cnpj() -> None:
    assert is_valid_cnpj("00000000000000") is False
    with pytest.raises(InvalidCompanyDataError):
        normalize_document("00.000.000/0000-00")


@pytest.mark.unit
def test_normalize_slug_and_code() -> None:
    assert normalize_slug(" rigaud-tech ") == "rigaud-tech"
    assert normalize_code(" rigaud ") == "RIGAUD"


@pytest.mark.unit
def test_rejects_invalid_slug_and_code() -> None:
    with pytest.raises(InvalidCompanyDataError):
        normalize_slug("Rigaud Tech")
    with pytest.raises(InvalidCompanyDataError):
        normalize_code("x")


@pytest.mark.unit
def test_normalize_email_and_phone() -> None:
    assert normalize_email(" CONTATO@EMPRESA.COM.BR ") == "contato@empresa.com.br"
    assert normalize_phone("(75) 98216-5869") == "75982165869"
