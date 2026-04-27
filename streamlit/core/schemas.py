from pydantic import BaseModel, Field
from typing import Optional, List

class ExtractedField(BaseModel):
    value: str = Field(description="The extracted text value")
    bounding_box: List[int] = Field(description="Bounding box coordinates [xmin, ymin, xmax, ymax]")

class InvoiceExtraction(BaseModel):
    invoice_number: Optional[ExtractedField]
    invoice_date: Optional[ExtractedField]
    total_amount: Optional[ExtractedField]
    vendor_name: Optional[ExtractedField]
    vendor_address: Optional[ExtractedField]
    customer_name: Optional[ExtractedField]
