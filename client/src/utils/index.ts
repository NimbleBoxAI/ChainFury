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
  builtin_ai: '#EA3852',
  actions: '#FF9135'
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

export function convertStringToJson(x: string) {
  try {
    let idx = [...x]
      .map((ltr, i) => (ltr === '`' ? i : undefined))
      .filter((val): val is number => val !== undefined);
    if (idx.length % 2 !== 0) {
      console.log('Odd number of backticks');
    }

    let start_end_pairs: [number, number][] = [];
    for (let i = 0; i < idx.length; i += 2) {
      start_end_pairs.push([idx[i], idx[i + 1]]);
    }

    let new_x = '';
    let offset = 0;
    for (let [s, e] of start_end_pairs) {
      new_x += x.slice(offset, s) + x.slice(s, e).replace(/\n/g, '\\n') + x.slice(e, s);
      offset = e;
    }
    new_x += x.slice(offset);
    new_x = new_x.replace(/`/g, '"');
    console.log({ new_x });
    return JSON.parse(new_x);
  } catch (e) {
    console.log(e);
    return null;
  }
}

export const TranslateNodes = ({
  nodes,
  edges
}: {
  nodes: any;
  edges: any;
}): {
  nodes: any;
  edges: any;
  sample: Record<string, any>;
  main_in: string;
  main_out: string;
} => {
  const tempNodes = JSON.parse(JSON.stringify(nodes));
  const tempEdges = JSON.parse(JSON.stringify(edges));
  console.log('prev', { tempNodes, edges });
  let sample = {} as Record<string, any>;
  let chatIn = null as string | null;
  let chatOut = null as string | null;
  let nodeIds = [] as string[];
  let restructuredNodes = [] as any;

  // Generate sample data from nodes
  for (let key in tempNodes) {
    if (nodeIds.includes(tempNodes[key].id)) {
      continue;
    }
    nodeIds.push(tempNodes[key].id);
    let node = tempNodes[key];
    const passKeys = [] as string[];
    node?.data?.node?.fields?.forEach((field: any) => {
      if (field?.password) passKeys.push(field?.name);
    });
    Object?.entries(node?.data?.node?.fn?.model_params ?? {}).forEach(([key, value]) => {
      sample[`${!(passKeys.includes(key) && !sample[key]) ? node?.id + '/' : ''}${key}`] = value;
    });
    node['cf_data'] = node.data;
    delete node.data;
    restructuredNodes.push(node);
  }
  for (let key in edges) {
    let edge = edges[key];
    if (edge?.source === 'chatin') {
      chatIn = edge?.target + '/' + edge?.targetHandle;
    }
    if (edge?.target === 'chatout') {
      chatOut = edge?.source + '/' + edge?.sourceHandle;
    }
    if (chatIn && chatOut) {
      break;
    }
  }
  restructuredNodes = restructuredNodes.filter(
    (node: { id: string }) => node.id !== 'chatin' && node.id !== 'chatout'
  );
  console.log('prev', { restructuredNodes, edges });

  return {
    sample,
    edges: FilterEdges({
      edges: tempEdges,
      nodeIds
    }),
    nodes: restructuredNodes,
    main_in: chatIn ?? '',
    main_out: chatOut ?? ''
  };
};

export const FilterEdges = ({
  edges,
  nodeIds
}: {
  edges: {
    source: string;
    sourceHandle: string;
    targetHandle: string;
    target: string;
  }[];
  nodeIds: string[];
}) => {
  const filteredEdges = edges.filter((edge: { source: string; target: string }) => {
    return (
      nodeIds.includes(edge.source) &&
      nodeIds.includes(edge.target) &&
      edge.source !== 'chatin' &&
      edge.target !== 'chatout'
    );
  });
  return filteredEdges;
};

export const safeJsonParse = (x: string) => {
  try {
    return JSON.parse(x);
  } catch (e) {
    return x;
  }
};
