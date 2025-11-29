"""
Protocol definitions for billing system.

All protocols are database-agnostic and provider-agnostic.
User implements these protocols with their own storage/services.
"""

from typing import Protocol, Dict, Any, List, Optional
from datetime import datetime
from decimal import Decimal


class InvoiceStorage(Protocol):
    """
    Protocol for invoice data persistence.
    
    User implements this with their database (PostgreSQL, MongoDB, etc.).
    All methods require tenant_id for multi-tenant isolation.
    """
    
    async def create_invoice(
        self,
        tenant_id: str,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Create new invoice.
        
        Args:
            tenant_id: Tenant identifier
            data: Invoice data (from InvoiceCreate schema)
            
        Returns:
            Created invoice with id
        """
        ...
    
    async def get_invoice(
        self,
        tenant_id: str,
        invoice_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Get invoice by ID."""
        ...
    
    async def get_invoice_by_number(
        self,
        tenant_id: str,
        invoice_number: str,
    ) -> Optional[Dict[str, Any]]:
        """Get invoice by unique number."""
        ...
    
    async def update_invoice(
        self,
        tenant_id: str,
        invoice_id: str,
        updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update invoice fields."""
        ...
    
    async def list_invoices(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        List invoices with filters.
        
        Filters can include: status, customer_id, date_from, date_to, etc.
        """
        ...
    
    async def record_payment(
        self,
        tenant_id: str,
        invoice_id: str,
        payment_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Record payment for invoice."""
        ...
    
    async def get_payments(
        self,
        tenant_id: str,
        invoice_id: str,
    ) -> List[Dict[str, Any]]:
        """Get all payments for invoice."""
        ...
    
    async def get_last_serial_number(
        self,
        tenant_id: str,
        year: int,
        series: Optional[str] = None,
    ) -> Optional[int]:
        """Get last used serial number for tenant/year/series."""
        ...


class PDFTemplateProvider(Protocol):
    """
    Protocol for PDF generation from invoice data.
    
    User implements with Jinja2, WeasyPrint, ReportLab, etc.
    """
    
    async def render_pdf(
        self,
        invoice_data: Dict[str, Any],
        template_name: str = "default",
        language: str = "en",
    ) -> bytes:
        """
        Render invoice to PDF.
        
        Args:
            invoice_data: Complete invoice data
            template_name: Template identifier (e.g., "default", "minimal")
            language: Language code for labels
            
        Returns:
            PDF as bytes
        """
        ...
    
    async def get_available_templates(self) -> List[str]:
        """Get list of available template names."""
        ...


class EInvoiceProvider(Protocol):
    """
    Protocol for e-invoice XML generation.
    
    Supports FatturaPA (IT), PEPPOL UBL, Factur-X, etc.
    """
    
    async def generate_xml(
        self,
        invoice_data: Dict[str, Any],
        format: str = "fatturapa",
    ) -> Dict[str, Any]:
        """
        Generate e-invoice XML.
        
        Args:
            invoice_data: Complete invoice data
            format: E-invoice format (fatturapa, peppol, facturx)
            
        Returns:
            Dict with keys: xml (str), hash (str), format (str)
        """
        ...
    
    async def validate_xml(
        self,
        xml_content: str,
        format: str = "fatturapa",
    ) -> Dict[str, Any]:
        """
        Validate XML against schema.
        
        Returns:
            Dict with keys: valid (bool), errors (List[str])
        """
        ...


class SerialNumberProvider(Protocol):
    """
    Protocol for invoice numbering/sequencing.
    
    Generates unique invoice numbers per tenant.
    """
    
    async def generate_number(
        self,
        tenant_id: str,
        invoice_type: str,
        date: datetime,
        series: Optional[str] = None,
    ) -> str:
        """
        Generate unique invoice number.
        
        Args:
            tenant_id: Tenant identifier
            invoice_type: Invoice type (invoice, credit_note, etc.)
            date: Invoice date
            series: Optional series identifier
            
        Returns:
            Unique invoice number (e.g., "ACME-2025-000001")
        """
        ...
    
    async def validate_number(
        self,
        tenant_id: str,
        invoice_number: str,
    ) -> bool:
        """Check if invoice number is available/valid."""
        ...


class EmailProvider(Protocol):
    """
    Protocol for sending invoices via email.
    
    User implements with SMTP, SendGrid, AWS SES, etc.
    """
    
    async def send_invoice(
        self,
        tenant_id: str,
        invoice_id: str,
        recipient_email: str,
        subject: str,
        body: str,
        pdf_attachment: bytes,
        xml_attachment: Optional[bytes] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Send invoice via email.
        
        Returns:
            Dict with keys: sent (bool), message_id (str), timestamp (datetime)
        """
        ...


class VIESValidator(Protocol):
    """
    Protocol for VAT number validation (EU VIES system).
    
    User implements with actual API or stub.
    """
    
    async def validate_vat_number(
        self,
        vat_number: str,
        country_code: str,
    ) -> Dict[str, Any]:
        """
        Validate VAT number via VIES.
        
        Returns:
            Dict with keys: valid (bool), company_name (str), address (str)
        """
        ...


class I18nProvider(Protocol):
    """
    Protocol for internationalization.
    
    Provides translations for invoice labels, messages, etc.
    """
    
    def get_translation(
        self,
        key: str,
        language: str = "en",
        **kwargs,
    ) -> str:
        """
        Get translated string.
        
        Args:
            key: Translation key (e.g., "invoice.total")
            language: Language code
            **kwargs: Variables for string interpolation
            
        Returns:
            Translated string
        """
        ...
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported language codes."""
        ...
