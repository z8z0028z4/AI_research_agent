/**
 * 文字反白上下文提供者
 * 
 * 負責管理全局的文字反白狀態，包括：
 * - 反白文字內容
 * - 彈窗位置和顯示狀態
 * - 互動歷史記錄
 * - 全局事件監聽
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { message } from 'antd';

const TextHighlightContext = createContext();

export const useTextHighlight = () => {
  const context = useContext(TextHighlightContext);
  if (!context) {
    throw new Error('useTextHighlight must be used within a TextHighlightProvider');
  }
  return context;
};

export const TextHighlightProvider = ({ children }) => {
  // 反白狀態
  const [highlightedText, setHighlightedText] = useState('');
  const [contextParagraph, setContextParagraph] = useState('');
  const [fullText, setFullText] = useState('');
  const [highlightedArea, setHighlightedArea] = useState('proposal'); // 🔍 [NEW] 反白區域
  
  // 彈窗狀態
  const [showPopup, setShowPopup] = useState(false);
  const [popupPosition, setPopupPosition] = useState({ x: 0, y: 0 });
  
  // 互動狀態
  const [interactionType, setInteractionType] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  
  // 歷史記錄
  const [interactionHistory, setInteractionHistory] = useState([]);
  
  // 當前頁面模式
  const [currentMode, setCurrentMode] = useState('make proposal');
  
  // 提案相關數據（用於修改功能）
  const [proposalData, setProposalData] = useState({
    proposal: '',
    oldChunks: []
  });

  // 添加回調函數狀態
  const [onReviseCallback, setOnReviseCallback] = useState(null);

  // 處理文字選擇
  const handleTextSelection = useCallback((event) => {
    console.log('🔍 [TEXT-HIGHLIGHT] 文字選擇事件觸發');
    
    // 阻止事件冒泡，避免觸發全局點擊事件
    event.stopPropagation();
    
    const selection = window.getSelection();
    const selectedText = selection.toString().trim();
    
    console.log('🔍 [TEXT-HIGHLIGHT] 選中文字:', selectedText);
    console.log('🔍 [TEXT-HIGHLIGHT] 文字長度:', selectedText.length);
    
    if (selectedText && selectedText.length > 0) {
      // 檢查是否在 citation 卡片內
      const target = event.target;
      const isInCitation = target.closest('.ant-collapse-item-content') || 
                          target.closest('[data-citation]');
      
      console.log('🔍 [TEXT-HIGHLIGHT] 目標元素:', target);
      console.log('🔍 [TEXT-HIGHLIGHT] 是否在 citation 內:', isInCitation);
      
      if (isInCitation) {
        console.log('🔍 [TEXT-HIGHLIGHT] 在 citation 內，不觸發功能');
        return; // 在 citation 卡片內不觸發反白功能
      }
      
      // 🔍 [NEW] 識別反白區域
      const highlightedArea = identifyHighlightedArea(target);
      console.log('🔍 [TEXT-HIGHLIGHT] 識別的反白區域:', highlightedArea);
      
      // 獲取選中文字的位置
      const range = selection.getRangeAt(0);
      const rect = range.getBoundingClientRect();
      
      // 計算到選中文字最後一個字符的位置
      const endPosition = calculateEndPosition(range);
      
      // 提取上下文段落
      const contextText = extractContextParagraph(selectedText, event.target);
      
      console.log('🔍 [TEXT-HIGHLIGHT] 設置彈窗狀態');
      console.log('🔍 [TEXT-HIGHLIGHT] 原始彈窗位置:', { x: rect.right, y: rect.bottom });
      console.log('🔍 [TEXT-HIGHLIGHT] 修正後彈窗位置:', endPosition);
      
      setHighlightedText(selectedText);
      setContextParagraph(contextText);
      setPopupPosition(endPosition);
      setShowPopup(true);
      
      // 🔍 [NEW] 設置反白區域信息
      setHighlightedArea(highlightedArea);
      
      console.log('🔍 [TEXT-HIGHLIGHT] 彈窗狀態已設置');
    } else {
      setShowPopup(false);
    }
  }, []);

  // 🔍 [NEW] 識別反白區域的函數
  const identifyHighlightedArea = (targetElement) => {
    // 向上遍歷 DOM 樹，尋找特定的容器元素
    let currentElement = targetElement;
    
    while (currentElement && currentElement !== document.body) {
      // 檢查是否在 proposal card 內
      if (currentElement.closest('[data-area="proposal"]') || 
          currentElement.closest('.proposal-card') ||
          currentElement.closest('[data-testid="proposal-content"]')) {
        return 'proposal';
      }
      
      // 檢查是否在 experiment detail card 內
      if (currentElement.closest('[data-area="experiment"]') || 
          currentElement.closest('.experiment-detail-card') ||
          currentElement.closest('[data-testid="experiment-content"]')) {
        return 'experiment';
      }
      
      currentElement = currentElement.parentElement;
    }
    
    // 默認返回 proposal（向後兼容）
    return 'proposal';
  };

  // 計算選中文字最後一個字符的位置
  const calculateEndPosition = (range) => {
    try {
      // 創建一個新的範圍，只包含選中文字的最後一個字符
      const endRange = range.cloneRange();
      
      // 將範圍的開始位置移動到結束位置的前一個字符
      endRange.setStart(range.endContainer, Math.max(0, range.endOffset - 1));
      endRange.setEnd(range.endContainer, range.endOffset);
      
      // 獲取最後一個字符的位置
      const endRect = endRange.getBoundingClientRect();
      
      // 如果最後一個字符的位置有效，使用它；否則回退到原始範圍的右下角
      if (endRect.width > 0 && endRect.height > 0) {
        return {
          x: endRect.right,
          y: endRect.bottom
        };
      } else {
        // 回退方案：使用原始範圍的右下角
        const originalRect = range.getBoundingClientRect();
        return {
          x: originalRect.right,
          y: originalRect.bottom
        };
      }
    } catch (error) {
      console.error('計算結束位置失敗:', error);
      // 錯誤處理：回退到原始範圍的右下角
      const originalRect = range.getBoundingClientRect();
      return {
        x: originalRect.right,
        y: originalRect.bottom
      };
    }
  };

  // 提取上下文段落
  const extractContextParagraph = (selectedText, targetElement) => {
    try {
      // 尋找包含選中文字的段落元素
      let paragraphElement = targetElement;
      while (paragraphElement && !paragraphElement.textContent.includes(selectedText)) {
        paragraphElement = paragraphElement.parentElement;
      }
      
      if (paragraphElement) {
        return paragraphElement.textContent || selectedText;
      }
      
      return selectedText;
    } catch (error) {
      console.error('提取上下文段落失敗:', error);
      return selectedText;
    }
  };

  // 清除反白狀態
  const clearHighlight = useCallback(() => {
    setHighlightedText('');
    setContextParagraph('');
    setShowPopup(false);
    setInteractionType('');
    setIsProcessing(false);
  }, []);

  // 處理互動請求
  const handleTextInteraction = useCallback(async (type, userInput) => {
    console.log('🔍 [TEXT-HIGHLIGHT] 開始處理文字互動請求:', { type, userInput, highlightedText });
    
    if (!highlightedText.trim()) {
      message.warning('請先選擇文字');
      return;
    }

    setIsProcessing(true);
    
    try {
      // 構建請求數據
      const requestData = {
        highlighted_text: highlightedText,
        context_paragraph: contextParagraph,
        full_text: fullText,
        mode: currentMode,
        user_input: userInput,
        interaction_type: type,  // 添加這個字段
        highlighted_area: highlightedArea  // 🔍 [NEW] 添加反白區域信息
      };

      // 如果是修改功能，需要添加提案數據
      if (type === 'revise') {
        requestData.proposal = proposalData.proposal;
        requestData.old_chunks = proposalData.oldChunks;
      }

      const response = await fetch('/api/v1/text-interaction', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      if (!response.ok) {
        const errorText = await response.text();
        let errorMessage = '請求失敗';
        
        try {
          const errorData = JSON.parse(errorText);
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch (e) {
          errorMessage = errorText || errorMessage;
        }
        
        throw new Error(errorMessage);
      }

      const result = await response.json();
      
      console.log('🔍 [TEXT-HIGHLIGHT] API 響應接收完成');
      console.log('🔍 [TEXT-HIGHLIGHT] result 類型:', typeof result);
      console.log('🔍 [TEXT-HIGHLIGHT] result 鍵:', Object.keys(result));
      console.log('🔍 [TEXT-HIGHLIGHT] result.chemicals:', result.chemicals);
      console.log('🔍 [TEXT-HIGHLIGHT] result.chemicals 類型:', typeof result.chemicals);
      console.log('🔍 [TEXT-HIGHLIGHT] result.chemicals 長度:', result.chemicals?.length);
      
      // 添加到歷史記錄
      const historyItem = {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        type: type,
        highlightedText: highlightedText,
        userInput: userInput,
        llmResponse: result.answer,
        citations: result.citations,
        context: currentMode,
        requestId: result.request_id
      };
      
      setInteractionHistory(prev => [historyItem, ...prev]);
      
      // 如果是修改功能，自動應用修改並關閉彈窗
      if (type === 'revise' && (result.structured_proposal || result.structured_experiment)) {
        console.log('🔍 [TEXT-HIGHLIGHT] 修改功能完成，準備應用修改');
        console.log('🔍 [TEXT-HIGHLIGHT] 修改類型:', result.structured_proposal ? 'proposal' : 'experiment');
        console.log('🔍 [TEXT-HIGHLIGHT] 調用 onReviseCallback 前的 result.chemicals:', result.chemicals);
        
        // 調用回調函數，通知 Proposal.jsx 更新狀態
        if (onReviseCallback) {
          console.log('🔍 [TEXT-HIGHLIGHT] onReviseCallback 存在，開始調用');
          onReviseCallback(result);
          console.log('🔍 [TEXT-HIGHLIGHT] onReviseCallback 調用完成');
        } else {
          console.log('❌ [TEXT-HIGHLIGHT] onReviseCallback 不存在！');
        }
        
        // 更新內部狀態
        setProposalData(prev => ({
          ...prev,
          proposal: result.answer,
          oldChunks: result.chunks || []
        }));
        
        // 自動關閉彈窗
        clearHighlight();
        
        // 顯示成功消息
        const successMessage = result.structured_proposal ? '提案修改成功！' : '實驗細節修改成功！';
        message.success(successMessage);
      }
      
      return result;
      
    } catch (error) {
      console.error('文字互動請求失敗:', error);
      message.error(error.message || '處理失敗，請稍後再試');
      throw error;
    } finally {
      setIsProcessing(false);
      // 只有修改功能才關閉彈窗，解釋功能保持彈窗開啟
      if (type === 'revise') {
        // 修改功能已經在 if 區塊中處理了關閉彈窗
        // 這裡不需要額外處理
      } else {
        // 解釋功能保持彈窗開啟，不關閉
        // 移除自動關閉彈窗的邏輯
      }
    }
  }, [highlightedText, contextParagraph, fullText, currentMode, proposalData, onReviseCallback, clearHighlight]);

  // 設置當前模式
  const setMode = useCallback((mode) => {
    setCurrentMode(mode);
  }, []);

  // 設置提案數據
  const setProposal = useCallback((proposal, chunks = []) => {
    setProposalData({
      proposal: proposal,
      oldChunks: chunks
    });
  }, []);

  // 設置完整文本
  const setText = useCallback((text) => {
    setFullText(text);
  }, []);

  // 清除歷史記錄
  const clearHistory = useCallback(() => {
    setInteractionHistory([]);
  }, []);

  // ESC 鍵關閉彈窗
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === 'Escape' && showPopup) {
        clearHighlight();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [showPopup, clearHighlight]);

  // 設置修改回調函數
  const setReviseCallback = useCallback((callback) => {
    setOnReviseCallback(() => callback);
  }, []);

  // 提供給子組件的值
  const value = {
    // 狀態
    highlightedText,
    contextParagraph,
    showPopup,
    popupPosition,
    interactionType,
    isProcessing,
    interactionHistory,
    currentMode,
    proposalData,
    highlightedArea, // 🔍 [NEW] 添加反白區域
    
    // 方法
    handleTextSelection,
    handleTextInteraction,
    clearHighlight,
    setMode,
    setProposal,
    setText,
    clearHistory,
    setReviseCallback  // 新增：設置修改回調函數
  };

  return (
    <TextHighlightContext.Provider value={value}>
      {children}
    </TextHighlightContext.Provider>
  );
}; 