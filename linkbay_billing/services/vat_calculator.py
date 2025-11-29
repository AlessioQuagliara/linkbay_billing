"""
VAT and tax calculation service.
"""

from typing import List, Optional
from decimal import Decimal
from ..schemas import InvoiceRow, RetentionInfo, VATSummary, TaxCalculationResult
from ..constants import STAMP_DUTY_THRESHOLD_IT, STAMP_DUTY_AMOUNT_IT


class VATCalculator:
    """
    Service for calculating VAT, retention, and other taxes.
    
    Supports:
    - Multi-rate VAT calculation
    - VAT summary by rate
    - Retention (ritenuta d'acconto)
    - Social security contributions
    - Stamp duty
    - Split payment
    - Reverse charge
    """
    
    def calculate(
        self,
        rows: List[InvoiceRow],
        retention: Optional[RetentionInfo] = None,
        social_security_rate: Optional[Decimal] = None,
        stamp_duty: bool = False,
        split_payment: bool = False,
    ) -> TaxCalculationResult:
        """
        Calculate all taxes for invoice.
        
        Args:
            rows: Invoice line items
            retention: Retention info
            social_security_rate: Social security rate percentage
            stamp_duty: Apply stamp duty (Italy)
            split_payment: Split payment mode (Italy)
            
        Returns:
            Complete tax calculation result
            
        Example:
            ```python
            calculator = VATCalculator()
            result = calculator.calculate(
                rows=[
                    InvoiceRow(
                        description="Service A",
                        quantity=Decimal("10"),
                        unit_price=Decimal("100"),
                        vat_rate=Decimal("22"),
                    ),
                    InvoiceRow(
                        description="Service B",
                        quantity=Decimal("5"),
                        unit_price=Decimal("50"),
                        vat_rate=Decimal("10"),
                    ),
                ],
                retention=RetentionInfo(
                    rate=Decimal("20"),
                    amount=Decimal("240"),
                ),
                stamp_duty=True,
            )
            ```
        """
        # Calculate subtotal and group by VAT rate
        subtotal = Decimal("0")
        vat_groups = {}
        
        for row in rows:
            row_subtotal = row.calculate_subtotal()
            subtotal += row_subtotal
            
            vat_rate = row.vat_rate
            if vat_rate not in vat_groups:
                vat_groups[vat_rate] = Decimal("0")
            vat_groups[vat_rate] += row_subtotal
        
        # Calculate social security
        social_security_amount = None
        if social_security_rate:
            social_security_amount = (
                subtotal * social_security_rate / 100
            ).quantize(Decimal("0.01"))
            subtotal += social_security_amount
        
        # Calculate VAT summaries
        vat_summaries = []
        total_vat = Decimal("0")
        
        for rate, taxable in vat_groups.items():
            if split_payment and rate > 0:
                # Split payment: VAT calculated but not charged
                vat_amount = Decimal("0")
            else:
                vat_amount = (taxable * rate / 100).quantize(Decimal("0.01"))
            
            total_vat += vat_amount
            vat_summaries.append(
                VATSummary(
                    vat_rate=rate,
                    taxable_amount=taxable,
                    vat_amount=vat_amount,
                )
            )
        
        # Calculate total
        total = subtotal + total_vat
        
        # Calculate stamp duty (Italy)
        stamp_duty_amount = None
        if stamp_duty and total < STAMP_DUTY_THRESHOLD_IT:
            stamp_duty_amount = STAMP_DUTY_AMOUNT_IT
            total += stamp_duty_amount
        
        # Calculate retention
        retention_amount = None
        if retention:
            retention_amount = retention.amount
        
        # Calculate net to pay
        net_to_pay = total
        if retention_amount:
            net_to_pay -= retention_amount
        
        return TaxCalculationResult(
            subtotal=subtotal,
            vat_summaries=vat_summaries,
            total_vat=total_vat,
            retention_amount=retention_amount,
            social_security_amount=social_security_amount,
            stamp_duty_amount=stamp_duty_amount,
            total=total,
            net_to_pay=net_to_pay,
        )
    
    def calculate_retention(
        self,
        taxable_amount: Decimal,
        rate: Decimal,
    ) -> Decimal:
        """Calculate retention amount."""
        return (taxable_amount * rate / 100).quantize(Decimal("0.01"))
    
    def validate_vat_rate(
        self,
        rate: Decimal,
        country: str,
    ) -> bool:
        """Validate VAT rate for country."""
        # Basic validation - user can extend
        if rate < 0 or rate > 100:
            return False
        return True
