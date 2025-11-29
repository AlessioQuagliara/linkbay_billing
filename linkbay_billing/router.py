"""
FastAPI router factory for billing endpoints.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, status
from datetime import date
from ..services import InvoiceManager, ReportingService
from ..providers import Jinja2PDFProvider, FatturaPAProvider, SimpleEmailProvider
from ..schemas import (
    InvoiceCreate,
    InvoiceUpdate,
    InvoiceResponse,
    InvoiceListResponse,
    CreditNoteCreate,
    PaymentRecordCreate,
    PaymentRecord,
    EmailDeliveryRequest,
    EmailDeliveryResponse,
    EInvoiceExportRequest,
    EInvoiceExportResponse,
    VATReport,
    OutstandingReport,
)
from ..exceptions import BillingError


def create_billing_router(
    invoice_manager: InvoiceManager,
    reporting_service: ReportingService,
    pdf_provider: Optional[Jinja2PDFProvider] = None,
    einvoice_provider: Optional[FatturaPAProvider] = None,
    email_provider: Optional[SimpleEmailProvider] = None,
    prefix: str = "/billing",
) -> APIRouter:
    """
    Create FastAPI router for billing endpoints.
    
    Args:
        invoice_manager: InvoiceManager instance
        reporting_service: ReportingService instance
        pdf_provider: PDF generation provider
        einvoice_provider: E-invoice generation provider
        email_provider: Email delivery provider
        prefix: URL prefix
        
    Returns:
        Configured APIRouter
        
    Example:
        ```python
        from fastapi import FastAPI
        from linkbay_billing import (
            InvoiceManager,
            ReportingService,
            create_billing_router,
        )
        
        app = FastAPI()
        
        manager = InvoiceManager(storage, serial_provider)
        reporting = ReportingService(storage)
        
        router = create_billing_router(manager, reporting)
        app.include_router(router)
        ```
    """
    router = APIRouter(prefix=prefix, tags=["billing"])
    
    @router.post(
        "/{tenant_id}/invoices",
        response_model=InvoiceResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def create_invoice(
        tenant_id: str,
        invoice_data: InvoiceCreate,
    ):
        """Create new invoice."""
        try:
            return await invoice_manager.create_invoice(tenant_id, invoice_data)
        except BillingError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @router.get("/{tenant_id}/invoices/{invoice_id}", response_model=InvoiceResponse)
    async def get_invoice(tenant_id: str, invoice_id: str):
        """Get invoice by ID."""
        try:
            return await invoice_manager.get_invoice(tenant_id, invoice_id)
        except BillingError as e:
            raise HTTPException(status_code=404, detail=str(e))
    
    @router.get("/{tenant_id}/invoices", response_model=InvoiceListResponse)
    async def list_invoices(
        tenant_id: str,
        skip: int = 0,
        limit: int = 100,
    ):
        """List invoices."""
        invoices = await invoice_manager.list_invoices(tenant_id, skip, limit)
        return InvoiceListResponse(
            invoices=invoices,
            total=len(invoices),
            skip=skip,
            limit=limit,
        )
    
    @router.put("/{tenant_id}/invoices/{invoice_id}", response_model=InvoiceResponse)
    async def update_invoice(
        tenant_id: str,
        invoice_id: str,
        updates: InvoiceUpdate,
    ):
        """Update invoice."""
        try:
            return await invoice_manager.update_invoice(tenant_id, invoice_id, updates)
        except BillingError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @router.delete("/{tenant_id}/invoices/{invoice_id}", response_model=InvoiceResponse)
    async def cancel_invoice(
        tenant_id: str,
        invoice_id: str,
        reason: Optional[str] = None,
    ):
        """Cancel invoice."""
        try:
            return await invoice_manager.cancel_invoice(tenant_id, invoice_id, reason)
        except BillingError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @router.post("/{tenant_id}/credit-notes", response_model=InvoiceResponse)
    async def create_credit_note(
        tenant_id: str,
        credit_note_data: CreditNoteCreate,
    ):
        """Create credit note."""
        try:
            return await invoice_manager.create_credit_note(tenant_id, credit_note_data)
        except BillingError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @router.post(
        "/{tenant_id}/invoices/{invoice_id}/payments",
        response_model=PaymentRecord,
    )
    async def record_payment(
        tenant_id: str,
        invoice_id: str,
        payment_data: PaymentRecordCreate,
    ):
        """Record payment for invoice."""
        try:
            return await invoice_manager.record_payment(
                tenant_id, invoice_id, payment_data
            )
        except BillingError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @router.get("/{tenant_id}/invoices/{invoice_id}/pdf")
    async def download_pdf(tenant_id: str, invoice_id: str):
        """Download invoice as PDF."""
        if not pdf_provider:
            raise HTTPException(status_code=501, detail="PDF generation not configured")
        
        try:
            invoice = await invoice_manager.get_invoice(tenant_id, invoice_id)
            pdf_bytes = await pdf_provider.render_pdf(
                invoice.model_dump(),
                language=invoice.language,
            )
            
            from fastapi.responses import Response
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": f"attachment; filename=invoice_{invoice.invoice_number}.pdf"
                },
            )
        except BillingError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @router.post(
        "/{tenant_id}/invoices/{invoice_id}/xml",
        response_model=EInvoiceExportResponse,
    )
    async def export_einvoice(
        tenant_id: str,
        invoice_id: str,
        request: EInvoiceExportRequest,
    ):
        """Export invoice to e-invoice XML format."""
        if not einvoice_provider:
            raise HTTPException(
                status_code=501, detail="E-invoice generation not configured"
            )
        
        try:
            invoice = await invoice_manager.get_invoice(tenant_id, invoice_id)
            result = await einvoice_provider.generate_xml(
                invoice.model_dump(), format=request.format
            )
            
            validation = {"valid": True, "errors": []}
            if request.validate:
                validation = await einvoice_provider.validate_xml(
                    result["xml"], format=request.format
                )
            
            from datetime import datetime
            return EInvoiceExportResponse(
                format=result["format"],
                xml=result["xml"],
                hash=result.get("hash"),
                valid=validation["valid"],
                validation_errors=validation.get("errors"),
                generated_at=datetime.utcnow(),
            )
        except BillingError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @router.post(
        "/{tenant_id}/invoices/{invoice_id}/send",
        response_model=EmailDeliveryResponse,
    )
    async def send_invoice_email(
        tenant_id: str,
        invoice_id: str,
        delivery_request: EmailDeliveryRequest,
    ):
        """Send invoice via email."""
        if not email_provider or not pdf_provider:
            raise HTTPException(
                status_code=501, detail="Email delivery not configured"
            )
        
        try:
            invoice = await invoice_manager.get_invoice(tenant_id, invoice_id)
            
            # Generate PDF
            pdf_bytes = await pdf_provider.render_pdf(
                invoice.model_dump(),
                language=delivery_request.language,
            )
            
            # Generate XML if requested
            xml_bytes = None
            if delivery_request.include_xml and einvoice_provider:
                result = await einvoice_provider.generate_xml(invoice.model_dump())
                xml_bytes = result["xml"].encode("utf-8")
            
            # Send email
            result = await email_provider.send_invoice(
                tenant_id=tenant_id,
                invoice_id=invoice_id,
                recipient_email=delivery_request.recipient_email,
                subject=delivery_request.subject
                or f"Invoice {invoice.invoice_number}",
                body=delivery_request.body or "Please find your invoice attached.",
                pdf_attachment=pdf_bytes,
                xml_attachment=xml_bytes,
                cc=delivery_request.cc,
                bcc=delivery_request.bcc,
            )
            
            # Mark as sent
            await invoice_manager.mark_as_sent(tenant_id, invoice_id)
            
            return EmailDeliveryResponse(**result)
        except BillingError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @router.get("/{tenant_id}/reports/vat", response_model=VATReport)
    async def get_vat_report(
        tenant_id: str,
        period_start: date,
        period_end: date,
    ):
        """Generate VAT report for period."""
        try:
            return await reporting_service.generate_vat_report(
                tenant_id, period_start, period_end
            )
        except BillingError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    @router.get("/{tenant_id}/reports/outstanding", response_model=OutstandingReport)
    async def get_outstanding_report(tenant_id: str):
        """Generate outstanding invoices report."""
        try:
            return await reporting_service.generate_outstanding_report(tenant_id)
        except BillingError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    return router
