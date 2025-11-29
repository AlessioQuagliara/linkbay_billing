"""
LinkBay Billing - Enterprise-grade invoicing and billing library.

Protocol-based, database-agnostic, multi-tenant billing system
for European fiscal compliance and global tax support.
"""

__version__ = "0.1.0"

# Constants and enums
from .constants import (
    InvoiceType,
    InvoiceStatus,
    PaymentStatus,
    VATRate,
    TaxType,
    DocumentLanguage,
    EInvoiceFormat,
    PaymentMethod,
    PaymentTerms,
    CurrencyCode,
)

# Exceptions
from .exceptions import (
    BillingError,
    InvoiceNotFoundError,
    InvalidInvoiceDataError,
    InvalidVATNumberError,
    SerialNumberError,
    PDFGenerationError,
    EInvoiceGenerationError,
    TaxCalculationError,
    DeliveryError,
)

# Protocols
from .protocols import (
    InvoiceStorage,
    PDFTemplateProvider,
    EInvoiceProvider,
    SerialNumberProvider,
    EmailProvider,
    VIESValidator,
    I18nProvider,
)

# Schemas
from .schemas import (
    # Core entities
    Address,
    TaxInfo,
    Company,
    Customer,
    # Invoice components
    InvoiceRow,
    TaxDetail,
    PaymentInfo,
    RetentionInfo,
    # Invoice operations
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceResponse,
    InvoiceListResponse,
    CreditNoteCreate,
    # Tax calculations
    VATSummary,
    TaxCalculationResult,
    # Payments
    PaymentRecord,
    PaymentRecordCreate,
    # Reports
    VATReport,
    OutstandingReport,
    CustomerBalance,
    # Delivery
    EmailDeliveryRequest,
    EmailDeliveryResponse,
    # E-Invoice
    EInvoiceExportRequest,
    EInvoiceExportResponse,
)

# Services
from .services import (
    InvoiceManager,
    VATCalculator,
    SerialNumberGenerator,
    ReportingService,
)

# Providers
from .providers import (
    Jinja2PDFProvider,
    FatturaPAProvider,
    PEPPOLProvider,
    SimpleEmailProvider,
)

# Router
from .router import create_billing_router

__all__ = [
    # Version
    "__version__",
    # Constants
    "InvoiceType",
    "InvoiceStatus",
    "PaymentStatus",
    "VATRate",
    "TaxType",
    "DocumentLanguage",
    "EInvoiceFormat",
    "PaymentMethod",
    "PaymentTerms",
    "CurrencyCode",
    # Exceptions
    "BillingError",
    "InvoiceNotFoundError",
    "InvalidInvoiceDataError",
    "InvalidVATNumberError",
    "SerialNumberError",
    "PDFGenerationError",
    "EInvoiceGenerationError",
    "TaxCalculationError",
    "DeliveryError",
    # Protocols
    "InvoiceStorage",
    "PDFTemplateProvider",
    "EInvoiceProvider",
    "SerialNumberProvider",
    "EmailProvider",
    "VIESValidator",
    "I18nProvider",
    # Schemas
    "Address",
    "TaxInfo",
    "Company",
    "Customer",
    "InvoiceRow",
    "TaxDetail",
    "PaymentInfo",
    "RetentionInfo",
    "InvoiceCreate",
    "InvoiceUpdate",
    "InvoiceResponse",
    "InvoiceListResponse",
    "CreditNoteCreate",
    "VATSummary",
    "TaxCalculationResult",
    "PaymentRecord",
    "PaymentRecordCreate",
    "VATReport",
    "OutstandingReport",
    "CustomerBalance",
    "EmailDeliveryRequest",
    "EmailDeliveryResponse",
    "EInvoiceExportRequest",
    "EInvoiceExportResponse",
    # Services
    "InvoiceManager",
    "VATCalculator",
    "SerialNumberGenerator",
    "ReportingService",
    # Providers
    "Jinja2PDFProvider",
    "FatturaPAProvider",
    "PEPPOLProvider",
    "SimpleEmailProvider",
    # Router
    "create_billing_router",
]
