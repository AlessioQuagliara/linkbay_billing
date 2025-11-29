"""
Pydantic schemas for billing system.

All DTOs for invoice creation, tax calculations, reports, etc.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field, EmailStr, field_validator


# Base entities

class Address(BaseModel):
    """Physical address."""
    
    street: str
    city: str
    postal_code: str
    state_province: Optional[str] = None
    country: str  # ISO 3166-1 alpha-2
    
    class Config:
        json_schema_extra = {
            "example": {
                "street": "Via Roma 123",
                "city": "Milano",
                "postal_code": "20100",
                "country": "IT",
            }
        }


class TaxInfo(BaseModel):
    """Tax identification info."""
    
    vat_number: Optional[str] = None
    tax_code: Optional[str] = None  # Codice fiscale (IT)
    sdi_code: Optional[str] = None  # SDI code for e-invoice (IT)
    pec_email: Optional[EmailStr] = None  # PEC email (IT)
    
    class Config:
        json_schema_extra = {
            "example": {
                "vat_number": "IT12345678901",
                "tax_code": "RSSMRA80A01H501U",
                "sdi_code": "A1B2C3D",
            }
        }


class Company(BaseModel):
    """Company/issuer details."""
    
    name: str
    legal_name: Optional[str] = None
    address: Address
    tax_info: TaxInfo
    email: EmailStr
    phone: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "ACME Agency",
                "legal_name": "ACME S.r.l.",
                "address": {
                    "street": "Via Milano 1",
                    "city": "Roma",
                    "postal_code": "00100",
                    "country": "IT",
                },
                "tax_info": {
                    "vat_number": "IT12345678901",
                },
                "email": "info@acme.com",
            }
        }


class Customer(BaseModel):
    """Customer/buyer details."""
    
    id: str
    name: str
    legal_name: Optional[str] = None
    address: Address
    tax_info: Optional[TaxInfo] = None
    email: EmailStr
    phone: Optional[str] = None
    is_company: bool = False
    payment_terms: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "cust_123",
                "name": "Cliente SPA",
                "address": {
                    "street": "Corso Italia 50",
                    "city": "Milano",
                    "postal_code": "20100",
                    "country": "IT",
                },
                "tax_info": {
                    "vat_number": "IT98765432109",
                },
                "email": "cliente@example.com",
                "is_company": True,
            }
        }


# Invoice components

class InvoiceRow(BaseModel):
    """Invoice line item."""
    
    description: str
    quantity: Decimal = Field(ge=0)
    unit_price: Decimal
    vat_rate: Decimal = Field(ge=0, le=100)
    discount_percent: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    unit: Optional[str] = "unit"
    product_code: Optional[str] = None
    
    def calculate_subtotal(self) -> Decimal:
        """Calculate row subtotal before VAT."""
        subtotal = self.quantity * self.unit_price
        if self.discount_percent > 0:
            subtotal = subtotal * (1 - self.discount_percent / 100)
        return subtotal.quantize(Decimal("0.01"))
    
    def calculate_vat(self) -> Decimal:
        """Calculate VAT amount for row."""
        subtotal = self.calculate_subtotal()
        return (subtotal * self.vat_rate / 100).quantize(Decimal("0.01"))
    
    def calculate_total(self) -> Decimal:
        """Calculate row total with VAT."""
        return (self.calculate_subtotal() + self.calculate_vat()).quantize(Decimal("0.01"))
    
    class Config:
        json_schema_extra = {
            "example": {
                "description": "Web Design Service",
                "quantity": "10",
                "unit_price": "100.00",
                "vat_rate": "22",
                "unit": "hours",
            }
        }


class TaxDetail(BaseModel):
    """Tax detail for summary."""
    
    rate: Decimal
    taxable_amount: Decimal
    tax_amount: Decimal
    
    class Config:
        json_schema_extra = {
            "example": {
                "rate": "22",
                "taxable_amount": "1000.00",
                "tax_amount": "220.00",
            }
        }


class RetentionInfo(BaseModel):
    """Retention/withholding info."""
    
    rate: Decimal = Field(ge=0, le=100)
    amount: Decimal
    reason: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "rate": "20",
                "amount": "200.00",
                "reason": "Ritenuta d'acconto professionale",
            }
        }


class PaymentInfo(BaseModel):
    """Payment terms and bank details."""
    
    method: str
    terms: str
    due_date: Optional[date] = None
    bank_name: Optional[str] = None
    iban: Optional[str] = None
    swift_bic: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "method": "bank_transfer",
                "terms": "net_30",
                "due_date": "2025-01-26",
                "bank_name": "Intesa Sanpaolo",
                "iban": "IT60X0542811101000000123456",
            }
        }


# Invoice operations

class InvoiceCreate(BaseModel):
    """Create invoice request."""
    
    invoice_type: str = "invoice"
    company: Company
    customer: Customer
    rows: List[InvoiceRow] = Field(min_length=1)
    issue_date: date
    payment_info: PaymentInfo
    notes: Optional[str] = None
    currency: str = "EUR"
    language: str = "en"
    retention: Optional[RetentionInfo] = None
    social_security_rate: Optional[Decimal] = None
    stamp_duty: bool = False
    split_payment: bool = False  # Scissione pagamenti (IT)
    reverse_charge: bool = False
    series: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class InvoiceUpdate(BaseModel):
    """Update invoice fields."""
    
    status: Optional[str] = None
    notes: Optional[str] = None
    payment_info: Optional[PaymentInfo] = None
    metadata: Optional[Dict[str, Any]] = None


class InvoiceResponse(BaseModel):
    """Invoice response with all data."""
    
    id: str
    tenant_id: str
    invoice_number: str
    invoice_type: str
    status: str
    company: Company
    customer: Customer
    rows: List[InvoiceRow]
    issue_date: date
    payment_info: PaymentInfo
    
    # Calculated fields
    subtotal: Decimal
    total_vat: Decimal
    total: Decimal
    net_to_pay: Decimal  # After retention
    
    # Optional
    retention: Optional[RetentionInfo] = None
    social_security_amount: Optional[Decimal] = None
    stamp_duty_amount: Optional[Decimal] = None
    split_payment: bool = False
    reverse_charge: bool = False
    
    notes: Optional[str] = None
    currency: str = "EUR"
    language: str = "en"
    series: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    sent_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None


class InvoiceListResponse(BaseModel):
    """List invoices response."""
    
    invoices: List[InvoiceResponse]
    total: int
    skip: int
    limit: int


class CreditNoteCreate(BaseModel):
    """Create credit note request."""
    
    original_invoice_id: str
    reason: str
    rows: Optional[List[InvoiceRow]] = None  # If None, credit full invoice
    issue_date: date
    notes: Optional[str] = None


# Tax calculations

class VATSummary(BaseModel):
    """VAT summary by rate."""
    
    vat_rate: Decimal
    taxable_amount: Decimal
    vat_amount: Decimal


class TaxCalculationResult(BaseModel):
    """Result of tax calculation."""
    
    subtotal: Decimal
    vat_summaries: List[VATSummary]
    total_vat: Decimal
    retention_amount: Optional[Decimal] = None
    social_security_amount: Optional[Decimal] = None
    stamp_duty_amount: Optional[Decimal] = None
    total: Decimal
    net_to_pay: Decimal


# Payments

class PaymentRecordCreate(BaseModel):
    """Record payment."""
    
    amount: Decimal = Field(gt=0)
    payment_date: date
    payment_method: str
    transaction_id: Optional[str] = None
    notes: Optional[str] = None


class PaymentRecord(BaseModel):
    """Payment record response."""
    
    id: str
    invoice_id: str
    amount: Decimal
    payment_date: date
    payment_method: str
    transaction_id: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime


# Reports

class VATReport(BaseModel):
    """VAT report for period."""
    
    tenant_id: str
    period_start: date
    period_end: date
    total_invoices: int
    total_taxable: Decimal
    total_vat: Decimal
    total_gross: Decimal
    vat_by_rate: List[VATSummary]
    generated_at: datetime


class CustomerBalance(BaseModel):
    """Customer outstanding balance."""
    
    customer_id: str
    customer_name: str
    total_invoiced: Decimal
    total_paid: Decimal
    total_outstanding: Decimal
    overdue_amount: Decimal
    invoice_count: int


class OutstandingReport(BaseModel):
    """Outstanding invoices report."""
    
    tenant_id: str
    total_outstanding: Decimal
    total_overdue: Decimal
    by_customer: List[CustomerBalance]
    generated_at: datetime


# Delivery

class EmailDeliveryRequest(BaseModel):
    """Send invoice via email."""
    
    recipient_email: EmailStr
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    include_xml: bool = False
    language: str = "en"


class EmailDeliveryResponse(BaseModel):
    """Email delivery result."""
    
    sent: bool
    message_id: Optional[str] = None
    timestamp: datetime
    error: Optional[str] = None


# E-Invoice

class EInvoiceExportRequest(BaseModel):
    """Export invoice to e-invoice format."""
    
    format: str = "fatturapa"  # fatturapa, peppol, facturx
    validate: bool = True


class EInvoiceExportResponse(BaseModel):
    """E-invoice export result."""
    
    format: str
    xml: str
    hash: Optional[str] = None
    valid: bool
    validation_errors: Optional[List[str]] = None
    generated_at: datetime
