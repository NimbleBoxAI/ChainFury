export const nodeColors: { [char: string]: string } = {
  prompts: '#9CE0FC',
  llms: '#6344BE',
  chains: '#EA3852',
  agents: '#FF7496',
  tools: '#FF3434',
  memories: '#FF9135',
  advanced: '#000000',
  chat: '#454173',
  thought: '#272541',
  docloaders: '#FF9135',
  toolkits: '#DB2C2C',
  wrappers: '#E6277A',
  unknown: '#9CA3AF',
  models: '#9CE0FC',
  programatic_actions: '#6344BE',
  builtin_ai: '#EA3852'
};

export const nodeNames: { [char: string]: string } = {
  prompts: 'Prompts',
  llms: 'LLMs',
  chains: 'Chains',
  agents: 'Agents',
  tools: 'Tools',
  memories: 'Memories',
  advanced: 'Advanced',
  chat: 'Chat',
  docloaders: 'Document Loader',
  toolkits: 'Toolkits',
  wrappers: 'Wrappers',
  unknown: 'Unknown'
};

export function makeid(length: number) {
  let result = '';
  const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  const charactersLength = characters.length;
  let counter = 0;
  while (counter < length) {
    result += characters.charAt(Math.floor(Math.random() * charactersLength));
    counter += 1;
  }
  return result;
}
