"""
Reporting service for VAT and financial reports.
"""

from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
from ..protocols import InvoiceStorage
from ..schemas import VATReport, OutstandingReport, CustomerBalance, VATSummary
from ..constants import InvoiceStatus


class ReportingService:
    """
    Service for generating financial and tax reports.
    
    Supports:
    - VAT reports by period
    - Outstanding invoices report
    - Customer balance report
    """
    
    def __init__(self, storage: InvoiceStorage):
        """
        Initialize reporting service.
        
        Args:
            storage: Invoice storage implementation
        """
        self.storage = storage
    
    async def generate_vat_report(
        self,
        tenant_id: str,
        period_start: date,
        period_end: date,
    ) -> VATReport:
        """
        Generate VAT report for period.
        
        Args:
            tenant_id: Tenant identifier
            period_start: Report period start
            period_end: Report period end
            
        Returns:
            VAT report with totals by rate
            
        Example:
            ```python
            reporting = ReportingService(storage)
            
            report = await reporting.generate_vat_report(
                tenant_id="agency123",
                period_start=date(2025, 1, 1),
                period_end=date(2025, 3, 31),
            )
            ```
        """
        # Get all invoices in period
        invoices = await self.storage.list_invoices(
            tenant_id,
            filters={
                "issue_date_from": period_start,
                "issue_date_to": period_end,
                "status_not": InvoiceStatus.CANCELED.value,
            },
        )
        
        # Calculate totals
        total_invoices = len(invoices)
        total_taxable = Decimal("0")
        total_vat = Decimal("0")
        total_gross = Decimal("0")
        vat_by_rate = {}
        
        for invoice in invoices:
            subtotal = Decimal(str(invoice.get("subtotal", 0)))
            vat = Decimal(str(invoice.get("total_vat", 0)))
            total = Decimal(str(invoice.get("total", 0)))
            
            total_taxable += subtotal
            total_vat += vat
            total_gross += total
            
            # Group by VAT rate
            for row in invoice.get("rows", []):
                rate = Decimal(str(row.get("vat_rate", 0)))
                row_subtotal = Decimal(str(row.get("quantity", 1))) * Decimal(
                    str(row.get("unit_price", 0))
                )
                
                if rate not in vat_by_rate:
                    vat_by_rate[rate] = {
                        "taxable": Decimal("0"),
                        "vat": Decimal("0"),
                    }
                
                vat_by_rate[rate]["taxable"] += row_subtotal
                vat_by_rate[rate]["vat"] += (row_subtotal * rate / 100).quantize(
                    Decimal("0.01")
                )
        
        # Build VAT summaries
        vat_summaries = [
            VATSummary(
                vat_rate=rate,
                taxable_amount=data["taxable"],
                vat_amount=data["vat"],
            )
            for rate, data in vat_by_rate.items()
        ]
        
        return VATReport(
            tenant_id=tenant_id,
            period_start=period_start,
            period_end=period_end,
            total_invoices=total_invoices,
            total_taxable=total_taxable,
            total_vat=total_vat,
            total_gross=total_gross,
            vat_by_rate=vat_summaries,
            generated_at=datetime.utcnow(),
        )
    
    async def generate_outstanding_report(
        self,
        tenant_id: str,
    ) -> OutstandingReport:
        """
        Generate report of outstanding invoices.
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            Outstanding invoices by customer
        """
        # Get unpaid and partially paid invoices
        invoices = await self.storage.list_invoices(
            tenant_id,
            filters={
                "status_in": [
                    InvoiceStatus.ISSUED.value,
                    InvoiceStatus.SENT.value,
                    InvoiceStatus.PARTIALLY_PAID.value,
                    InvoiceStatus.OVERDUE.value,
                ],
            },
        )
        
        # Group by customer
        customer_balances = {}
        total_outstanding = Decimal("0")
        total_overdue = Decimal("0")
        
        for invoice in invoices:
            customer_id = invoice["customer"]["id"]
            customer_name = invoice["customer"]["name"]
            net_to_pay = Decimal(str(invoice.get("net_to_pay", 0)))
            
            # Get payments
            payments = await self.storage.get_payments(tenant_id, invoice["id"])
            total_paid = sum(Decimal(str(p["amount"])) for p in payments)
            outstanding = net_to_pay - total_paid
            
            if customer_id not in customer_balances:
                customer_balances[customer_id] = {
                    "customer_id": customer_id,
                    "customer_name": customer_name,
                    "total_invoiced": Decimal("0"),
                    "total_paid": Decimal("0"),
                    "total_outstanding": Decimal("0"),
                    "overdue_amount": Decimal("0"),
                    "invoice_count": 0,
                }
            
            customer_balances[customer_id]["total_invoiced"] += net_to_pay
            customer_balances[customer_id]["total_paid"] += total_paid
            customer_balances[customer_id]["total_outstanding"] += outstanding
            customer_balances[customer_id]["invoice_count"] += 1
            
            total_outstanding += outstanding
            
            # Check if overdue
            if invoice["status"] == InvoiceStatus.OVERDUE.value:
                customer_balances[customer_id]["overdue_amount"] += outstanding
                total_overdue += outstanding
        
        # Build customer balance list
        by_customer = [
            CustomerBalance(**data) for data in customer_balances.values()
        ]
        
        return OutstandingReport(
            tenant_id=tenant_id,
            total_outstanding=total_outstanding,
            total_overdue=total_overdue,
            by_customer=by_customer,
            generated_at=datetime.utcnow(),
        )
