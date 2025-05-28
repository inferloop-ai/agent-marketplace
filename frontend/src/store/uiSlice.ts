/**
 * UI-related state and actions
 *
 * This slice manages the UI-related state such as the currently selected node or the visibility of the settings panel.
 */

import { createSlice } from '@reduxjs/toolkit';

export interface UiState {
  selectedNodeId: string | null;
  isSettingsPanelVisible: boolean;
}

const initialState: UiState = {
  selectedNodeId: null,
  isSettingsPanelVisible: false,
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    selectNode: (state, action: PayloadAction<string | null>) => {
      state.selectedNodeId = action.payload;
    },
    toggleSettingsPanel: (state) => {
      state.isSettingsPanelVisible = !state.isSettingsPanelVisible;
    },
  },
});

export const { selectNode, toggleSettingsPanel } = uiSlice.actions;

export default uiSlice.reducer;
