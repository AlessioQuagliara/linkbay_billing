# LinkBay-Billing

**Version**: 0.3.x  
**License**: Proprietary  
**Python**: 3.10+  

Motore di documenti fiscali per SaaS multi-tenant: fatture, note di credito, calcolo IVA, generazione PDF/XML e integrazione con e-invoicing europeo. È una libreria protocol-based, database-agnostic e completamente async, pensata per collegarsi a `LinkBay-Subscriptions` (gestione piani/usage/proration) mantenendo separato il dominio fiscale.

## Project description

LinkBay-Billing copre il ciclo “documentale” della fatturazione: numerazione, calcoli IVA/ritenute, generazione PDF, creazione XML conforme a standard europei (FatturaPA, PEPPOL UBL, Factur-X) ed invio via email. Non è un motore subscription billing completo: per piani, proration, usage metering e dunning usare `LinkBay-Subscriptions`, che delega a questa libreria la produzione dei documenti fiscali.

## Principali capacità

- Servizi `InvoiceManager`, `VATCalculator`, `ReportingService` con API async multi-tenant.
- Protocolli `InvoiceStorage`, `SerialNumberProvider`, `EInvoiceProvider`, `PDFTemplateProvider`, `EmailProvider` per integrare qualsiasi datastore o provider terzo.
- Supporto dettagliato alla fiscalità italiana (ritenute, split payment, bollo) e mapping verso standard europei EN 16931 (FatturaPA, PEPPOL BIS, Factur-X/ZUGFeRD).
- Generazione PDF con template Jinja2 + WeasyPrint e creazione XML/UBL/CII personalizzabile tramite providers.
- Reportistica IVA e posizione clienti (outstanding) pronta per i team finance.
- Primitives multi-tenant isolati per `tenant_id`, con numerazioni dedicate e serial generator per tenant.

## Indice

- [Project description](#project-description)
- [Principali capacità](#principali-capacità)
- [Requisiti](#requisiti)
- [Perimetro e posizionamento](#perimetro-e-posizionamento)
- [Compliance e limitazioni](#compliance-e-limitazioni)
- [Multi-tenant e gerarchie](#multi-tenant-e-gerarchie)
- [Security & GDPR](#security--gdpr)
- [Architecture](#architecture)
- [Feature set](#feature-set)
- [Quick Start](#quick-start)
- [FastAPI Integration](#fastapi-integration)
- [VAT Calculation Examples](#vat-calculation-examples)

## Requisiti

| Requisito | Dettagli |
| --- | --- |
| Python | 3.10 o superiore |
| Dipendenze core | `pydantic>=2.0.0`, `python-dateutil` |
| Extra opzionali | `[pdf]` abilita Jinja2+WeasyPrint, `[einvoice]` abilita provider XML, `[fastapi]` espone il router REST, `[all]` installa tutto |
| Storage raccomandati | PostgreSQL (JSONB), MongoDB, DynamoDB, data lake append-only |
| Ambienti target | SaaS multi-tenant UE/Italia con requisiti fiscali strutturati |

## Perimetro e posizionamento

- **Cosa fa**: generazione documenti fiscali, calcoli IVA/ritenute/bollo, esportazione PDF/XML, gestione pagamenti registrati, report IVA/outstanding, email con allegati fiscali.
- **Cosa non fa**: gestione piani/abbonamenti, proration, metered billing, dunning, gerarchie di account, logica MRR/ARR. Queste parti sono in `LinkBay-Subscriptions` e in eventuali servizi verticali (es. `LinkBay-Org`).
- **Utilizzo tipico**: backend SaaS che riceve eventi di fatturazione (es. da Subscriptions) e produce documenti fiscali compliant da archiviare/inviare.

## Compliance e limitazioni

- La libreria genera documenti XML conformi agli standard EN 16931 (FatturaPA, PEPPOL BIS, Factur-X), ma **non** funge da intermediario SdI/PEPPOL: per l'invio serve un Access Point o provider certificato esterno.
- Non copre conservazione sostitutiva, firma digitale o riconciliazione con portali fiscali nazionali. Integra con servizi dedicati.
- Aggiornamenti normativi locali (es. CIUS nazionali) devono essere gestiti tramite estensioni dei provider o versionamento controllato.
- Include un disclaimer: non costituisce consulenza fiscale/legale; verificare sempre con il team contabile.

## Multi-tenant e gerarchie

- Il modello dati è basato su `tenant_id` piatto: ogni tenant ha numerazione, configurazioni IVA e documenti separati.
- Scenari enterprise con organizzazioni gerarchiche (holding + filiali) richiedono un livello applicativo aggiuntivo per consolidare o ripartire le fatture.
- Per consolidated billing o cross-tenant invoicing, prevedi servizi ad hoc che orchestrano più tenant e chiamano le API di LinkBay-Billing.

## Security & GDPR

- **Cifratura**: implementa provider `InvoiceStorage` che criptano i dati a riposo (es. KMS, column encryption) e assicurati che il traffico sia TLS.
- **Accesso controllato**: integra il router FastAPI con `LinkBay-Roles` per limitare la visibilità a ruoli finance/compliance; traccia tutte le operazioni con `LinkBay-Audit`.
- **Data minimization**: evita di memorizzare IBAN o PII non necessari; valuta strategie di mascheramento/anonimizzazione su storici oltre la retention obbligatoria.
- **Retention**: definisci policy per export e cancellazione storica coordinata con LinkBay-Audit e con i requisiti legali del paese.

## Architecture

Pure service/protocol approach con zero database coupling:

- `InvoiceStorage`: scegli il tuo datastore (PostgreSQL, MongoDB, DynamoDB, data lake) garantendo transazioni per tenant.
- `PDFTemplateProvider`: Jinja2/WeasyPrint o renderer custom; supporta localizzazione stringhe.
- `EInvoiceProvider`: FatturaPA (IT), PEPPOL BIS UBL, Factur-X/ZUGFeRD. Estendi con specifiche nazionali (xRechnung, Finvoice) implementando il protocollo.
- `SerialNumberProvider`: pattern configurabili (es. `{tenant_abbr}-{year}-{seq:06d}`) con reset annuale opzionale.
- `EmailProvider`: SMTP, SendGrid, AWS SES; supporta allegati PDF/XML e note di cortesia localizzate.

Tutte le integrazioni passano da `Protocol` per evitare lock-in applicativi.

## Feature set

- Creazione fatture e note di credito con auto-numbering per tenant.
- Calcolo IVA multi-aliquota, split payment, reverse charge, ritenute professionali, contributi INPS/ENASARCO, imposta di bollo.
- Tracking stato fattura (draft, issued, sent, paid, overdue) e registrazione pagamenti con riconciliazione manuale.
- Generazione PDF multi-lingua e multi-template con branding tenant-specific.
- Creazione XML per FatturaPA, PEPPOL BIS, Factur-X con hash e metadata per firma digitale.
- Servizi email per invio fatture e note di credito con allegati e log di invio.
- Report IVA (per periodo/aliquota) e report crediti aperti (outstanding) per tenant.
- Supporto i18n (IT, EN, DE, FR, ES) per etichette documenti e comunicazioni email.

## Installation

```bash
pip install linkbay-billing
```

Optional dependencies:

```bash
pip install linkbay-billing[pdf]        # Jinja2 + WeasyPrint
pip install linkbay-billing[einvoice]   # XML generation
pip install linkbay-billing[fastapi]    # REST API router
pip install linkbay-billing[all]        # All features
```

Direct installation from repository:


## Quick Start

### 1. Implement Storage Protocol

```python
from linkbay_billing import InvoiceStorage

class PostgresInvoiceStorage(InvoiceStorage):
    async def create_invoice(self, tenant_id: str, data: dict) -> dict:
        result = await self.db.execute(
            "INSERT INTO invoices (...) VALUES (...)",
            tenant_id, data["invoice_number"], ...
        )
        return {"id": result.id, **data}
    
    async def get_invoice(self, tenant_id: str, invoice_id: str) -> dict:
        return await self.db.fetch_one(
            "SELECT * FROM invoices WHERE tenant_id = $1 AND id = $2",
            tenant_id, invoice_id
        )
    
    # Implement other protocol methods...
```

### 2. Configure Services

```python
from linkbay_billing import (
    InvoiceManager,
    VATCalculator,
    SerialNumberGenerator,
    ReportingService,
)

# Initialize storage
storage = PostgresInvoiceStorage(db)

# Initialize services
serial_provider = SerialNumberGenerator(
    storage=storage,
    pattern="standard",  # {tenant_abbr}-{year}-{seq:06d}
)

invoice_manager = InvoiceManager(
    storage=storage,
    serial_provider=serial_provider,
)

reporting = ReportingService(storage)
```

### 3. Create Invoice

```python
from linkbay_billing import InvoiceCreate, InvoiceRow, PaymentInfo, Company, Customer
from decimal import Decimal
from datetime import date

invoice = await invoice_manager.create_invoice(
    tenant_id="agency123",
    invoice_data=InvoiceCreate(
        company=Company(
            name="ACME Agency",
            address=Address(
                street="Via Roma 1",
                city="Milano",
                postal_code="20100",
                country="IT",
            ),
            tax_info=TaxInfo(vat_number="IT12345678901"),
            email="info@acme.com",
        ),
        customer=Customer(
            id="cust_123",
            name="Cliente SPA",
            address=Address(
                street="Corso Italia 50",
                city="Milano",
                postal_code="20100",
                country="IT",
            ),
            tax_info=TaxInfo(vat_number="IT98765432109"),
            email="cliente@example.com",
            is_company=True,
        ),
        rows=[
            InvoiceRow(
                description="Web Design Service",
                quantity=Decimal("10"),
                unit_price=Decimal("100"),
                vat_rate=Decimal("22"),
                unit="hours",
            ),
            InvoiceRow(
                description="Hosting Service",
                quantity=Decimal("12"),
                unit_price=Decimal("50"),
                vat_rate=Decimal("22"),
                unit="months",
            ),
        ],
        issue_date=date.today(),
        payment_info=PaymentInfo(
            method="bank_transfer",
            terms="net_30",
            bank_name="Intesa Sanpaolo",
            iban="IT60X0542811101000000123456",
        ),
        retention=RetentionInfo(
            rate=Decimal("20"),
            amount=Decimal("320"),  # 20% of 1600
            reason="Ritenuta d'acconto professionale",
        ),
        split_payment=False,
        stamp_duty=False,
    ),
)

print(f"Invoice created: {invoice.invoice_number}")
print(f"Total: EUR {invoice.total}")
print(f"Net to pay: EUR {invoice.net_to_pay}")
```

### 4. Generate PDF

```python
from linkbay_billing import Jinja2PDFProvider

pdf_provider = Jinja2PDFProvider("/path/to/templates")

pdf_bytes = await pdf_provider.render_pdf(
    invoice_data=invoice.model_dump(),
    template_name="default",
    language="it",
)

with open(f"invoice_{invoice.invoice_number}.pdf", "wb") as f:
    f.write(pdf_bytes)
```

### 5. Generate E-Invoice XML

```python
from linkbay_billing import FatturaPAProvider

einvoice_provider = FatturaPAProvider()

result = await einvoice_provider.generate_xml(
    invoice_data=invoice.model_dump(),
    format="fatturapa",
)

xml_content = result["xml"]
xml_hash = result["hash"]

# Save XML for digital signature
with open(f"invoice_{invoice.invoice_number}.xml", "w") as f:
    f.write(xml_content)
```

### 6. Send Invoice via Email

```python
from linkbay_billing import SimpleEmailProvider

email_provider = SimpleEmailProvider(
    smtp_host="smtp.gmail.com",
    smtp_port=587,
    smtp_user="user@example.com",
    smtp_password="password",
    from_email="invoices@acme.com",
)

result = await email_provider.send_invoice(
    tenant_id="agency123",
    invoice_id=invoice.id,
    recipient_email="cliente@example.com",
    subject=f"Invoice {invoice.invoice_number}",
    body="Please find your invoice attached.",
    pdf_attachment=pdf_bytes,
    xml_attachment=xml_content.encode("utf-8"),
)

# Mark invoice as sent
await invoice_manager.mark_as_sent("agency123", invoice.id)
```

### 7. Record Payment

```python
from linkbay_billing import PaymentRecordCreate

payment = await invoice_manager.record_payment(
    tenant_id="agency123",
    invoice_id=invoice.id,
    payment_data=PaymentRecordCreate(
        amount=invoice.net_to_pay,
        payment_date=date.today(),
        payment_method="bank_transfer",
        transaction_id="TXN123456",
    ),
)

print(f"Payment recorded: {payment.id}")
```

### 8. Generate VAT Report

```python
vat_report = await reporting.generate_vat_report(
    tenant_id="agency123",
    period_start=date(2025, 1, 1),
    period_end=date(2025, 3, 31),
)

print(f"Total invoices: {vat_report.total_invoices}")
print(f"Total taxable: EUR {vat_report.total_taxable}")
print(f"Total VAT: EUR {vat_report.total_vat}")

for summary in vat_report.vat_by_rate:
    print(f"  VAT {summary.vat_rate}%: EUR {summary.vat_amount}")
```

### 9. Generate Outstanding Report

```python
outstanding_report = await reporting.generate_outstanding_report(
    tenant_id="agency123"
)

print(f"Total outstanding: EUR {outstanding_report.total_outstanding}")
print(f"Total overdue: EUR {outstanding_report.total_overdue}")

for customer in outstanding_report.by_customer:
    print(f"  {customer.customer_name}: EUR {customer.total_outstanding}")
```

### 10. Create Credit Note

```python
from linkbay_billing import CreditNoteCreate

credit_note = await invoice_manager.create_credit_note(
    tenant_id="agency123",
    credit_note_data=CreditNoteCreate(
        original_invoice_id=invoice.id,
        reason="Customer requested refund",
        issue_date=date.today(),
        # rows=None means credit full invoice
    ),
)

print(f"Credit note created: {credit_note.invoice_number}")
```

## FastAPI Integration

```python
from fastapi import FastAPI
from linkbay_billing import create_billing_router

app = FastAPI()

router = create_billing_router(
    invoice_manager=invoice_manager,
    reporting_service=reporting,
    pdf_provider=pdf_provider,
    einvoice_provider=einvoice_provider,
    email_provider=email_provider,
)

app.include_router(router)

# Available endpoints:
# POST   /billing/{tenant_id}/invoices
# GET    /billing/{tenant_id}/invoices/{invoice_id}
# GET    /billing/{tenant_id}/invoices
# PUT    /billing/{tenant_id}/invoices/{invoice_id}
# DELETE /billing/{tenant_id}/invoices/{invoice_id}
# POST   /billing/{tenant_id}/credit-notes
# POST   /billing/{tenant_id}/invoices/{invoice_id}/payments
# GET    /billing/{tenant_id}/invoices/{invoice_id}/pdf
# POST   /billing/{tenant_id}/invoices/{invoice_id}/xml
# POST   /billing/{tenant_id}/invoices/{invoice_id}/send
# GET    /billing/{tenant_id}/reports/vat
# GET    /billing/{tenant_id}/reports/outstanding
```

## VAT Calculation Examples

### Multi-Rate VAT

```python
from linkbay_billing import VATCalculator

calculator = VATCalculator()

result = calculator.calculate(
    rows=[
        InvoiceRow(
            description="Service A",
            quantity=Decimal("10"),
            unit_price=Decimal("100"),
            vat_rate=Decimal("22"),  # Standard IT
        ),
        InvoiceRow(
            description="Service B",
            quantity=Decimal("5"),
            unit_price=Decimal("50"),
            vat_rate=Decimal("10"),  # Reduced IT
        ),
    ],
)

print(f"Subtotal: EUR {result.subtotal}")
print(f"Total VAT: EUR {result.total_vat}")
print(f"Total: EUR {result.total}")

for summary in result.vat_summaries:
    print(f"  VAT {summary.vat_rate}%: EUR {summary.vat_amount}")
```

### With Retention

```python
result = calculator.calculate(
    rows=rows,
    retention=RetentionInfo(
        rate=Decimal("20"),
        amount=Decimal("240"),
    ),
)

print(f"Total: EUR {result.total}")
print(f"Retention: EUR {result.retention_amount}")
print(f"Net to pay: EUR {result.net_to_pay}")
```

### Split Payment (Italy)

```python
result = calculator.calculate(
    rows=rows,
    split_payment=True,  # VAT calculated but not charged
)

print(f"Subtotal: EUR {result.subtotal}")
print(f"VAT (not charged): EUR {result.total_vat}")
print(f"Total: EUR {result.total}")
```

## Invoice Numbering Patterns

```python
from linkbay_billing import INVOICE_NUMBER_PATTERNS

# Available patterns:
# - "standard": ACME-2025-000001
# - "simple": 2025/0001
# - "with_type": INV/2025/00001
# - "full": ACME-INV-2025-01-00001

serial_provider = SerialNumberGenerator(
    storage=storage,
    pattern="with_type",
    tenant_abbr_resolver=lambda tid: get_tenant(tid).abbreviation,
)
```

## Multi-Tenant Support

All operations enforce tenant isolation:

```python
# Each tenant has separate invoice numbering
invoice_a = await invoice_manager.create_invoice(
    tenant_id="agency_a",
    invoice_data=...,
)
# Result: AGENCYA-2025-000001

invoice_b = await invoice_manager.create_invoice(
    tenant_id="agency_b",
    invoice_data=...,
)
# Result: AGENCYB-2025-000001
```

## Internationalization

All templates and labels support multiple languages:

```python
pdf_bytes = await pdf_provider.render_pdf(
    invoice_data=invoice.model_dump(),
    language="it",  # Italian labels
)

# Supported languages: IT, EN, DE, FR, ES
```

## Testing

Mock storage for unit tests:

```python
from linkbay_billing import InvoiceStorage

class MockStorage(InvoiceStorage):
    def __init__(self):
        self.invoices = {}
        self.serial_counter = {}
    
    async def create_invoice(self, tenant_id: str, data: dict) -> dict:
        invoice_id = f"inv_{len(self.invoices)}"
        self.invoices[invoice_id] = {"id": invoice_id, **data}
        return self.invoices[invoice_id]
    
    # Implement other methods...

storage = MockStorage()
manager = InvoiceManager(storage, serial_provider)
```

## Author

**Alessio Quagliara**

