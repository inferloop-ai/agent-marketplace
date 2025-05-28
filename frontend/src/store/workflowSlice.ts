// frontend/src/store/workflowSlice.ts
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { apiService } from '../services/api';

interface Node {
  id: string;
  name: string;
  type: string;
  position_x: number;
  position_y: number;
  config: Record<string, any>;
  metadata: Record<string, any>;
}

interface Connection {
  id: string;
  source_node_id: string;
  target_node_id: string;
  source_port: string;
  target_port: string;
}

interface Workflow {
  id: string;
  name: string;
  description?: string;
  status: string;
  definition: Record<string, any>;
  nodes?: Node[];
  connections?: Connection[];
  created_at: string;
  updated_at: string;
}

interface WorkflowState {
  workflows: Workflow[];
  currentWorkflow: Workflow | null;
  selectedNodeId: string | null;
  isLoading: boolean;
  error: string | null;
}

const initialState: WorkflowState = {
  workflows: [],
  currentWorkflow: null,
  selectedNodeId: null,
  isLoading: false,
  error: null,
};

// Async thunks
export const fetchWorkflows = createAsyncThunk(
  'workflow/fetchWorkflows',
  async (params?: any, { rejectWithValue }) => {
    try {
      const response = await apiService.getWorkflows(params);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch workflows');
    }
  }
);

export const fetchWorkflow = createAsyncThunk(
  'workflow/fetchWorkflow',
  async (id: string, { rejectWithValue }) => {
    try {
      const response = await apiService.getWorkflow(id);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch workflow');
    }
  }
);

export const createWorkflow = createAsyncThunk(
  'workflow/createWorkflow',
  async (data: Partial<Workflow>, { rejectWithValue }) => {
    try {
      const response = await apiService.createWorkflow(data);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to create workflow');
    }
  }
);

export const updateWorkflow = createAsyncThunk(
  'workflow/updateWorkflow',
  async ({ id, data }: { id: string; data: Partial<Workflow> }, { rejectWithValue }) => {
    try {
      const response = await apiService.updateWorkflow(id, data);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to update workflow');
    }
  }
);

export const deleteWorkflow = createAsyncThunk(
  'workflow/deleteWorkflow',
  async (id: string, { rejectWithValue }) => {
    try {
      await apiService.deleteWorkflow(id);
      return id;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to delete workflow');
    }
  }
);

const workflowSlice = createSlice({
  name: 'workflow',
  initialState,
  reducers: {
    setSelectedNode: (state, action: PayloadAction<string | null>) => {
      state.selectedNodeId = action.payload;
    },
    updateCurrentWorkflow: (state, action: PayloadAction<Partial<Workflow>>) => {
      if (state.currentWorkflow) {
        state.currentWorkflow = { ...state.currentWorkflow, ...action.payload };
      }
    },
    addNode: (state, action: PayloadAction<Node>) => {
      if (state.currentWorkflow) {
        if (!state.currentWorkflow.nodes) {
          state.currentWorkflow.nodes = [];
        }
        state.currentWorkflow.nodes.push(action.payload);
      }
    },
    updateNode: (state, action: PayloadAction<{ id: string; updates: Partial<Node> }>) => {
      if (state.currentWorkflow?.nodes) {
        const nodeIndex = state.currentWorkflow.nodes.findIndex(
          (node) => node.id === action.payload.id
        );
        if (nodeIndex !== -1) {
          state.currentWorkflow.nodes[nodeIndex] = {
            ...state.currentWorkflow.nodes[nodeIndex],
            ...action.payload.updates,
          };
        }
      }
    },
    removeNode: (state, action: PayloadAction<string>) => {
      if (state.currentWorkflow?.nodes) {
        state.currentWorkflow.nodes = state.currentWorkflow.nodes.filter(
          (node) => node.id !== action.payload
        );
        // Also remove connections involving this node
        if (state.currentWorkflow.connections) {
          state.currentWorkflow.connections = state.currentWorkflow.connections.filter(
            (conn) =>
              conn.source_node_id !== action.payload && conn.target_node_id !== action.payload
          );
        }
      }
      if (state.selectedNodeId === action.payload) {
        state.selectedNodeId = null;
      }
    },
    addConnection: (state, action: PayloadAction<Connection>) => {
      if (state.currentWorkflow) {
        if (!state.currentWorkflow.connections) {
          state.currentWorkflow.connections = [];
        }
        state.currentWorkflow.connections.push(action.payload);
      }
    },
    removeConnection: (state, action: PayloadAction<string>) => {
      if (state.currentWorkflow?.connections) {
        state.currentWorkflow.connections = state.currentWorkflow.connections.filter(
          (conn) => conn.id !== action.payload
        );
      }
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch workflows
      .addCase(fetchWorkflows.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchWorkflows.fulfilled, (state, action) => {
        state.isLoading = false;
        state.workflows = action.payload;
      })
      .addCase(fetchWorkflows.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Fetch workflow
      .addCase(fetchWorkflow.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchWorkflow.fulfilled, (state, action) => {
        state.isLoading = false;
        state.currentWorkflow = action.payload;
      })
      .addCase(fetchWorkflow.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Create workflow
      .addCase(createWorkflow.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(createWorkflow.fulfilled, (state, action) => {
        state.isLoading = false;
        state.workflows.push(action.payload);
        state.currentWorkflow = action.payload;
      })
      .addCase(createWorkflow.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Update workflow
      .addCase(updateWorkflow.fulfilled, (state, action) => {
        const index = state.workflows.findIndex((w) => w.id === action.payload.id);
        if (index !== -1) {
          state.workflows[index] = action.payload;
        }
        if (state.currentWorkflow?.id === action.payload.id) {
          state.currentWorkflow = action.payload;
        }
      })
      // Delete workflow
      .addCase(deleteWorkflow.fulfilled, (state, action) => {
        state.workflows = state.workflows.filter((w) => w.id !== action.payload);
        if (state.currentWorkflow?.id === action.payload) {
          state.currentWorkflow = null;
        }
      });
  },
});

export const {
  setSelectedNode,
  updateCurrentWorkflow,
  addNode,
  updateNode,
  removeNode,
  addConnection,
  removeConnection,
  clearError,
} = workflowSlice.actions;

export default workflowSlice.reducer;
