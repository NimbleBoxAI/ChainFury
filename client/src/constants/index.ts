import { ReactFlowInstance } from "reactflow";

const BASE_URL = window?.location?.host?.includes("localhost:5173")
  ? "http://127.0.0.1:8000/api/v1"
  : "/api/v1";
type DEFAULT_RESPONSE = any;
type TemplateVariableType = {
  type: string;
  required: boolean;
  placeholder?: string;
  list: boolean;
  show: boolean;
  multiline?: boolean;
  value?: any;
  [key: string]: any;
};

type APITemplateType = {
  _type: any;
  [key: string]: TemplateVariableType;
};

type APIClassType = {
  base_classes: Array<string>;
  description: string;
  template: APITemplateType;
  chain: string;
  [key: string]: Array<string> | string | APITemplateType;
};
type NodeDataType = {
  type: string;
  node?: APIClassType;
  id: string;
  value: any;
  deleteMe: () => void;
};

type TextAreaComponentType = {
  disabled: boolean;
  onChange: (value: string) => void;
  value: string;
};

type DropDownComponentType = {
  value: string;
  options: string[];
  onSelect: (value: string) => void;
};

type FloatComponentType = {
  value: string;
  disabled?: boolean;
  onChange: (value: string) => void;
};

type InputComponentType = {
  value: string;
  disabled?: boolean;
  onChange: (value: string) => void;
  password: boolean;
};

type FileComponentType = {
  disabled: boolean;
  onChange: (value: string) => void;
  value: string;
  suffixes: Array<string>;
  fileTypes: Array<string>;
  onFileChange: (value: string) => void;
};

type InputListComponentType = {
  value: string[];
  onChange: (value: string[]) => void;
  disabled: boolean;
};

type ToggleComponentType = {
  enabled: boolean;
  setEnabled: (state: boolean) => void;
  disabled: boolean;
};

type ParameterComponentType = {
  data: NodeDataType;
  title: string;
  id: string;
  color: string;
  left: boolean;
  type: string;
  required?: boolean;
  name?: string;
  tooltipTitle: string;
};

export { BASE_URL };
export type {
  DEFAULT_RESPONSE,
  NodeDataType,
  APIClassType,
  APITemplateType,
  TemplateVariableType,
  TextAreaComponentType,
  DropDownComponentType,
  InputComponentType,
  FileComponentType,
  InputListComponentType,
  FloatComponentType,
  ToggleComponentType,
  ParameterComponentType,
};
