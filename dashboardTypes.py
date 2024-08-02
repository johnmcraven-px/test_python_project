
from pydantic import BaseModel
from typing import Dict, List, Any, Union, Literal, Optional, ForwardRef

class RowLayoutType(BaseModel):
    type: Literal["row"]
    className: Optional[str]
    content: List['LayoutType']

class ListLayoutType(BaseModel):
    type: Literal["list"]
    className: Optional[str]
    content: List['LayoutType']

class ComponentLayoutType(BaseModel):
    type: Literal["component"]
    className: Optional[str]
    componentName: str
    componentState: Any

LayoutType = Union[RowLayoutType, ListLayoutType, ComponentLayoutType]

RowLayoutType.update_forward_refs()
ListLayoutType.update_forward_refs()


class DashboardResponse(BaseModel):
    layout: LayoutType
    vegaSpecs: Dict[str, str]
