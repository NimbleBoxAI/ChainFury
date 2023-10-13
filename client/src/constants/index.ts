import { ReactFlowInstance } from 'reactflow';

const BASE_URL = window?.location?.host?.includes(':5173')
  ? 'http://127.0.0.1:8000'
  : '';

const DummyMetricsData = {
  data: [
    {
      '': {
        total_conversations: 10,
        total_tokens_processed: 6950,
        no_of_conversations_rated_by_developer: 7,
        no_of_conversations_rated_by_end_user: 5,
        no_of_conversations_rated_by_openai: 10,
        average_rating: 2.5,
        average_chatbot_user_ratings: 2,
        average_developer_ratings: 3,
        average_openai_ratings: 2
      }
    }
  ]
};

const DummyMetricsInfo = {
  user_score: {
    bad_count: 2,
    good_count: 9,
    neutral_count: 10
  },
  internal_review_score: {
    bad_count: 4,
    good_count: 7,
    neutral_count: 10
  },
  gpt_review_score: {
    bad_count: 3,
    good_count: 8,
    neutral_count: 10
  }
};

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

export { BASE_URL, DummyMetricsData, DummyMetricsInfo };
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
  ParameterComponentType
};
