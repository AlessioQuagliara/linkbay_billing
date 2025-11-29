"""
Constants and enums for billing system.
"""

from enum import Enum


class InvoiceType(str, Enum):
    """Invoice document types."""
    
    INVOICE = "invoice"
    CREDIT_NOTE = "credit_note"
    DEBIT_NOTE = "debit_note"
    PROFORMA = "proforma"
    RECEIPT = "receipt"
    ADVANCE_INVOICE = "advance_invoice"


class InvoiceStatus(str, Enum):
    """Invoice lifecycle status."""
    
    DRAFT = "draft"
    ISSUED = "issued"
    SENT = "sent"
    VIEWED = "viewed"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"
    OVERDUE = "overdue"
    CANCELED = "canceled"
    REFUNDED = "refunded"


class PaymentStatus(str, Enum):
    """Payment status for invoice."""
    
    UNPAID = "unpaid"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"
    REFUNDED = "refunded"


class VATRate(str, Enum):
    """Common VAT rates (user can define custom)."""
    
    STANDARD_IT = "22"  # Italy standard
    REDUCED_IT_10 = "10"  # Italy reduced
    REDUCED_IT_5 = "5"  # Italy super-reduced
    REDUCED_IT_4 = "4"  # Italy special
    EXEMPT = "0"  # VAT exempt
    REVERSE_CHARGE = "RC"  # Reverse charge
    SPLIT_PAYMENT = "SP"  # Split payment (Italy)
    INTRA_EU = "EU"  # Intra-EU supply
    STANDARD_EU = "20"  # Generic EU standard


class TaxType(str, Enum):
    """Types of taxes and deductions."""
    
    VAT = "vat"
    RETENTION = "retention"  # Ritenuta d'acconto
    SOCIAL_SECURITY = "social_security"  # Contributo previdenziale
    STAMP_DUTY = "stamp_duty"  # Bollo
    WITHHOLDING_TAX = "withholding_tax"


class DocumentLanguage(str, Enum):
    """Supported languages for invoice documents."""
    
    IT = "it"  # Italian
    EN = "en"  # English
    DE = "de"  # German
    FR = "fr"  # French
    ES = "es"  # Spanish


class EInvoiceFormat(str, Enum):
    """E-invoice export formats."""
    
    FATTURA_PA = "fatturapa"  # Italian FatturaPA XML
    PEPPOL_UBL = "peppol"  # PEPPOL UBL 2.1
    FACTUR_X = "facturx"  # Factur-X (FR/DE)
    SIMPLE_XML = "simple_xml"  # Generic XML


class PaymentMethod(str, Enum):
    """Payment methods."""
    
    BANK_TRANSFER = "bank_transfer"
    CREDIT_CARD = "credit_card"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    CASH = "cash"
    CHECK = "check"
    SEPA_DIRECT_DEBIT = "sepa_dd"
    RIBA = "riba"  # Italy
    RID = "rid"  # Italy


class PaymentTerms(str, Enum):
    """Payment terms."""
    
    IMMEDIATE = "immediate"
    NET_7 = "net_7"
    NET_15 = "net_15"
    NET_30 = "net_30"
    NET_60 = "net_60"
    NET_90 = "net_90"
    END_OF_MONTH = "eom"
    ADVANCE = "advance"


class CurrencyCode(str, Enum):
    """ISO 4217 currency codes."""
    
    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"
    CHF = "CHF"
    JPY = "JPY"


# Default VAT rates by country
DEFAULT_VAT_RATES = {
    "IT": {"standard": 22, "reduced": [10, 5, 4]},
    "DE": {"standard": 19, "reduced": [7]},
    "FR": {"standard": 20, "reduced": [10, 5.5, 2.1]},
    "ES": {"standard": 21, "reduced": [10, 4]},
    "GB": {"standard": 20, "reduced": [5, 0]},
    "AT": {"standard": 20, "reduced": [10, 13]},
    "BE": {"standard": 21, "reduced": [12, 6]},
    "NL": {"standard": 21, "reduced": [9]},
    "PT": {"standard": 23, "reduced": [13, 6]},
}

# Retention rates (Italy)
RETENTION_RATES_IT = {
    "professional": 20.0,  # Professionisti
    "agent": 23.0,  # Agenti
    "company": 4.0,  # Società
}

# Social security rates (Italy)
SOCIAL_SECURITY_RATES_IT = {
    "cassa_geometri": 4.0,
    "cassa_ingegneri": 4.0,
    "inps": 4.0,
}

# Stamp duty thresholds (Italy)
STAMP_DUTY_THRESHOLD_IT = 77.47  # EUR
STAMP_DUTY_AMOUNT_IT = 2.00  # EUR

# Invoice number pattern templates
INVOICE_NUMBER_PATTERNS = {
    "standard": "{tenant_abbr}-{year}-{seq:06d}",
    "simple": "{year}/{seq:04d}",
    "with_type": "{type_abbr}/{year}/{seq:05d}",
    "full": "{tenant_abbr}-{type_abbr}-{year}-{month:02d}-{seq:05d}",
}

# Document type abbreviations
DOCUMENT_TYPE_ABBR = {
    InvoiceType.INVOICE: "INV",
    InvoiceType.CREDIT_NOTE: "CN",
    InvoiceType.DEBIT_NOTE: "DN",
    InvoiceType.PROFORMA: "PRO",
    InvoiceType.RECEIPT: "RCP",
    InvoiceType.ADVANCE_INVOICE: "ADV",
}
