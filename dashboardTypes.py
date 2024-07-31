
from pydantic import BaseModel
from typing import Dict, List

class DashboardResponse(BaseModel):
    layout: str
    vegaSpecs: Dict[str, str]
