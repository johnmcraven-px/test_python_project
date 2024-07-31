
from pydantic import BaseModel
from typing import Dict, List

class DashboardResponse(BaseModel):
    goldenLayoutJsonStr: str
    vegaSpecs: Dict[str, str]
