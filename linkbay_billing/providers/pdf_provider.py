"""
PDF generation provider using Jinja2 and WeasyPrint.
"""

from typing import Dict, Any, List
from ..protocols import PDFTemplateProvider
from ..exceptions import PDFGenerationError


class Jinja2PDFProvider:
    """
    PDF provider using Jinja2 templates and WeasyPrint.
    
    User provides templates directory with HTML/CSS templates.
    """
    
    def __init__(self, templates_dir: str):
        """
        Initialize PDF provider.
        
        Args:
            templates_dir: Path to templates directory
        """
        self.templates_dir = templates_dir
        self._templates = {}
    
    async def render_pdf(
        self,
        invoice_data: Dict[str, Any],
        template_name: str = "default",
        language: str = "en",
    ) -> bytes:
        """
        Render invoice to PDF.
        
        Example:
            ```python
            provider = Jinja2PDFProvider("/path/to/templates")
            
            pdf_bytes = await provider.render_pdf(
                invoice_data=invoice_dict,
                template_name="default",
                language="it",
            )
            
            with open("invoice.pdf", "wb") as f:
                f.write(pdf_bytes)
            ```
        """
        try:
            # User implements: load Jinja2 template, render HTML, convert to PDF
            # This is a stub implementation
            html_content = f"<html><body>Invoice {invoice_data.get('invoice_number')}</body></html>"
            
            # In real implementation:
            # from jinja2 import Environment, FileSystemLoader
            # from weasyprint import HTML
            # env = Environment(loader=FileSystemLoader(self.templates_dir))
            # template = env.get_template(f"{template_name}_{language}.html")
            # html = template.render(**invoice_data)
            # pdf_bytes = HTML(string=html).write_pdf()
            
            return html_content.encode("utf-8")
        
        except Exception as e:
            raise PDFGenerationError(
                invoice_data.get("id", "unknown"),
                str(e),
            )
    
    async def get_available_templates(self) -> List[str]:
        """Get list of available templates."""
        return ["default", "minimal", "detailed"]
