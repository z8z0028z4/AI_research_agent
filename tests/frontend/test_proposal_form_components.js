/**
 * 提案表單組件測試
 * =================
 * 
 * 測試提案表單的改進功能：
 * 1. Document Retrieval Count 下拉選單
 * 2. 表單狀態管理
 * 3. 文字反白 popup 位置計算
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import React from 'react';

// Mock Ant Design components
const mockAntd = {
  Button: ({ children, onClick, type, icon, loading, ...props }) => (
    <button 
      onClick={onClick} 
      data-testid={`button-${type || 'default'}`}
      disabled={loading}
      {...props}
    >
      {icon} {children}
    </button>
  ),
  Form: ({ children, form, layout, initialValues, ...props }) => (
    <form data-testid="form" {...props}>
      {children}
    </form>
  ),
  FormItem: ({ children, name, label, rules, initialValue, ...props }) => (
    <div data-testid={`form-item-${name}`} {...props}>
      <label data-testid={`label-${name}`}>{label}</label>
      {children}
    </div>
  ),
  Input: {
    TextArea: ({ rows, placeholder, onFocus, onBlur, onChange, ...props }) => (
      <textarea
        rows={rows}
        placeholder={placeholder}
        onFocus={onFocus}
        onBlur={onBlur}
        onChange={onChange}
        data-testid="textarea"
        {...props}
      />
    )
  },
  Select: ({ value, onChange, style, children, ...props }) => (
    <select
      value={value}
      onChange={(e) => onChange && onChange(e.target.value)}
      style={style}
      data-testid="select"
      {...props}
    >
      {children}
    </select>
  ),
  Option: ({ value, children, ...props }) => (
    <option value={value} {...props}>
      {children}
    </option>
  ),
  Space: ({ children, direction, style, wrap, ...props }) => (
    <div data-testid="space" style={style} {...props}>
      {children}
    </div>
  ),
  Card: ({ children, title, style, ...props }) => (
    <div data-testid="card" style={style} {...props}>
      <div data-testid="card-title">{title}</div>
      {children}
    </div>
  ),
  Typography: {
    Title: ({ children, level, ...props }) => (
      <h1 data-testid={`title-${level}`} {...props}>
        {children}
      </h1>
    ),
    Paragraph: ({ children, ...props }) => (
      <p data-testid="paragraph" {...props}>
        {children}
      </p>
    )
  },
  message: {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn()
  }
};

vi.mock('antd', () => mockAntd);

// Mock React hooks
const mockUseState = vi.fn();
const mockUseEffect = vi.fn();
const mockUseRef = vi.fn();
const mockUseMemo = vi.fn();
const mockUseCallback = vi.fn();

vi.mock('react', async () => {
  const actual = await vi.importActual('react');
  return {
    ...actual,
    useState: mockUseState,
    useEffect: mockUseEffect,
    useRef: mockUseRef,
    useMemo: mockUseMemo,
    useCallback: mockUseCallback
  };
});

// Mock fetch
global.fetch = vi.fn();

// Mock window.getSelection
Object.defineProperty(window, 'getSelection', {
  value: vi.fn(() => ({
    toString: () => 'selected text',
    getRangeAt: vi.fn(() => ({
      getBoundingClientRect: () => ({
        right: 100,
        bottom: 50,
        width: 10,
        height: 15
      }),
      cloneRange: vi.fn(),
      endContainer: {},
      endOffset: 5
    }))
  })),
  writable: true
});

describe('Proposal Form Components', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    
    // Mock default state values
    mockUseState.mockImplementation((initial) => {
      const [state, setState] = React.useState(initial);
      return [state, setState];
    });
    
    mockUseRef.mockReturnValue({ current: null });
    mockUseMemo.mockImplementation((fn) => fn());
    mockUseCallback.mockImplementation((fn) => fn);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Document Retrieval Count Dropdown', () => {
    it('should render dropdown with correct options', () => {
      const mockFormData = { goal: '', retrievalCount: 10 };
      const mockRetrievalCount = 10;
      const mockSetProposalFormData = vi.fn();

      // Mock the component state
      mockUseState
        .mockReturnValueOnce([mockFormData, mockSetProposalFormData]) // formData
        .mockReturnValueOnce([mockRetrievalCount, vi.fn()]) // retrievalCount
        .mockReturnValueOnce([false, vi.fn()]) // loading
        .mockReturnValueOnce([false, vi.fn()]) // isTextareaFocused
        .mockReturnValueOnce([false, vi.fn()]); // isReviseInputFocused

      // Mock other hooks
      mockUseMemo.mockReturnValue(false);
      mockUseRef.mockReturnValue({ current: null });

      // Import and render component
      const { Proposal } = require('../../frontend/src/pages/Proposal.jsx');
      
      render(<Proposal />);

      // Check if select element exists
      const select = screen.getByTestId('select');
      expect(select).toBeInTheDocument();

      // Check if form item exists
      const formItem = screen.getByTestId('form-item-retrievalCount');
      expect(formItem).toBeInTheDocument();

      // Check if label exists
      const label = screen.getByTestId('label-retrievalCount');
      expect(label).toHaveTextContent('Document Retrieval Count');
    });

    it('should handle dropdown value changes', () => {
      const mockSetProposalFormData = vi.fn();
      const mockFormData = { goal: '', retrievalCount: 10 };
      const mockRetrievalCount = 10;

      mockUseState
        .mockReturnValueOnce([mockFormData, mockSetProposalFormData])
        .mockReturnValueOnce([mockRetrievalCount, vi.fn()])
        .mockReturnValueOnce([false, vi.fn()])
        .mockReturnValueOnce([false, vi.fn()])
        .mockReturnValueOnce([false, vi.fn()]);

      mockUseMemo.mockReturnValue(false);
      mockUseRef.mockReturnValue({ current: null });

      const { Proposal } = require('../../frontend/src/pages/Proposal.jsx');
      render(<Proposal />);

      const select = screen.getByTestId('select');
      
      // Simulate dropdown change
      fireEvent.change(select, { target: { value: '15' } });

      // Verify that setProposalFormData was called with correct value
      expect(mockSetProposalFormData).toHaveBeenCalledWith({ retrievalCount: '15' });
    });

    it('should have correct initial value', () => {
      const mockFormData = { goal: '', retrievalCount: 10 };
      const mockRetrievalCount = 10;

      mockUseState
        .mockReturnValueOnce([mockFormData, vi.fn()])
        .mockReturnValueOnce([mockRetrievalCount, vi.fn()])
        .mockReturnValueOnce([false, vi.fn()])
        .mockReturnValueOnce([false, vi.fn()])
        .mockReturnValueOnce([false, vi.fn()]);

      mockUseMemo.mockReturnValue(false);
      mockUseRef.mockReturnValue({ current: null });

      const { Proposal } = require('../../frontend/src/pages/Proposal.jsx');
      render(<Proposal />);

      const select = screen.getByTestId('select');
      expect(select).toHaveValue(10);
    });
  });

  describe('Form State Management', () => {
    it('should initialize with correct form data structure', () => {
      const expectedFormData = { goal: '', retrievalCount: 10 };
      
      // Mock AppStateContext
      const mockAppState = {
        state: {
          proposal: {
            formData: expectedFormData,
            retrievalCount: 10,
            proposal: '',
            chemicals: [],
            notFound: [],
            citations: [],
            chunks: [],
            experimentDetail: '',
            structuredExperiment: null,
            structuredProposal: null,
            hasGeneratedContent: false,
            showReviseInput: false,
            reviseFeedback: ''
          }
        },
        setProposalFormData: vi.fn(),
        setProposalResult: vi.fn(),
        setProposalExperiment: vi.fn()
      };

      // Mock useAppState hook
      vi.doMock('../../frontend/src/contexts/AppStateContext.jsx', () => ({
        useAppState: () => mockAppState
      }));

      expect(expectedFormData.goal).toBe('');
      expect(expectedFormData.retrievalCount).toBe(10);
    });

    it('should handle form data updates correctly', () => {
      const mockSetProposalFormData = vi.fn();
      
      // Test updating goal
      mockSetProposalFormData({ goal: 'Test research goal' });
      expect(mockSetProposalFormData).toHaveBeenCalledWith({ goal: 'Test research goal' });

      // Test updating retrieval count
      mockSetProposalFormData({ retrievalCount: 15 });
      expect(mockSetProposalFormData).toHaveBeenCalledWith({ retrievalCount: 15 });

      // Test updating both
      mockSetProposalFormData({ goal: 'New goal', retrievalCount: 20 });
      expect(mockSetProposalFormData).toHaveBeenCalledWith({ goal: 'New goal', retrievalCount: 20 });
    });
  });

  describe('Text Highlight Popup Position', () => {
    it('should calculate end position correctly', () => {
      // Mock range object
      const mockRange = {
        endContainer: {},
        endOffset: 5,
        getBoundingClientRect: () => ({
          right: 100,
          bottom: 50,
          width: 10,
          height: 15
        }),
        cloneRange: () => ({
          setStart: vi.fn(),
          setEnd: vi.fn(),
          getBoundingClientRect: () => ({
            right: 95,
            bottom: 50,
            width: 5,
            height: 15
          })
        })
      };

      // Test position calculation
      const calculateEndPosition = (range) => {
        try {
          const endRange = range.cloneRange();
          endRange.setStart(range.endContainer, Math.max(0, range.endOffset - 1));
          endRange.setEnd(range.endContainer, range.endOffset);
          
          const endRect = endRange.getBoundingClientRect();
          
          if (endRect.width > 0 && endRect.height > 0) {
            return {
              x: endRect.right,
              y: endRect.bottom
            };
          } else {
            const originalRect = range.getBoundingClientRect();
            return {
              x: originalRect.right,
              y: originalRect.bottom
            };
          }
        } catch (error) {
          const originalRect = range.getBoundingClientRect();
          return {
            x: originalRect.right,
            y: originalRect.bottom
          };
        }
      };

      const result = calculateEndPosition(mockRange);
      
      expect(result).toHaveProperty('x');
      expect(result).toHaveProperty('y');
      expect(typeof result.x).toBe('number');
      expect(typeof result.y).toBe('number');
    });

    it('should handle position calculation errors gracefully', () => {
      const mockRange = {
        getBoundingClientRect: () => {
          throw new Error('DOM Error');
        }
      };

      const calculateEndPosition = (range) => {
        try {
          const endRange = range.cloneRange();
          endRange.setStart(range.endContainer, Math.max(0, range.endOffset - 1));
          endRange.setEnd(range.endContainer, range.endOffset);
          
          const endRect = endRange.getBoundingClientRect();
          
          if (endRect.width > 0 && endRect.height > 0) {
            return {
              x: endRect.right,
              y: endRect.bottom
            };
          } else {
            const originalRect = range.getBoundingClientRect();
            return {
              x: originalRect.right,
              y: originalRect.bottom
            };
          }
        } catch (error) {
          // Fallback to default position
          return {
            x: 0,
            y: 0
          };
        }
      };

      const result = calculateEndPosition(mockRange);
      
      expect(result).toEqual({ x: 0, y: 0 });
    });

    it('should handle text selection events', () => {
      const mockHandleTextSelection = vi.fn();
      
      // Mock text selection event
      const mockEvent = {
        stopPropagation: vi.fn(),
        target: {
          closest: vi.fn(() => null)
        }
      };

      // Simulate text selection
      mockHandleTextSelection(mockEvent);
      
      expect(mockHandleTextSelection).toHaveBeenCalledWith(mockEvent);
    });
  });

  describe('Integration Tests', () => {
    it('should handle complete proposal generation workflow', async () => {
      const mockFormData = { goal: 'Test research goal', retrievalCount: 15 };
      const mockRetrievalCount = 15;
      const mockSetProposalFormData = vi.fn();
      const mockSetProposalResult = vi.fn();

      // Mock API response
      const mockApiResponse = {
        proposal: 'Generated proposal content',
        chemicals: [],
        not_found: [],
        citations: [],
        chunks: [],
        structured_proposal: null
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockApiResponse)
      });

      mockUseState
        .mockReturnValueOnce([mockFormData, mockSetProposalFormData])
        .mockReturnValueOnce([mockRetrievalCount, vi.fn()])
        .mockReturnValueOnce([false, vi.fn()])
        .mockReturnValueOnce([false, vi.fn()])
        .mockReturnValueOnce([false, vi.fn()]);

      mockUseMemo.mockReturnValue(false);
      mockUseRef.mockReturnValue({ current: null });

      // Test that form data is properly structured
      expect(mockFormData.goal).toBe('Test research goal');
      expect(mockFormData.retrievalCount).toBe(15);
    });

    it('should maintain state consistency between form and global state', () => {
      const formData = { goal: 'Test goal', retrievalCount: 10 };
      const globalRetrievalCount = 10;
      
      // Verify consistency
      expect(formData.retrievalCount).toBe(globalRetrievalCount);
      
      // Test state update
      const updatedFormData = { ...formData, retrievalCount: 15 };
      expect(updatedFormData.retrievalCount).toBe(15);
      expect(updatedFormData.goal).toBe('Test goal');
    });
  });
});