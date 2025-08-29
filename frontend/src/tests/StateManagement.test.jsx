/**
 * 狀態管理功能測試
 * 
 * 測試以下功能：
 * - 狀態保存和恢復
 * - 跨頁面數據持久化
 * - 數據導出/導入
 * - 清除功能
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AppStateProvider } from '../contexts/AppStateContext';
import { TextHighlightProvider } from '../components/TextHighlight/TextHighlightProvider';
import StateManager from '../components/common/StateManager';

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

// 測試用的Wrapper組件
const TestWrapper = ({ children }) => (
  <BrowserRouter>
    <AppStateProvider>
      <TextHighlightProvider>
        {children}
      </TextHighlightProvider>
    </AppStateProvider>
  </BrowserRouter>
);

describe('State Management', () => {
  beforeEach(() => {
    localStorageMock.getItem.mockClear();
    localStorageMock.setItem.mockClear();
    localStorageMock.removeItem.mockClear();
  });

  test('should save state to localStorage', async () => {
    render(
      <TestWrapper>
        <StateManager />
      </TestWrapper>
    );

    // 點擊狀態管理按鈕
    const stateManagerButton = screen.getByText('狀態管理');
    fireEvent.click(stateManagerButton);

    // 等待模態框出現
    await waitFor(() => {
      expect(screen.getByText('數據統計')).toBeInTheDocument();
    });

    // 驗證localStorage被調用
    expect(localStorageMock.setItem).toHaveBeenCalled();
  });

  test('should load state from localStorage on mount', () => {
    const mockState = {
      proposal: {
        formData: { goal: 'Test goal' },
        proposal: 'Test proposal',
        hasGeneratedContent: true
      },
      search: {
        searchQuery: 'Test query',
        hasSearched: true
      },
      knowledgeQuery: {
        formData: { question: 'Test question' },
        hasQueried: true
      },
      settings: {
        lastActiveTab: '/',
        autoSave: true
      }
    };

    localStorageMock.getItem.mockReturnValue(JSON.stringify(mockState));

    render(
      <TestWrapper>
        <StateManager />
      </TestWrapper>
    );

    // 驗證localStorage.getItem被調用
    expect(localStorageMock.getItem).toHaveBeenCalledWith('ai_research_app_state');
  });

  test('should export data correctly', async () => {
    // Mock URL.createObjectURL and URL.revokeObjectURL
    const mockCreateObjectURL = jest.fn(() => 'mock-url');
    const mockRevokeObjectURL = jest.fn();
    global.URL.createObjectURL = mockCreateObjectURL;
    global.URL.revokeObjectURL = mockRevokeObjectURL;

    // Mock document.createElement and appendChild
    const mockAnchor = {
      href: '',
      download: '',
      click: jest.fn(),
    };
    const mockAppendChild = jest.fn();
    const mockRemoveChild = jest.fn();
    document.createElement = jest.fn(() => mockAnchor);
    document.body.appendChild = mockAppendChild;
    document.body.removeChild = mockRemoveChild;

    render(
      <TestWrapper>
        <StateManager />
      </TestWrapper>
    );

    // 點擊狀態管理按鈕
    const stateManagerButton = screen.getByText('狀態管理');
    fireEvent.click(stateManagerButton);

    // 等待模態框出現並點擊導出按鈕
    await waitFor(() => {
      const exportButton = screen.getByText('導出所有數據');
      fireEvent.click(exportButton);
    });

    // 驗證導出功能被調用
    expect(mockCreateObjectURL).toHaveBeenCalled();
    expect(mockAnchor.click).toHaveBeenCalled();
  });

  test('should clear data correctly', async () => {
    render(
      <TestWrapper>
        <StateManager />
      </TestWrapper>
    );

    // 點擊狀態管理按鈕
    const stateManagerButton = screen.getByText('狀態管理');
    fireEvent.click(stateManagerButton);

    // 等待模態框出現並點擊清除所有數據按鈕
    await waitFor(() => {
      const clearAllButton = screen.getByText('清除所有數據');
      fireEvent.click(clearAllButton);
    });

    // 等待確認對話框出現
    await waitFor(() => {
      expect(screen.getByText('確認清除')).toBeInTheDocument();
    });

    // 點擊確認按鈕
    const confirmButton = screen.getByText('確認');
    fireEvent.click(confirmButton);

    // 驗證localStorage.removeItem被調用
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('ai_research_app_state');
  });
}); 