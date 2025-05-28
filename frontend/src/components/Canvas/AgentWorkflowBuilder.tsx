import React, { useState, useRef, useCallback } from 'react';
import { ChevronDown, Plus, Play, Save, Settings, Trash2, Move, Search, Filter, Grid } from 'lucide-react';

// Define interfaces for better type safety
interface AgentItem {
  id: string;
  name: string;
  description: string;
}

interface AgentCategory {
  color: string;
  items: AgentItem[];
}

interface Node {
  id: string;
  x: number;
  y: number;
  label: string;
  type: string;
  description: string;
  category?: string;  // Optional category field
}

interface Connection {
  from: string;
  to: string;
}

interface ConnectionPoint {
  start: { x: number; y: number };
  end: { x: number; y: number };
}

// Agent Categories and Types
const agentCategories: Record<string, AgentCategory> = {
  'LLM Agents': {
    color: '#3B82F6',
    items: [
      { id: 'openai-gpt4', name: 'OpenAI GPT-4', description: 'Advanced reasoning and code generation' },
      { id: 'claude-sonnet', name: 'Claude Sonnet', description: 'Anthropic\'s Claude for analysis' },
      { id: 'gemini-pro', name: 'Gemini Pro', description: 'Google\'s multimodal AI' },
      { id: 'llama-3', name: 'Llama 3', description: 'Meta\'s open-source LLM' }
    ]
  },
  'Specialized Agents': {
    color: '#10B981',
    items: [
      { id: 'code-agent', name: 'Code Agent', description: 'Software development and debugging' },
      { id: 'data-analyst', name: 'Data Analyst', description: 'Data processing and visualization' },
      { id: 'web-scraper', name: 'Web Scraper', description: 'Extract data from websites' },
      { id: 'email-agent', name: 'Email Agent', description: 'Email automation and management' }
    ]
  },
  'Tools & Connectors': {
    color: '#F59E0B',
    items: [
      { id: 'webhook', name: 'Webhook', description: 'HTTP requests and API calls' },
      { id: 'database', name: 'Database', description: 'SQL and NoSQL operations' },
      { id: 'file-processor', name: 'File Processor', description: 'File upload and processing' },
      { id: 'scheduler', name: 'Scheduler', description: 'Time-based triggers' }
    ]
  },
  'CrewAI Components': {
    color: '#8B5CF6',
    items: [
      { id: 'crew-manager', name: 'Crew Manager', description: 'Orchestrate multiple agents' },
      { id: 'task-delegator', name: 'Task Delegator', description: 'Distribute tasks to agents' },
      { id: 'crew-memory', name: 'Crew Memory', description: 'Shared memory across agents' }
    ]
  },
  'LangChain Tools': {
    color: '#EF4444',
    items: [
      { id: 'langchain-agent', name: 'LangChain Agent', description: 'Agent with tools and memory' },
      { id: 'vector-store', name: 'Vector Store', description: 'Embedding storage and retrieval' },
      { id: 'retriever', name: 'Retriever', description: 'RAG document retrieval' },
      { id: 'chain-executor', name: 'Chain Executor', description: 'Execute LangChain sequences' }
    ]
  },
  'Monitoring & Control': {
    color: '#6B7280',
    items: [
      { id: 'logger', name: 'Logger', description: 'Log agent activities' },
      { id: 'metrics', name: 'Metrics', description: 'Performance monitoring' },
      { id: 'error-handler', name: 'Error Handler', description: 'Exception handling' },
      { id: 'validator', name: 'Validator', description: 'Output validation' }
    ]
  }
};

// Node Component
const WorkflowNode = ({ 
  node, 
  isSelected, 
  onSelect, 
  onMove, 
  onStartConnection, 
  onEndConnection, 
  isDragging 
}: { 
  node: Node; 
  isSelected: boolean; 
  onSelect: (id: string) => void; 
  onMove: (id: string, x: number, y: number) => void; 
  onStartConnection: (id: string, type: 'input' | 'output') => void; 
  onEndConnection?: (id: string) => void; 
  isDragging: boolean; 
}) => {
  const [dragStart, setDragStart] = useState<{ x: number; y: number } | null>(null);
  const nodeRef = useRef<HTMLDivElement>(null);

  const categoryColor = node.category ? agentCategories[node.category]?.color : '#6B7280';

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.target instanceof HTMLElement && e.target.classList.contains('connection-point')) return;
    
    e.stopPropagation();
    onSelect(node.id);
    
    if (nodeRef.current) {
      const rect = nodeRef.current.getBoundingClientRect();
      const canvasRect = nodeRef.current.closest('.canvas')?.getBoundingClientRect() || { left: 0, top: 0 };
      
      setDragStart({
        x: e.clientX - (node.x + canvasRect.left),
        y: e.clientY - (node.y + canvasRect.top)
      });
    }
  };

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!dragStart) return;
    
    if (nodeRef.current) {
      const canvasRect = nodeRef.current.closest('.canvas')?.getBoundingClientRect() || { left: 0, top: 0 };
      const newX = e.clientX - canvasRect.left - dragStart.x;
      const newY = e.clientY - canvasRect.top - dragStart.y;
      
      onMove(node.id, Math.max(0, newX), Math.max(0, newY));
    }
  }, [dragStart, node.id, onMove]);

  const handleMouseUp = () => {
    setDragStart(null);
    if (onEndConnection) {
      onEndConnection(node.id);
    }
  };

  React.useEffect(() => {
    if (dragStart) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [dragStart, handleMouseMove]);

  return (
    <div
      ref={nodeRef}
      className={`absolute bg-white border-2 rounded-lg shadow-lg transition-all duration-200 min-w-[180px] cursor-move ${
        isSelected ? 'border-blue-500 shadow-blue-200 z-20' : 'border-gray-200 hover:border-gray-300 z-10'
      } ${isDragging ? 'opacity-75' : ''}`}
      style={{ 
        left: node.x, 
        top: node.y,
        transform: isDragging ? 'scale(1.05)' : 'scale(1)'
      }}
      onMouseDown={handleMouseDown}
    >
      <div className="px-4 py-3">
        <div className="flex items-center space-x-2">
          <div 
            className="w-3 h-3 rounded-full"
            style={{ backgroundColor: categoryColor }}
          />
          <div className="font-medium text-sm text-gray-900 truncate">
            {node.label}
          </div>
        </div>
        <div className="text-xs text-gray-500 mt-1 truncate">
          {node.description}
        </div>
      </div>
      
      {/* Connection points */}
      <div 
        className="connection-point absolute -left-2 top-1/2 w-4 h-4 bg-gray-400 rounded-full transform -translate-y-1/2 cursor-crosshair hover:bg-blue-500 transition-colors"
        onMouseDown={(e) => {
          e.stopPropagation();
          onStartConnection(node.id, 'input');
        }}
      />
      <div 
        className="connection-point absolute -right-2 top-1/2 w-4 h-4 bg-gray-400 rounded-full transform -translate-y-1/2 cursor-crosshair hover:bg-blue-500 transition-colors"
        onMouseDown={(e) => {
          e.stopPropagation();
          onStartConnection(node.id, 'output');
        }}
        onMouseEnter={(e) => {
          if (onEndConnection) onEndConnection(node.id);
        }}
      />
    </div>
  );
};

// Connection SVG Component
const ConnectionSVG = ({ connections, nodes, tempConnection }: { 
  connections: Connection[]; 
  nodes: Node[]; 
  tempConnection?: ConnectionPoint;
}) => {
  const getNodeCenter = (nodeId: string, point: 'output' = 'output') => {
    const node = nodes.find(n => n.id === nodeId);
    if (!node) return { x: 0, y: 0 };
    
    const offsetX = point === 'output' ? 180 : 0;
    return {
      x: node.x + offsetX,
      y: node.y + 37 // half height of node
    };
  };

  const createPath = (start: { x: number; y: number }, end: { x: number; y: number }) => {
    const deltaX = end.x - start.x;
    const deltaY = end.y - start.y;
    const controlPointOffset = Math.max(Math.abs(deltaX) / 2, 50);
    
    return `M ${start.x} ${start.y} C ${start.x + controlPointOffset} ${start.y}, ${end.x - controlPointOffset} ${end.y}, ${end.x} ${end.y}`;
  };

  return (
    <svg className="absolute inset-0 pointer-events-none z-5" style={{ width: '100%', height: '100%' }}>
      <defs>
        <marker id="arrowhead" markerWidth="10" markerHeight="7" 
          refX="9" refY="3.5" orient="auto">
          <polygon points="0 0, 10 3.5, 0 7" fill="#6B7280" />
        </marker>
      </defs>
      
      {/* Existing connections */}
      {connections.map((conn, index) => {
        const start = getNodeCenter(conn.from, 'output');
        const end = getNodeCenter(conn.to, 'input');
        return (
          <path
            key={index}
            d={createPath(start, end)}
            stroke="#6B7280"
            strokeWidth="2"
            fill="none"
            markerEnd="url(#arrowhead)"
            className="drop-shadow-sm"
          />
        );
      })}
      
      {/* Temporary connection while dragging */}
      {tempConnection && (
        <path
          d={createPath(tempConnection.start, tempConnection.end)}
          stroke="#3B82F6"
          strokeWidth="2"
          fill="none"
          strokeDasharray="5,5"
          markerEnd="url(#arrowhead)"
        />
      )}
    </svg>
  );
};

export default function AgentWorkflowBuilder() {
  const [nodes, setNodes] = useState<Node[]>([
    {
      id: '1',
      x: 100,
      y: 100,
      label: 'OpenAI GPT-4',
      type: 'openai-gpt4',
      description: 'Advanced reasoning and code generation'
    },
    {
      id: '2',
      x: 400,
      y: 100,
      label: 'Code Agent',
      type: 'code-agent',
      description: 'Software development and debugging'
    }
  ]);
  
  const [connections, setConnections] = useState<Connection[]>([
    { from: '1', to: '2' }
  ]);
  
  const [expandedCategories, setExpandedCategories] = useState<Record<string, boolean>>({
    'LLM Agents': true
  });
  
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [connecting, setConnecting] = useState<{ nodeId: string; type: 'input' | 'output' } | null>(null);
  const [tempConnection, setTempConnection] = useState<ConnectionPoint | null>(null);
  const [mousePos, setMousePos] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All Categories');
  const [viewMode, setViewMode] = useState<'list' | 'grid'>('list');
  const [draggedAgent, setDraggedAgent] = useState<AgentItem | null>(null);
  
  const canvasRef = useRef<HTMLDivElement>(null);

  const toggleCategory = (category: string) => {
    setExpandedCategories(prev => ({
      ...prev,
      [category]: !prev[category]
    }));
  };

  // Filter agents based on search and category
  const getFilteredAgents = (): Record<string, AgentCategory> => {
    let filteredCategories = { ...agentCategories };
    
    // Filter by selected category
    if (selectedCategory !== 'All Categories') {
      filteredCategories = { [selectedCategory]: agentCategories[selectedCategory] };
    }
    
    // Filter by search term
    if (searchTerm) {
      Object.keys(filteredCategories).forEach(category => {
        filteredCategories[category] = {
          ...filteredCategories[category],
          items: filteredCategories[category].items.filter(item =>
            item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            item.description.toLowerCase().includes(searchTerm.toLowerCase())
          )
        };
        
        // Remove empty categories
        if (filteredCategories[category].items.length === 0) {
          delete filteredCategories[category];
        }
      });
    }
    
    return filteredCategories;
  };

  // Handle drag start from agent library
  const handleAgentDragStart = (e: React.DragEvent, agentItem: AgentItem) => {
    setDraggedAgent(agentItem);
    e.dataTransfer.effectAllowed = 'copy';
  };

  // Handle drop on canvas
  const handleCanvasDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (draggedAgent && canvasRef.current) {
      const rect = canvasRef.current.getBoundingClientRect();
      const position = {
        x: e.clientX - rect.left - 90, // Center the node
        y: e.clientY - rect.top - 37
      };
      addNodeToCanvas(draggedAgent, position);
      setDraggedAgent(null);
    }
  };

  const handleCanvasDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const addNodeToCanvas = (agentItem: AgentItem, position?: { x: number; y: number }) => {
    const newNode: Node = {
      id: Date.now().toString(),
      x: position ? position.x : Math.random() * 300 + 50,
      y: position ? position.y : Math.random() * 300 + 50,
      label: agentItem.name,
      type: agentItem.id,
      description: agentItem.description
    };
    setNodes(prev => [...prev, newNode]);
  };

  const moveNode = (nodeId: string, x: number, y: number) => {
    setNodes(prev => prev.map(node => 
      node.id === nodeId ? { ...node, x, y } : node
    ));
  };

  const selectNode = (nodeId: string) => {
    setSelectedNode(nodeId);
  };

  const deleteSelectedNode = () => {
    if (selectedNode) {
      setNodes(prev => prev.filter(node => node.id !== selectedNode));
      setConnections(prev => prev.filter(conn => 
        conn.from !== selectedNode && conn.to !== selectedNode
      ));
      setSelectedNode(null);
    }
  };

  const startConnection = (nodeId: string, type: 'input' | 'output') => {
    setConnecting({ nodeId, type });
  };

  const endConnection = (targetNodeId: string) => {
    if (connecting && connecting.nodeId !== targetNodeId) {
      const newConnection: Connection = {
        from: connecting.type === 'output' ? connecting.nodeId : targetNodeId,
        to: connecting.type === 'output' ? targetNodeId : connecting.nodeId
      };
      
      // Check if connection already exists
      const exists = connections.some(conn => 
        conn.from === newConnection.from && conn.to === newConnection.to
      );
      
      if (!exists) {
        setConnections(prev => [...prev, newConnection]);
      }
    }
    setConnecting(null);
    setTempConnection(null);
  };

  const handleCanvasMouseMove = (e: React.MouseEvent) => {
    if (!canvasRef.current) return;
    
    const rect = canvasRef.current.getBoundingClientRect();
    const newMousePos = {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    };
    setMousePos(newMousePos);

    if (connecting) {
      const sourceNode = nodes.find(n => n.id === connecting.nodeId);
      if (sourceNode) {
        const startX = connecting.type === 'output' ? sourceNode.x + 180 : sourceNode.x;
        const startY = sourceNode.y + 37;
        
        setTempConnection({
          start: { x: startX, y: startY },
          end: newMousePos
        });
      }
    }
  };

  const handleCanvasClick = (e: React.MouseEvent) => {
    if (e.target === canvasRef.current) {
      setSelectedNode(null);
      if (connecting) {
        setConnecting(null);
        setTempConnection(null);
      }
    }
  };

  const updateNodeProperty = (nodeId: string, property: keyof Node, value: string | number) => {
    setNodes(prev => prev.map(node => 
      node.id === nodeId ? { ...node, [property]: value } : node
    ));
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Left Panel - Agent Selection */}
      <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Agent Library</h2>
          <p className="text-sm text-gray-500 mt-1">Drag agents to build your workflow</p>
        </div>

        {/* Search and Filters */}
        <div className="p-4 border-b border-gray-200 space-y-3">
          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search agents..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            />
          </div>

          {/* Category Filter and View Toggle */}
          <div className="flex items-center justify-between space-x-2">
            <div className="flex-1">
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-blue-500"
              >
                <option value="All Categories">All Categories</option>
                {Object.keys(agentCategories).map(category => (
                  <option key={category} value={category}>{category}</option>
                ))}
              </select>
            </div>
            
            <div className="flex border border-gray-200 rounded-lg overflow-hidden">
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 ${viewMode === 'list' ? 'bg-blue-100 text-blue-600' : 'text-gray-500 hover:bg-gray-50'}`}
              >
                <Filter className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 ${viewMode === 'grid' ? 'bg-blue-100 text-blue-600' : 'text-gray-500 hover:bg-gray-50'}`}
              >
                <Grid className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Agent Categories */}
        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          {Object.entries(getFilteredAgents()).map(([category, config]) => (
            <div key={category} className="border border-gray-200 rounded-lg overflow-hidden">
              <button
                onClick={() => toggleCategory(category)}
                className="w-full px-4 py-3 bg-gray-50 hover:bg-gray-100 flex items-center justify-between text-left transition-colors"
              >
                <div className="flex items-center space-x-2">
                  <div 
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: config.color }}
                  />
                  <span className="font-medium text-gray-900">{category}</span>
                  <span className="text-xs text-gray-500 bg-white px-2 py-0.5 rounded-full">
                    {config.items.length}
                  </span>
                </div>
                <ChevronDown 
                  className={`w-4 h-4 text-gray-500 transition-transform ${
                    expandedCategories[category] ? 'rotate-180' : ''
                  }`}
                />
              </button>

              {expandedCategories[category] && (
                <div className={`p-2 ${viewMode === 'grid' ? 'grid grid-cols-1 gap-2' : 'space-y-1'}`}>
                  {config.items.map((item) => (
                    <div
                      key={item.id}
                      draggable
                      onDragStart={(e) => handleAgentDragStart(e, item)}
                      className={`${
                        viewMode === 'grid' 
                          ? 'p-3 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50' 
                          : 'flex items-center justify-between p-2 rounded hover:bg-gray-50'
                      } cursor-grab active:cursor-grabbing transition-all duration-200 group`}
                    >
                      {viewMode === 'grid' ? (
                        // Grid View
                        <div className="text-center">
                          <div 
                            className="w-8 h-8 rounded-full mx-auto mb-2"
                            style={{ backgroundColor: config.color }}
                          />
                          <div className="font-medium text-sm text-gray-900 truncate mb-1">
                            {item.name}
                          </div>
                          <div className="text-xs text-gray-500 h-8 overflow-hidden">
                            {item.description}
                          </div>
                          <button
                            onClick={() => addNodeToCanvas(item)}
                            className="mt-2 w-full py-1 px-2 bg-blue-100 text-blue-600 rounded text-xs hover:bg-blue-200 transition-colors"
                          >
                            Add to Canvas
                          </button>
                        </div>
                      ) : (
                        // List View
                        <>
                          <div className="flex items-center space-x-3 flex-1 min-w-0">
                            <div 
                              className="w-4 h-4 rounded-full flex-shrink-0"
                              style={{ backgroundColor: config.color }}
                            />
                            <div className="flex-1 min-w-0">
                              <div className="font-medium text-sm text-gray-900 truncate">
                                {item.name}
                              </div>
                              <div className="text-xs text-gray-500 truncate">
                                {item.description}
                              </div>
                            </div>
                          </div>
                          <button
                            onClick={() => addNodeToCanvas(item)}
                            className="ml-2 p-1 rounded-full bg-blue-100 text-blue-600 opacity-0 group-hover:opacity-100 transition-all hover:bg-blue-200 flex-shrink-0"
                          >
                            <Plus className="w-3 h-3" />
                          </button>
                        </>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}

          {/* No Results Message */}
          {Object.keys(getFilteredAgents()).length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <Search className="w-8 h-8 mx-auto mb-4 opacity-50" />
              <p className="font-medium">No agents found</p>
              <p className="text-sm">Try adjusting your search or filters</p>
            </div>
          )}
        </div>

        {/* Quick Stats */}
        <div className="p-4 border-t border-gray-200 bg-gray-50">
          <div className="flex justify-between text-xs text-gray-600">
            <span>Total Agents: {Object.values(agentCategories).reduce((sum, cat) => sum + cat.items.length, 0)}</span>
            <span>In Canvas: {nodes.length}</span>
          </div>
        </div>
      </div>

      {/* Right Panel - Canvas */}
      <div className="flex-1 flex flex-col">
        {/* Toolbar */}
        <div className="bg-white border-b border-gray-200 p-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <h1 className="text-lg font-semibold text-gray-900">Workflow Canvas</h1>
            <span className="text-sm text-gray-500">({nodes.length} nodes, {connections.length} connections)</span>
          </div>
          
          <div className="flex items-center space-x-2">
            {selectedNode && (
              <button
                onClick={deleteSelectedNode}
                className="px-3 py-1.5 bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors flex items-center space-x-1"
              >
                <Trash2 className="w-4 h-4" />
                <span>Delete</span>
              </button>
            )}
            <button className="px-3 py-1.5 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors flex items-center space-x-1">
              <Save className="w-4 h-4" />
              <span>Save</span>
            </button>
            <button className="px-3 py-1.5 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors flex items-center space-x-1">
              <Play className="w-4 h-4" />
              <span>Execute</span>
            </button>
          </div>
        </div>

        {/* Canvas */}
        <div className="flex-1 relative overflow-hidden">
          <div 
            ref={canvasRef}
            className="canvas w-full h-full relative bg-gray-50"
            style={{
              backgroundImage: `
                linear-gradient(rgba(0,0,0,.1) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0,0,0,.1) 1px, transparent 1px)
              `,
              backgroundSize: '20px 20px'
            }}
            onMouseMove={handleCanvasMouseMove}
            onClick={handleCanvasClick}
            onDrop={handleCanvasDrop}
            onDragOver={handleCanvasDragOver}
          >
            {/* Connections SVG */}
            <ConnectionSVG 
              connections={connections} 
              nodes={nodes} 
              tempConnection={tempConnection}
            />
            
            {/* Nodes */}
            {nodes.map((node) => (
              <WorkflowNode
                key={node.id}
                node={node}
                isSelected={selectedNode === node.id}
                onSelect={selectNode}
                onMove={moveNode}
                onStartConnection={startConnection}
                onEndConnection={endConnection}
                isDragging={false}
              />
            ))}

            {/* Instructions overlay when empty */}
            {nodes.length === 0 && (
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                <div className="text-center text-gray-500">
                  <Move className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p className="text-lg font-medium">Start building your workflow</p>
                  <p className="text-sm mt-1">Drag agents from the left panel or click + to add</p>
                  <div className="mt-4 text-xs text-gray-400">
                    💡 Tip: Drag between connection points to link agents
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Node Configuration Panel */}
          {selectedNode && (
            <div className="absolute top-4 right-4 w-64 bg-white rounded-lg shadow-lg border border-gray-200 p-4 z-30">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-medium text-gray-900">Node Configuration</h3>
                <Settings className="w-4 h-4 text-gray-500" />
              </div>
              
              {(() => {
                const node = nodes.find(n => n.id === selectedNode);
                if (!node) return null;
                
                return (
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                      <input 
                        type="text" 
                        value={node.label}
                        className="w-full px-3 py-2 border border-gray-200 rounded text-sm focus:outline-none focus:border-blue-500"
                        onChange={(e) => updateNodeProperty(selectedNode, 'label', e.target.value)}
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                      <input 
                        type="text" 
                        value={node.type}
                        className="w-full px-3 py-2 border border-gray-200 rounded text-sm bg-gray-50"
                        readOnly
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                      <textarea 
                        value={node.description}
                        className="w-full px-3 py-2 border border-gray-200 rounded text-sm resize-none focus:outline-none focus:border-blue-500"
                        rows={3}
                        onChange={(e) => updateNodeProperty(selectedNode, 'description', e.target.value)}
                      />
                    </div>
                    
                    <div className="pt-2 border-t border-gray-200">
                      <p className="text-xs text-gray-500">
                        Position: ({Math.round(node.x)}, {Math.round(node.y)})
                      </p>
                    </div>
                  </div>
                );
              })()}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
