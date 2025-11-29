"""
Custom exceptions for billing system.
"""


class BillingError(Exception):
    """Base exception for billing system."""
    
    pass


class InvoiceNotFoundError(BillingError):
    """Invoice not found in storage."""
    
    def __init__(self, tenant_id: str, invoice_id: str):
        self.tenant_id = tenant_id
        self.invoice_id = invoice_id
        super().__init__(
            f"Invoice {invoice_id} not found for tenant {tenant_id}"
        )


class InvalidInvoiceDataError(BillingError):
    """Invoice data validation failed."""
    
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"Invalid invoice data for field '{field}': {message}")


class InvalidVATNumberError(BillingError):
    """VAT number validation failed."""
    
    def __init__(self, vat_number: str, country: str):
        self.vat_number = vat_number
        self.country = country
        super().__init__(
            f"Invalid VAT number {vat_number} for country {country}"
        )


class SerialNumberError(BillingError):
    """Error generating invoice serial number."""
    
    def __init__(self, tenant_id: str, message: str):
        self.tenant_id = tenant_id
        super().__init__(f"Serial number error for tenant {tenant_id}: {message}")


class PDFGenerationError(BillingError):
    """Error generating PDF document."""
    
    def __init__(self, invoice_id: str, message: str):
        self.invoice_id = invoice_id
        super().__init__(f"PDF generation failed for invoice {invoice_id}: {message}")


class EInvoiceGenerationError(BillingError):
    """Error generating e-invoice XML."""
    
    def __init__(self, invoice_id: str, format: str, message: str):
        self.invoice_id = invoice_id
        self.format = format
        super().__init__(
            f"E-invoice generation failed for {invoice_id} ({format}): {message}"
        )


class TaxCalculationError(BillingError):
    """Error calculating taxes or VAT."""
    
    def __init__(self, message: str):
        super().__init__(f"Tax calculation error: {message}")


class DeliveryError(BillingError):
    """Error delivering invoice via email or other channel."""
    
    def __init__(self, invoice_id: str, channel: str, message: str):
        self.invoice_id = invoice_id
        self.channel = channel
        super().__init__(
            f"Delivery failed for invoice {invoice_id} via {channel}: {message}"
        )


class DuplicateInvoiceNumberError(BillingError):
    """Duplicate invoice number detected."""
    
    def __init__(self, invoice_number: str, tenant_id: str):
        self.invoice_number = invoice_number
        self.tenant_id = tenant_id
        super().__init__(
            f"Invoice number {invoice_number} already exists for tenant {tenant_id}"
        )


class InvoiceCanceledError(BillingError):
    """Operation not allowed on canceled invoice."""
    
    def __init__(self, invoice_id: str):
        self.invoice_id = invoice_id
        super().__init__(f"Invoice {invoice_id} is canceled")


class PaymentAmountError(BillingError):
    """Invalid payment amount."""
    
    def __init__(self, message: str):
        super().__init__(f"Payment amount error: {message}")
