"""
Serial number generation service.
"""

from typing import Optional
from datetime import datetime
from ..protocols import InvoiceStorage
from ..constants import INVOICE_NUMBER_PATTERNS, DOCUMENT_TYPE_ABBR
from ..exceptions import SerialNumberError


class SerialNumberGenerator:
    """
    Service for generating unique invoice numbers.
    
    Supports customizable patterns per tenant.
    """
    
    def __init__(
        self,
        storage: InvoiceStorage,
        pattern: str = "standard",
        tenant_abbr_resolver: Optional[callable] = None,
    ):
        """
        Initialize serial number generator.
        
        Args:
            storage: Invoice storage for retrieving last serial
            pattern: Pattern key from INVOICE_NUMBER_PATTERNS
            tenant_abbr_resolver: Function to get tenant abbreviation
        """
        self.storage = storage
        self.pattern = INVOICE_NUMBER_PATTERNS.get(pattern, pattern)
        self.tenant_abbr_resolver = tenant_abbr_resolver
    
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
            Unique invoice number
            
        Example:
            ```python
            generator = SerialNumberGenerator(storage, pattern="standard")
            
            number = await generator.generate_number(
                tenant_id="agency123",
                invoice_type="invoice",
                date=datetime.now(),
            )
            # Result: "ACME-2025-000001"
            ```
        """
        year = date.year
        month = date.month
        
        # Get last serial number for this tenant/year/series
        last_serial = await self.storage.get_last_serial_number(
            tenant_id, year, series
        )
        
        next_serial = (last_serial or 0) + 1
        
        # Get tenant abbreviation
        tenant_abbr = "TENANT"
        if self.tenant_abbr_resolver:
            tenant_abbr = self.tenant_abbr_resolver(tenant_id)
        
        # Get document type abbreviation
        type_abbr = DOCUMENT_TYPE_ABBR.get(invoice_type, "DOC")
        
        # Format invoice number
        try:
            invoice_number = self.pattern.format(
                tenant_abbr=tenant_abbr,
                type_abbr=type_abbr,
                year=year,
                month=month,
                seq=next_serial,
                series=series or "",
            )
        except KeyError as e:
            raise SerialNumberError(
                tenant_id,
                f"Invalid pattern: missing key {e}",
            )
        
        return invoice_number
    
    async def validate_number(
        self,
        tenant_id: str,
        invoice_number: str,
    ) -> bool:
        """Check if invoice number is available."""
        existing = await self.storage.get_invoice_by_number(
            tenant_id, invoice_number
        )
        return existing is None
