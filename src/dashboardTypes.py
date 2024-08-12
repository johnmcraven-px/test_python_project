
from pydantic import BaseModel
from typing import Dict, List, Any, Union, Literal, Optional, ForwardRef

# export interface IParamControl {
#   type: "range",
#   labelTitle: string;
#   displayName: string;
#   numberType: "integer" | "float";
#   defaultStart: number;
#   defaultEnd: number;
#   defaultStep: number;
# }

class ParamControl(BaseModel):
    type: Literal["range"]
    labelTitle: str
    displayName: str
    numberType: Union[Literal["integer"], Literal["float"]]
    defaultStart: Union[float | int]
    defaultEnd: Union[float | int]
    defaultStep: Union[float | int]

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