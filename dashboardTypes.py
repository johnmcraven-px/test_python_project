
from pydantic import BaseModel
from typing import Dict, List, Any, Union, Literal, Optional, ForwardRef

class RowLayoutType(BaseModel):
    type: Literal["row"]
    className: Optional[str]
    content: List['LayoutType']

class ColLayoutType(BaseModel):
    type: Literal["col"]
    className: Optional[str]
    content: List['LayoutType']

class ComponentLayoutType(BaseModel):
    type: Literal["component"]
    className: Optional[str]
    componentName: str
    componentState: Any

LayoutType = Union[RowLayoutType, ColLayoutType, ComponentLayoutType]

RowLayoutType.update_forward_refs()
ColLayoutType.update_forward_refs()


class DashboardResponse(BaseModel):
    layout: LayoutType
    vegaSpecs: Dict[str, str]
