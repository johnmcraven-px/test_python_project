
from pydantic import BaseModel
from typing import Dict, List, Any, Union, Literal, Optional, ForwardRef

class RowLayoutType(BaseModel):
    type: Literal["row"]
    className: Optional[str]
    style: Optional[Dict[str, str | int]]
    content: List['LayoutType']

class ListLayoutType(BaseModel):
    type: Literal["list"]
    className: Optional[str]
    style: Optional[Dict[str, str | int]]
    content: List['LayoutType']

class ComponentLayoutType(BaseModel):
    type: Literal["component"]
    className: Optional[str]
    style: Optional[Dict[str, str | int]]
    componentName: str
    componentState: Any

LayoutType = Union[RowLayoutType, ListLayoutType, ComponentLayoutType]

RowLayoutType.update_forward_refs()
ListLayoutType.update_forward_refs()


class DashboardResponse(BaseModel):
    layout: LayoutType
    vegaSpecs: Dict[str, str]

class UpdatesFromSignalsRequest(BaseModel):
    # {[sourceSpecId: string]: {[signalName: any]}}
    signals: Dict[str, Dict[str, Any]]


class UpdatesFromSignalsResponse(BaseModel):
    vegaSpecs: Dict[str, str]