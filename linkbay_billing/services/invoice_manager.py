"""
Invoice management service.

Core service for creating, updating, and managing invoices.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, date
from decimal import Decimal
from ..protocols import InvoiceStorage, SerialNumberProvider, I18nProvider
from ..schemas import (
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceResponse,
    CreditNoteCreate,
    PaymentRecordCreate,
    PaymentRecord,
)
from ..constants import InvoiceType, InvoiceStatus, PaymentStatus
from ..exceptions import (
    InvoiceNotFoundError,
    InvalidInvoiceDataError,
    InvoiceCanceledError,
    PaymentAmountError,
)
from .vat_calculator import VATCalculator


class InvoiceManager:
    """
    Main service for invoice operations.
    
    Handles invoice creation, updates, cancellation, payments.
    All operations are tenant-isolated.
    """
    
    def __init__(
        self,
        storage: InvoiceStorage,
        serial_provider: SerialNumberProvider,
        vat_calculator: Optional[VATCalculator] = None,
        i18n_provider: Optional[I18nProvider] = None,
    ):
        """
        Initialize invoice manager.
        
        Args:
            storage: Invoice storage implementation
            serial_provider: Serial number generator
            vat_calculator: VAT calculation service
            i18n_provider: Internationalization provider
        """
        self.storage = storage
        self.serial_provider = serial_provider
        self.vat_calculator = vat_calculator or VATCalculator()
        self.i18n_provider = i18n_provider
    
    async def create_invoice(
        self,
        tenant_id: str,
        invoice_data: InvoiceCreate,
    ) -> InvoiceResponse:
        """
        Create and issue new invoice.
        
        Args:
            tenant_id: Tenant identifier
            invoice_data: Invoice creation data
            
        Returns:
            Created invoice
            
        Example:
            ```python
            invoice = await manager.create_invoice(
                tenant_id="agency123",
                invoice_data=InvoiceCreate(
                    company=company,
                    customer=customer,
                    rows=[
                        InvoiceRow(
                            description="Web Design",
                            quantity=Decimal("10"),
                            unit_price=Decimal("100"),
                            vat_rate=Decimal("22"),
                        ),
                    ],
                    issue_date=date.today(),
                    payment_info=PaymentInfo(
                        method="bank_transfer",
                        terms="net_30",
                    ),
                ),
            )
            ```
        """
        # Generate invoice number
        invoice_number = await self.serial_provider.generate_number(
            tenant_id=tenant_id,
            invoice_type=invoice_data.invoice_type,
            date=datetime.combine(invoice_data.issue_date, datetime.min.time()),
            series=invoice_data.series,
        )
        
        # Calculate taxes
        tax_result = self.vat_calculator.calculate(
            rows=invoice_data.rows,
            retention=invoice_data.retention,
            social_security_rate=invoice_data.social_security_rate,
            stamp_duty=invoice_data.stamp_duty,
            split_payment=invoice_data.split_payment,
        )
        
        # Prepare invoice data
        invoice_dict = {
            "invoice_number": invoice_number,
            "invoice_type": invoice_data.invoice_type,
            "status": InvoiceStatus.ISSUED.value,
            "company": invoice_data.company.model_dump(),
            "customer": invoice_data.customer.model_dump(),
            "rows": [row.model_dump() for row in invoice_data.rows],
            "issue_date": invoice_data.issue_date,
            "payment_info": invoice_data.payment_info.model_dump(),
            "subtotal": tax_result.subtotal,
            "total_vat": tax_result.total_vat,
            "total": tax_result.total,
            "net_to_pay": tax_result.net_to_pay,
            "retention": invoice_data.retention.model_dump() if invoice_data.retention else None,
            "social_security_amount": tax_result.social_security_amount,
            "stamp_duty_amount": tax_result.stamp_duty_amount,
            "split_payment": invoice_data.split_payment,
            "reverse_charge": invoice_data.reverse_charge,
            "notes": invoice_data.notes,
            "currency": invoice_data.currency,
            "language": invoice_data.language,
            "series": invoice_data.series,
            "metadata": invoice_data.metadata or {},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        # Store invoice
        created = await self.storage.create_invoice(tenant_id, invoice_dict)
        
        return InvoiceResponse(**created)
    
    async def get_invoice(
        self,
        tenant_id: str,
        invoice_id: str,
    ) -> InvoiceResponse:
        """Get invoice by ID."""
        invoice = await self.storage.get_invoice(tenant_id, invoice_id)
        
        if not invoice:
            raise InvoiceNotFoundError(tenant_id, invoice_id)
        
        return InvoiceResponse(**invoice)
    
    async def get_invoice_by_number(
        self,
        tenant_id: str,
        invoice_number: str,
    ) -> InvoiceResponse:
        """Get invoice by unique number."""
        invoice = await self.storage.get_invoice_by_number(tenant_id, invoice_number)
        
        if not invoice:
            raise InvoiceNotFoundError(tenant_id, invoice_number)
        
        return InvoiceResponse(**invoice)
    
    async def update_invoice(
        self,
        tenant_id: str,
        invoice_id: str,
        updates: InvoiceUpdate,
    ) -> InvoiceResponse:
        """Update invoice fields."""
        invoice = await self.get_invoice(tenant_id, invoice_id)
        
        if invoice.status == InvoiceStatus.CANCELED.value:
            raise InvoiceCanceledError(invoice_id)
        
        update_dict = updates.model_dump(exclude_unset=True)
        update_dict["updated_at"] = datetime.utcnow()
        
        updated = await self.storage.update_invoice(tenant_id, invoice_id, update_dict)
        return InvoiceResponse(**updated)
    
    async def list_invoices(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[InvoiceResponse]:
        """List invoices with filters."""
        invoices = await self.storage.list_invoices(
            tenant_id, skip, limit, filters
        )
        return [InvoiceResponse(**inv) for inv in invoices]
    
    async def cancel_invoice(
        self,
        tenant_id: str,
        invoice_id: str,
        reason: Optional[str] = None,
    ) -> InvoiceResponse:
        """
        Cancel invoice.
        
        Args:
            tenant_id: Tenant identifier
            invoice_id: Invoice ID
            reason: Cancellation reason
        """
        invoice = await self.get_invoice(tenant_id, invoice_id)
        
        if invoice.status == InvoiceStatus.PAID.value:
            raise InvalidInvoiceDataError(
                "status", "Cannot cancel paid invoice. Issue credit note instead."
            )
        
        updates = {
            "status": InvoiceStatus.CANCELED.value,
            "metadata": {
                **invoice.metadata,
                "cancellation_reason": reason,
                "canceled_at": datetime.utcnow().isoformat(),
            },
            "updated_at": datetime.utcnow(),
        }
        
        updated = await self.storage.update_invoice(tenant_id, invoice_id, updates)
        return InvoiceResponse(**updated)
    
    async def create_credit_note(
        self,
        tenant_id: str,
        credit_note_data: CreditNoteCreate,
    ) -> InvoiceResponse:
        """
        Create credit note for original invoice.
        
        Args:
            tenant_id: Tenant identifier
            credit_note_data: Credit note creation data
            
        Returns:
            Created credit note
        """
        # Get original invoice
        original = await self.get_invoice(
            tenant_id, credit_note_data.original_invoice_id
        )
        
        # Use original rows or provided rows
        rows = credit_note_data.rows if credit_note_data.rows else original.rows
        
        # Create credit note as negative invoice
        credit_note = InvoiceCreate(
            invoice_type=InvoiceType.CREDIT_NOTE.value,
            company=original.company,
            customer=original.customer,
            rows=rows,
            issue_date=credit_note_data.issue_date,
            payment_info=original.payment_info,
            notes=credit_note_data.notes,
            currency=original.currency,
            language=original.language,
            retention=original.retention,
            split_payment=original.split_payment,
            reverse_charge=original.reverse_charge,
            metadata={
                "original_invoice_id": original.id,
                "original_invoice_number": original.invoice_number,
                "credit_reason": credit_note_data.reason,
            },
        )
        
        return await self.create_invoice(tenant_id, credit_note)
    
    async def record_payment(
        self,
        tenant_id: str,
        invoice_id: str,
        payment_data: PaymentRecordCreate,
    ) -> PaymentRecord:
        """
        Record payment for invoice.
        
        Updates invoice status based on total paid amount.
        """
        invoice = await self.get_invoice(tenant_id, invoice_id)
        
        if payment_data.amount > invoice.net_to_pay:
            raise PaymentAmountError(
                f"Payment amount {payment_data.amount} exceeds invoice total {invoice.net_to_pay}"
            )
        
        # Record payment
        payment_dict = {
            **payment_data.model_dump(),
            "invoice_id": invoice_id,
            "created_at": datetime.utcnow(),
        }
        
        payment = await self.storage.record_payment(
            tenant_id, invoice_id, payment_dict
        )
        
        # Get all payments
        payments = await self.storage.get_payments(tenant_id, invoice_id)
        total_paid = sum(Decimal(p["amount"]) for p in payments)
        
        # Update invoice status
        if total_paid >= invoice.net_to_pay:
            status = InvoiceStatus.PAID.value
            paid_at = datetime.utcnow()
        elif total_paid > 0:
            status = InvoiceStatus.PARTIALLY_PAID.value
            paid_at = None
        else:
            status = invoice.status
            paid_at = None
        
        await self.storage.update_invoice(
            tenant_id,
            invoice_id,
            {
                "status": status,
                "paid_at": paid_at,
                "updated_at": datetime.utcnow(),
            },
        )
        
        return PaymentRecord(**payment)
    
    async def mark_as_sent(
        self,
        tenant_id: str,
        invoice_id: str,
    ) -> InvoiceResponse:
        """Mark invoice as sent to customer."""
        updates = {
            "status": InvoiceStatus.SENT.value,
            "sent_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        updated = await self.storage.update_invoice(tenant_id, invoice_id, updates)
        return InvoiceResponse(**updated)
