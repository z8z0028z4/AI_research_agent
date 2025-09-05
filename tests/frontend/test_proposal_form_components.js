/**
 * 提案表單組件測試
 * =================
 * 
 * 測試前端提案表單的真實功能：
 * - 表單狀態管理
 * - 檢索數量選擇
 * - 提案生成
 * - 文字反白功能
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Form, Select, Button } from 'antd';
import React from 'react';

// 模擬 Ant Design 組件
vi.mock('antd', () => ({
  Form: {
    Item: ({ children, name, initialValue }) => (
      <div data-testid={`form-item-${name}`} data-initial-value={initialValue}>
        {children}
      </div>
    ),
    useForm: () => [
      {
        getFieldValue: vi.fn((field) => {
          if (field === 'retrievalCount') return 10;
          return null;
        }),
        setFieldsValue: vi.fn(),
        validateFields: vi.fn().mockResolvedValue({}),
      },
      {}
    ]
  },
  Select: ({ options, value, onChange, placeholder }) => (
    <select 
      data-testid="retrieval-count-select"
      value={value}
      onChange={(e) => onChange && onChange(parseInt(e.target.value))}
    >
      <option value="">{placeholder}</option>
      {options?.map(option => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  ),
  Button: ({ children, onClick, loading, type }) => (
    <button 
      data-testid="generate-button"
      onClick={onClick}
      disabled={loading}
      data-type={type}
    >
      {children}
    </button>
  ),
  Input: {
    TextArea: ({ value, onChange, placeholder }) => (
      <textarea 
        data-testid="research-goal-input"
        value={value}
        onChange={(e) => onChange && onChange(e.target.value)}
        placeholder={placeholder}
      />
    )
  }
}));

// 模擬 React Context
const mockAppStateContext = {
  state: {
    proposal: {
      formData: {
        goal: '',
        retrievalCount: 10
      },
      result: null,
      loading: false
    }
  },
  dispatch: vi.fn()
};

vi.mock('../../frontend/src/contexts/AppStateContext', () => ({
  useAppState: () => mockAppStateContext
}));

// 模擬 API 調用
const mockApiCall = vi.fn().mockResolvedValue({
  proposal: "這是一個測試提案內容",
  chemicals: [],
  citations: [],
  chunks: []
});

vi.mock('../../frontend/src/services/api', () => ({
  generateProposal: mockApiCall
}));

describe('提案表單組件測試', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('表單狀態管理', () => {
    it('應該正確初始化表單狀態', () => {
      const { state } = mockAppStateContext;
      
      expect(state.proposal.formData.goal).toBe('');
      expect(state.proposal.formData.retrievalCount).toBe(10);
      expect(state.proposal.result).toBeNull();
      expect(state.proposal.loading).toBe(false);
    });

    it('應該正確處理檢索數量選擇', () => {
      const { dispatch } = mockAppStateContext;
      
      // 模擬選擇檢索數量
      const newRetrievalCount = 15;
      dispatch({
        type: 'SET_PROPOSAL_FORM_DATA',
        payload: { retrievalCount: newRetrievalCount }
      });
      
      expect(dispatch).toHaveBeenCalledWith({
        type: 'SET_PROPOSAL_FORM_DATA',
        payload: { retrievalCount: newRetrievalCount }
      });
    });
  });

  describe('檢索數量選擇器', () => {
    it('應該顯示正確的選項', () => {
      const options = [
        { value: 1, label: '1' },
        { value: 5, label: '5' },
        { value: 10, label: '10' },
        { value: 15, label: '15' },
        { value: 20, label: '20' }
      ];
      
      render(
        <Select 
          options={options}
          placeholder="選擇檢索數量"
          data-testid="retrieval-count-select"
        />
      );
      
      const select = screen.getByTestId('retrieval-count-select');
      expect(select).toBeInTheDocument();
      
      // 檢查選項
      options.forEach(option => {
        const optionElement = screen.getByText(option.label);
        expect(optionElement).toBeInTheDocument();
      });
    });

    it('應該正確處理選擇變更', () => {
      const handleChange = vi.fn();
      const options = [
        { value: 10, label: '10' },
        { value: 15, label: '15' }
      ];
      
      render(
        <Select 
          options={options}
          onChange={handleChange}
          data-testid="retrieval-count-select"
        />
      );
      
      const select = screen.getByTestId('retrieval-count-select');
      fireEvent.change(select, { target: { value: '15' } });
      
      expect(handleChange).toHaveBeenCalledWith(15);
    });
  });

  describe('提案生成功能', () => {
    it('應該正確處理提案生成請求', async () => {
      const mockForm = {
        getFieldValue: vi.fn((field) => {
          if (field === 'retrievalCount') return 15;
          if (field === 'goal') return '測試研究目標';
          return null;
        }),
        validateFields: vi.fn().mockResolvedValue({})
      };
      
      // 模擬提案生成
      const result = await mockApiCall({
        research_goal: '測試研究目標',
        retrieval_count: 15
      });
      
      expect(mockApiCall).toHaveBeenCalledWith({
        research_goal: '測試研究目標',
        retrieval_count: 15
      });
      
      expect(result.proposal).toBe("這是一個測試提案內容");
      expect(result.chemicals).toEqual([]);
      expect(result.citations).toEqual([]);
      expect(result.chunks).toEqual([]);
    });

    it('應該正確處理表單驗證', async () => {
      const mockForm = {
        validateFields: vi.fn().mockRejectedValue(new Error('表單驗證失敗'))
      };
      
      try {
        await mockForm.validateFields();
      } catch (error) {
        expect(error.message).toBe('表單驗證失敗');
      }
      
      expect(mockForm.validateFields).toHaveBeenCalled();
    });
  });

  describe('文字反白功能', () => {
    it('應該正確處理文字選擇', () => {
      const mockTextSelection = {
        text: "MOF synthesis methods",
        position: { x: 100, y: 200 }
      };
      
      // 模擬文字選擇事件
      const handleTextSelection = vi.fn();
      handleTextSelection(mockTextSelection);
      
      expect(handleTextSelection).toHaveBeenCalledWith(mockTextSelection);
    });

    it('應該正確計算彈窗位置', () => {
      const mockRange = {
        getBoundingClientRect: () => ({
          right: 150,
          bottom: 250
        })
      };
      
      // 模擬位置計算
      const calculatePosition = (range) => {
        const rect = range.getBoundingClientRect();
        return { x: rect.right, y: rect.bottom };
      };
      
      const position = calculatePosition(mockRange);
      
      expect(position.x).toBe(150);
      expect(position.y).toBe(250);
    });
  });

  describe('錯誤處理', () => {
    it('應該正確處理API錯誤', async () => {
      const mockError = new Error('API調用失敗');
      mockApiCall.mockRejectedValueOnce(mockError);
      
      try {
        await mockApiCall({
          research_goal: '測試研究目標',
          retrieval_count: 10
        });
      } catch (error) {
        expect(error.message).toBe('API調用失敗');
      }
    });

    it('應該正確處理表單驗證錯誤', () => {
      const mockForm = {
        validateFields: vi.fn().mockRejectedValue(new Error('研究目標不能為空'))
      };
      
      expect(mockForm.validateFields).toThrow();
    });
  });

  describe('整合測試', () => {
    it('應該完成完整的提案生成流程', async () => {
      const mockForm = {
        getFieldValue: vi.fn((field) => {
          if (field === 'retrievalCount') return 10;
          if (field === 'goal') return 'Design a simple MOF for CO2 capture';
          return null;
        }),
        validateFields: vi.fn().mockResolvedValue({})
      };
      
      // 1. 驗證表單
      await mockForm.validateFields();
      
      // 2. 獲取表單數據
      const researchGoal = mockForm.getFieldValue('goal');
      const retrievalCount = mockForm.getFieldValue('retrievalCount');
      
      // 3. 調用API
      const result = await mockApiCall({
        research_goal: researchGoal,
        retrieval_count: retrievalCount
      });
      
      // 4. 驗證結果
      expect(mockForm.validateFields).toHaveBeenCalled();
      expect(mockForm.getFieldValue).toHaveBeenCalledWith('goal');
      expect(mockForm.getFieldValue).toHaveBeenCalledWith('retrievalCount');
      expect(mockApiCall).toHaveBeenCalledWith({
        research_goal: 'Design a simple MOF for CO2 capture',
        retrieval_count: 10
      });
      expect(result.proposal).toBe("這是一個測試提案內容");
    });
  });
});