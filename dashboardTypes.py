
from pydantic import BaseModel
from typing import Dict, List, Any, Union, Literal, Optional

# export interface IRowLayout {
#     type: "row"
#     className?: string;
#     content: ILayout[]
# }

# export interface IColLayout {
#     type: "col"
#     className?: string;
#     content: ILayout[]
# }

# export interface IComponentLayout {
#     type: "component"
#     className?: string;
#     // This will look up a React.FC<T>
#     componentName: string;
#     componentState: any
# }

# export type ILayout = IRowLayout | IColLayout | IComponentLayout;


class RowLayoutType(BaseModel):
    type: Literal["row"]
    className: Optional[str]
    content: List[ILayout]

class ColLayoutType(BaseModel):
    type: Literal["col"]
    className: Optional[str]
    content: List[ILayout]

class ComponentLayoutType(BaseModel):
    type: Literal["component"]
    className: Optional[str]
    componentName: str
    componentState: Any


LayoutType = Union[ITypeA, ITypeB]


class DashboardResponse(BaseModel):
    layout: LayoutType
    vegaSpecs: Dict[str, str]
