// frontend/src/hooks/useWorkflow.ts
import { useCallback } from 'react';
import { useAppDispatch, useAppSelector } from '../store';
import {
  fetchWorkflows,
  fetchWorkflow,
  createWorkflow,
  updateWorkflow,
  deleteWorkflow,
  setSelectedNode,
  addNode,
  updateNode,
  removeNode,
  addConnection,
  removeConnection,
} from '../store/workflowSlice';

export const useWorkflow = () => {
  const dispatch = useAppDispatch();
  const workflow = useAppSelector((state) => state.workflow);

  const actions = {
    fetchWorkflows: useCallback((params?: any) => {
      return dispatch(fetchWorkflows(params));
    }, [dispatch]),

    fetchWorkflow: useCallback((id: string) => {
      return dispatch(fetchWorkflow(id));
    }, [dispatch]),

    createWorkflow: useCallback((data: any) => {
      return dispatch(createWorkflow(data));
    }, [dispatch]),

    updateWorkflow: useCallback((id: string, data: any) => {
      return dispatch(updateWorkflow({ id, data }));
    }, [dispatch]),

    deleteWorkflow: useCallback((id: string) => {
      return dispatch(deleteWorkflow(id));
    }, [dispatch]),

    setSelectedNode: useCallback((nodeId: string | null) => {
      dispatch(setSelectedNode(nodeId));
    }, [dispatch]),

    addNode: useCallback((node: any) => {
      dispatch(addNode(node));
    }, [dispatch]),

    updateNode: useCallback((id: string, updates: any) => {
      dispatch(updateNode({ id, updates }));
    }, [dispatch]),

    removeNode: useCallback((id: string) => {
      dispatch(removeNode(id));
    }, [dispatch]),

    addConnection: useCallback((connection: any) => {
      dispatch(addConnection(connection));
    }, [dispatch]),

    removeConnection: useCallback((id: string) => {
      dispatch(removeConnection(id));
    }, [dispatch]),
  };

  return {
    ...workflow,
    actions,
  };
};