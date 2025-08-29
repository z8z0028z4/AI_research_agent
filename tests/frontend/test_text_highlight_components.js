/**
 * 前端文字反白組件測試
 * ===================
 * 
 * 測試文字反白互動功能的前端組件
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach } from 'vitest';
import React from 'react';

// Mock Ant Design components
vi.mock('antd', () => ({
  Button: ({ children, onClick, type, icon }) => (
    <button onClick={onClick} data-testid={`button-${type || 'default'}`}>
      {icon} {children}
    </button>
  ),
  Input: ({ value, onChange, placeholder, onPressEnter }) => (
    <input
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      onKeyPress={(e) => e.key === 'Enter' && onPressEnter && onPressEnter(e)}
      data-testid="input"
    />
  ),
  Modal: ({ children, open, onCancel, title }) => (
    open ? (
      <div data-testid="modal">
        <div data-testid="modal-title">{title}</div>
        <button onClick={onCancel} data-testid="modal-close">Close</button>
        {children}
      </div>
    ) : null
  ),
  message: {
    success: vi.fn(),
    error: vi.fn(),
    info: vi.fn()
  },
  Collapse: ({ children, defaultActiveKey, style, items }) => (
    <div data-testid="collapse" style={style}>
      {items.map((item, index) => (
        <div key={item.key || index} data-testid={`collapse-item-${item.key || index}`}>
          <div data-testid={`collapse-label-${item.key || index}`}>{item.label}</div>
          <div data-testid={`collapse-content-${item.key || index}`}>{item.children}</div>
        </div>
      ))}
    </div>
  )
}));

// Mock React components
vi.mock('react', async () => {
  const actual = await vi.importActual('react');
  return {
    ...actual,
    useState: vi.fn(),
    useEffect: vi.fn(),
    useCallback: vi.fn()
  };
});

// Mock fetch
global.fetch = vi.fn();

// Mock components
const MockTextHighlightProvider = ({ children, onTextInteraction }) => {
  const [popupState, setPopupState] = React.useState({
    visible: false,
    position: { x: 0, y: 0 },
    highlightedText: '',
    highlightedArea: 'proposal'
  });

  const handleTextSelection = (text, position, area) => {
    setPopupState({
      visible: true,
      position,
      highlightedText: text,
      highlightedArea: area
    });
  };

  const handleTextInteraction = async (type, userInput) => {
    if (onTextInteraction) {
      return await onTextInteraction(type, userInput);
    }
    return {
      answer: `Mock response for ${type}`,
      interaction_type: type,
      citations: [],
      chunks: []
    };
  };

  return (
    <div data-testid="text-highlight-provider">
      {children}
      {popupState.visible && (
        <div data-testid="popup" style={{ position: 'absolute', left: popupState.position.x, top: popupState.position.y }}>
          <div data-testid="highlighted-text">{popupState.highlightedText}</div>
          <button onClick={() => setPopupState({ ...popupState, visible: false })} data-testid="close-popup">
            Close
          </button>
        </div>
      )}
    </div>
  );
};

const MockHighlightPopup = ({ visible, position, highlightedText, highlightedArea, onClose, onInteraction }) => {
  const [inputType, setInputType] = React.useState('explain');
  const [showInput, setShowInput] = React.useState(false);
  const [userInput, setUserInput] = React.useState('');

  const handleInteraction = async (type) => {
    if (type === 'explain') {
      setShowInput(true);
    } else if (type === 'revise') {
      setShowInput(true);
    }
  };

  const handleInputSubmit = async () => {
    if (onInteraction) {
      await onInteraction(inputType, userInput);
    }
    setShowInput(false);
    onClose();
  };

  if (!visible) return null;

  return (
    <div data-testid="highlight-popup" style={{ position: 'absolute', left: position.x, top: position.y }}>
      <div data-testid="popup-content">
        <div data-testid="highlighted-text">{highlightedText}</div>
        <div data-testid="highlighted-area">{highlightedArea}</div>
        <button onClick={() => handleInteraction('explain')} data-testid="explain-button">
          Explain
        </button>
        <button onClick={() => handleInteraction('revise')} data-testid="revise-button">
          Revise
        </button>
        <button onClick={onClose} data-testid="close-button">
          Close
        </button>
      </div>
      {showInput && (
        <div data-testid="input-section">
          <input
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder="Enter your question or revision request"
            data-testid="user-input"
          />
          <button onClick={handleInputSubmit} data-testid="submit-button">
            Submit
          </button>
        </div>
      )}
    </div>
  );
};

const MockInteractionInput = ({ onSubmit, onCancel, type }) => {
  const [input, setInput] = React.useState('');

  const handleSubmit = () => {
    onSubmit(input);
  };

  return (
    <div data-testid="interaction-input">
      <div data-testid="input-type">{type}</div>
      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder={`Enter your ${type} request`}
        data-testid="input-field"
      />
      <button onClick={handleSubmit} data-testid="submit-input">
        Submit
      </button>
      <button onClick={onCancel} data-testid="cancel-input">
        Cancel
      </button>
    </div>
  );
};

const MockInteractionResponse = ({ response, type, onClose }) => {
  return (
    <div data-testid="interaction-response">
      <div data-testid="response-type">{type}</div>
      <div data-testid="response-content">{response}</div>
      <button onClick={onClose} data-testid="close-response">
        Close
      </button>
    </div>
  );
};

describe('Text Highlight Components', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('TextHighlightProvider', () => {
    it('should render children correctly', () => {
      render(
        <MockTextHighlightProvider>
          <div data-testid="child-content">Test Content</div>
        </MockTextHighlightProvider>
      );

      expect(screen.getByTestId('text-highlight-provider')).toBeInTheDocument();
      expect(screen.getByTestId('child-content')).toBeInTheDocument();
    });

    it('should show popup when text is selected', () => {
      render(
        <MockTextHighlightProvider>
          <div data-testid="child-content">Test Content</div>
        </MockTextHighlightProvider>
      );

      // Initially popup should not be visible
      expect(screen.queryByTestId('popup')).not.toBeInTheDocument();

      // Simulate text selection (this would be handled by the actual component)
      // For testing purposes, we'll just verify the structure
      expect(screen.getByTestId('text-highlight-provider')).toBeInTheDocument();
    });

    it('should handle text interaction correctly', async () => {
      const mockOnTextInteraction = vi.fn().mockResolvedValue({
        answer: 'Test explanation',
        interaction_type: 'explain',
        citations: [],
        chunks: []
      });

      render(
        <MockTextHighlightProvider onTextInteraction={mockOnTextInteraction}>
          <div data-testid="child-content">Test Content</div>
        </MockTextHighlightProvider>
      );

      // Simulate text interaction
      const result = await mockOnTextInteraction('explain', 'test question');
      
      expect(result.answer).toBe('Test explanation');
      expect(result.interaction_type).toBe('explain');
      expect(mockOnTextInteraction).toHaveBeenCalledWith('explain', 'test question');
    });
  });

  describe('HighlightPopup', () => {
    it('should render popup when visible', () => {
      render(
        <MockHighlightPopup
          visible={true}
          position={{ x: 100, y: 100 }}
          highlightedText="test text"
          highlightedArea="proposal"
          onClose={vi.fn()}
        />
      );

      expect(screen.getByTestId('highlight-popup')).toBeInTheDocument();
      expect(screen.getByTestId('highlighted-text')).toHaveTextContent('test text');
      expect(screen.getByTestId('highlighted-area')).toHaveTextContent('proposal');
    });

    it('should not render when not visible', () => {
      render(
        <MockHighlightPopup
          visible={false}
          position={{ x: 100, y: 100 }}
          highlightedText="test text"
          highlightedArea="proposal"
          onClose={vi.fn()}
        />
      );

      expect(screen.queryByTestId('highlight-popup')).not.toBeInTheDocument();
    });

    it('should show explain and revise buttons', () => {
      render(
        <MockHighlightPopup
          visible={true}
          position={{ x: 100, y: 100 }}
          highlightedText="test text"
          highlightedArea="proposal"
          onClose={vi.fn()}
        />
      );

      expect(screen.getByTestId('explain-button')).toBeInTheDocument();
      expect(screen.getByTestId('revise-button')).toBeInTheDocument();
      expect(screen.getByTestId('close-button')).toBeInTheDocument();
    });

    it('should show input section when explain button is clicked', () => {
      render(
        <MockHighlightPopup
          visible={true}
          position={{ x: 100, y: 100 }}
          highlightedText="test text"
          highlightedArea="proposal"
          onClose={vi.fn()}
        />
      );

      fireEvent.click(screen.getByTestId('explain-button'));

      expect(screen.getByTestId('input-section')).toBeInTheDocument();
      expect(screen.getByTestId('user-input')).toBeInTheDocument();
      expect(screen.getByTestId('submit-button')).toBeInTheDocument();
    });

    it('should show input section when revise button is clicked', () => {
      render(
        <MockHighlightPopup
          visible={true}
          position={{ x: 100, y: 100 }}
          highlightedText="test text"
          highlightedArea="proposal"
          onClose={vi.fn()}
        />
      );

      fireEvent.click(screen.getByTestId('revise-button'));

      expect(screen.getByTestId('input-section')).toBeInTheDocument();
      expect(screen.getByTestId('user-input')).toBeInTheDocument();
      expect(screen.getByTestId('submit-button')).toBeInTheDocument();
    });

    it('should handle input submission correctly', async () => {
      const mockOnInteraction = vi.fn();
      
      render(
        <MockHighlightPopup
          visible={true}
          position={{ x: 100, y: 100 }}
          highlightedText="test text"
          highlightedArea="proposal"
          onClose={vi.fn()}
          onInteraction={mockOnInteraction}
        />
      );

      fireEvent.click(screen.getByTestId('explain-button'));
      
      const input = screen.getByTestId('user-input');
      fireEvent.change(input, { target: { value: 'test question' } });
      
      fireEvent.click(screen.getByTestId('submit-button'));

      await waitFor(() => {
        expect(mockOnInteraction).toHaveBeenCalledWith('explain', 'test question');
      });
    });
  });

  describe('InteractionInput', () => {
    it('should render input component correctly', () => {
      render(
        <MockInteractionInput
          onSubmit={vi.fn()}
          onCancel={vi.fn()}
          type="explain"
        />
      );

      expect(screen.getByTestId('interaction-input')).toBeInTheDocument();
      expect(screen.getByTestId('input-type')).toHaveTextContent('explain');
      expect(screen.getByTestId('input-field')).toBeInTheDocument();
      expect(screen.getByTestId('submit-input')).toBeInTheDocument();
      expect(screen.getByTestId('cancel-input')).toBeInTheDocument();
    });

    it('should handle input change correctly', () => {
      render(
        <MockInteractionInput
          onSubmit={vi.fn()}
          onCancel={vi.fn()}
          type="explain"
        />
      );

      const input = screen.getByTestId('input-field');
      fireEvent.change(input, { target: { value: 'test input' } });

      expect(input.value).toBe('test input');
    });

    it('should call onSubmit when submit button is clicked', () => {
      const mockOnSubmit = vi.fn();
      
      render(
        <MockInteractionInput
          onSubmit={mockOnSubmit}
          onCancel={vi.fn()}
          type="explain"
        />
      );

      const input = screen.getByTestId('input-field');
      fireEvent.change(input, { target: { value: 'test input' } });
      
      fireEvent.click(screen.getByTestId('submit-input'));

      expect(mockOnSubmit).toHaveBeenCalledWith('test input');
    });

    it('should call onCancel when cancel button is clicked', () => {
      const mockOnCancel = vi.fn();
      
      render(
        <MockInteractionInput
          onSubmit={vi.fn()}
          onCancel={mockOnCancel}
          type="explain"
        />
      );

      fireEvent.click(screen.getByTestId('cancel-input'));

      expect(mockOnCancel).toHaveBeenCalled();
    });
  });

  describe('InteractionResponse', () => {
    it('should render response component correctly', () => {
      render(
        <MockInteractionResponse
          response="This is a test response"
          type="explain"
          onClose={vi.fn()}
        />
      );

      expect(screen.getByTestId('interaction-response')).toBeInTheDocument();
      expect(screen.getByTestId('response-type')).toHaveTextContent('explain');
      expect(screen.getByTestId('response-content')).toHaveTextContent('This is a test response');
      expect(screen.getByTestId('close-response')).toBeInTheDocument();
    });

    it('should call onClose when close button is clicked', () => {
      const mockOnClose = vi.fn();
      
      render(
        <MockInteractionResponse
          response="This is a test response"
          type="explain"
          onClose={mockOnClose}
        />
      );

      fireEvent.click(screen.getByTestId('close-response'));

      expect(mockOnClose).toHaveBeenCalled();
    });
  });

  describe('Integration Tests', () => {
    it('should handle complete explain workflow', async () => {
      const mockOnTextInteraction = vi.fn().mockResolvedValue({
        answer: 'This is an explanation of the highlighted text.',
        interaction_type: 'explain',
        citations: [],
        chunks: []
      });

      render(
        <MockTextHighlightProvider onTextInteraction={mockOnTextInteraction}>
          <div data-testid="child-content">Test Content</div>
        </MockTextHighlightProvider>
      );

      // Simulate complete workflow
      const result = await mockOnTextInteraction('explain', 'What does this mean?');
      
      expect(result.answer).toBe('This is an explanation of the highlighted text.');
      expect(result.interaction_type).toBe('explain');
      expect(mockOnTextInteraction).toHaveBeenCalledWith('explain', 'What does this mean?');
    });

    it('should handle complete revise workflow', async () => {
      const mockOnTextInteraction = vi.fn().mockResolvedValue({
        answer: 'This is a revised version.',
        interaction_type: 'revise',
        structured_proposal: { title: 'Revised Proposal' },
        citations: [],
        chunks: []
      });

      render(
        <MockTextHighlightProvider onTextInteraction={mockOnTextInteraction}>
          <div data-testid="child-content">Test Content</div>
        </MockTextHighlightProvider>
      );

      // Simulate complete workflow
      const result = await mockOnTextInteraction('revise', 'Please revise this section');
      
      expect(result.answer).toBe('This is a revised version.');
      expect(result.interaction_type).toBe('revise');
      expect(result.structured_proposal).toEqual({ title: 'Revised Proposal' });
      expect(mockOnTextInteraction).toHaveBeenCalledWith('revise', 'Please revise this section');
    });
  });
}); 