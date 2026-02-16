from pydantic import BaseModel, Field


class LegalFooterModel(BaseModel):
    text: str = Field(..., description="Full footer text")
    act_type: str = Field(..., description="Type of act")
    act_name: str = Field(..., description="Name of act")
    signed_by: str = Field(..., description="Signed / Approved by")
    number_and_date: str = Field(..., description="Number and date")
    edition: str = Field(..., description="Edition / version")
    status: str = Field(..., description="Current status")
    permanent_link: str = Field(..., description="Permanent link / electronic version")