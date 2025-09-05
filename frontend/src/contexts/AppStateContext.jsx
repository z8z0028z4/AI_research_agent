/**
 * 全局應用狀態管理Context
 * 
 * 負責管理所有頁面的狀態，包括：
 * - Proposal頁面的提案、化學品、引用等數據
 * - Search頁面的搜尋結果
 * - KnowledgeQuery頁面的查詢結果
 * - 自動保存到localStorage實現持久化
 * - 提供統一的狀態管理接口
 */

import React, { createContext, useContext, useReducer, useEffect, useCallback } from 'react';
import { message } from 'antd';

// 初始狀態
const initialState = {
  // Proposal頁面狀態
  proposal: {
    formData: { goal: '', retrievalCount: 10 },
    proposal: '',
    chemicals: [],
    notFound: [],
    citations: [],
    chunks: [],
    experimentDetail: '',
    structuredExperiment: null,
    structuredProposal: null,
    retrievalCount: 10,
    hasGeneratedContent: false,
    showReviseInput: false,
    reviseFeedback: ''
  },
  
  // Search頁面狀態
  search: {
    searchQuery: '',
    searchType: 'papers',
    results: [],
    hasSearched: false
  },
  
  // KnowledgeQuery頁面狀態
  knowledgeQuery: {
    formData: { question: '' },
    answer: '',
    citations: [],
    chunks: [],
    retrievalCount: 10,
    answerMode: 'rigorous',
    hasQueried: false
  },
  
  // 全局設置
  settings: {
    lastActiveTab: '/',
    autoSave: true,
    lastSaved: null
  }
};

  // Action類型
  const ACTIONS = {
    // Proposal actions
    SET_PROPOSAL_FORM_DATA: 'SET_PROPOSAL_FORM_DATA',
    SET_PROPOSAL_RESULT: 'SET_PROPOSAL_RESULT',
    SET_PROPOSAL_EXPERIMENT: 'SET_PROPOSAL_EXPERIMENT',
    CLEAR_PROPOSAL: 'CLEAR_PROPOSAL',
    
    // Search actions
    SET_SEARCH_QUERY: 'SET_SEARCH_QUERY',
    SET_SEARCH_TYPE: 'SET_SEARCH_TYPE',
    SET_SEARCH_RESULTS: 'SET_SEARCH_RESULTS',
    CLEAR_SEARCH: 'CLEAR_SEARCH',
    
    // KnowledgeQuery actions
    SET_KNOWLEDGE_FORM_DATA: 'SET_KNOWLEDGE_FORM_DATA',
    SET_KNOWLEDGE_RESULT: 'SET_KNOWLEDGE_RESULT',
    CLEAR_KNOWLEDGE: 'CLEAR_KNOWLEDGE',
    
    // Global actions
    SET_ACTIVE_TAB: 'SET_ACTIVE_TAB',
    CLEAR_ALL_DATA: 'CLEAR_ALL_DATA',
    IMPORT_DATA: 'IMPORT_DATA',
    EXPORT_DATA: 'EXPORT_DATA'
  };

// Reducer函數
const appStateReducer = (state, action) => {
  switch (action.type) {
    case ACTIONS.SET_PROPOSAL_FORM_DATA:
      return {
        ...state,
        proposal: {
          ...state.proposal,
          formData: { ...state.proposal.formData, ...action.payload }
        }
      };
      
    case ACTIONS.SET_PROPOSAL_RESULT:
      return {
        ...state,
        proposal: {
          ...state.proposal,
          ...action.payload,
          hasGeneratedContent: true
        }
      };
      
    case ACTIONS.SET_PROPOSAL_EXPERIMENT:
      return {
        ...state,
        proposal: {
          ...state.proposal,
          experimentDetail: action.payload.experimentDetail,
          structuredExperiment: action.payload.structuredExperiment,
          citations: action.payload.citations || state.proposal.citations
        }
      };
      
    case ACTIONS.CLEAR_PROPOSAL:
      return {
        ...state,
        proposal: {
          ...initialState.proposal,
          formData: state.proposal.formData // 保留表單數據
        }
      };
      
    case ACTIONS.SET_SEARCH_QUERY:
      return {
        ...state,
        search: {
          ...state.search,
          searchQuery: action.payload
        }
      };
      
    case ACTIONS.SET_SEARCH_TYPE:
      return {
        ...state,
        search: {
          ...state.search,
          searchType: action.payload
        }
      };
      
    case ACTIONS.SET_SEARCH_RESULTS:
      return {
        ...state,
        search: {
          ...state.search,
          results: action.payload,
          hasSearched: true
        }
      };
      
    case ACTIONS.CLEAR_SEARCH:
      return {
        ...state,
        search: {
          ...initialState.search,
          searchQuery: state.search.searchQuery // 保留搜尋查詢
        }
      };
      
    case ACTIONS.SET_KNOWLEDGE_FORM_DATA:
      return {
        ...state,
        knowledgeQuery: {
          ...state.knowledgeQuery,
          ...action.payload  // 直接更新根級別屬性
        }
      };
      
    case ACTIONS.SET_KNOWLEDGE_RESULT:
      return {
        ...state,
        knowledgeQuery: {
          ...state.knowledgeQuery,
          ...action.payload,
          hasQueried: true
        }
      };
      
    case ACTIONS.CLEAR_KNOWLEDGE:
      return {
        ...state,
        knowledgeQuery: {
          ...initialState.knowledgeQuery,
          formData: state.knowledgeQuery.formData // 保留表單數據
        }
      };
      
    case ACTIONS.SET_ACTIVE_TAB:
      return {
        ...state,
        settings: {
          ...state.settings,
          lastActiveTab: action.payload
        }
      };
      
    case ACTIONS.CLEAR_ALL_DATA:
      return {
        ...initialState,
        settings: {
          ...initialState.settings,
          lastActiveTab: state.settings.lastActiveTab
        }
      };
      
    case ACTIONS.IMPORT_DATA:
      return {
        ...action.payload,
        settings: {
          ...action.payload.settings,
          lastActiveTab: state.settings.lastActiveTab
        }
      };
      
    default:
      return state;
  }
};

// 創建Context
const AppStateContext = createContext();

// 自定義Hook
export const useAppState = () => {
  const context = useContext(AppStateContext);
  if (!context) {
    throw new Error('useAppState must be used within an AppStateProvider');
  }
  return context;
};

// Provider組件
export const AppStateProvider = ({ children }) => {
  const [state, dispatch] = useReducer(appStateReducer, initialState);
  
  // 從localStorage加載數據
  useEffect(() => {
    try {
      const savedState = localStorage.getItem('ai_research_app_state');
      if (savedState) {
        const parsedState = JSON.parse(savedState);
        dispatch({ type: ACTIONS.IMPORT_DATA, payload: parsedState });
        console.log('📦 [APP-STATE] 從localStorage恢復狀態');
      }
    } catch (error) {
      console.error('❌ [APP-STATE] 恢復狀態失敗:', error);
    }
  }, []);
  
  // 自動保存到localStorage
  useEffect(() => {
    if (state.settings.autoSave) {
      try {
        const stateToSave = {
          ...state,
          settings: {
            ...state.settings,
            lastSaved: new Date().toISOString()
          }
        };
        localStorage.setItem('ai_research_app_state', JSON.stringify(stateToSave));
        console.log('💾 [APP-STATE] 自動保存狀態到localStorage');
      } catch (error) {
        console.error('❌ [APP-STATE] 保存狀態失敗:', error);
      }
    }
  }, [state]);
  
  // Proposal相關actions
  const setProposalFormData = useCallback((formData) => {
    dispatch({ type: ACTIONS.SET_PROPOSAL_FORM_DATA, payload: formData });
  }, []);
  
  const setProposalResult = useCallback((result) => {
    dispatch({ type: ACTIONS.SET_PROPOSAL_RESULT, payload: result });
  }, []);
  
  const setProposalExperiment = useCallback((experimentData) => {
    dispatch({ type: ACTIONS.SET_PROPOSAL_EXPERIMENT, payload: experimentData });
  }, []);
  
  const clearProposal = useCallback(() => {
    dispatch({ type: ACTIONS.CLEAR_PROPOSAL });
    message.success('提案數據已清除');
  }, []);
  
  // Search相關actions
  const setSearchQuery = useCallback((query, field = 'searchQuery') => {
    if (field === 'searchQuery') {
      dispatch({ type: ACTIONS.SET_SEARCH_QUERY, payload: query });
    } else if (field === 'searchType') {
      dispatch({ type: ACTIONS.SET_SEARCH_TYPE, payload: query });
    }
  }, []);
  
  const setSearchResults = useCallback((results) => {
    dispatch({ type: ACTIONS.SET_SEARCH_RESULTS, payload: results });
  }, []);
  
  const clearSearch = useCallback(() => {
    dispatch({ type: ACTIONS.CLEAR_SEARCH });
    message.success('搜尋結果已清除');
  }, []);
  
  // KnowledgeQuery相關actions
  const setKnowledgeFormData = useCallback((formData) => {
    dispatch({ type: ACTIONS.SET_KNOWLEDGE_FORM_DATA, payload: formData });
  }, []);
  
  const setKnowledgeResult = useCallback((result) => {
    dispatch({ type: ACTIONS.SET_KNOWLEDGE_RESULT, payload: result });
  }, []);
  
  const clearKnowledge = useCallback(() => {
    dispatch({ type: ACTIONS.CLEAR_KNOWLEDGE });
    message.success('知識查詢結果已清除');
  }, []);
  
  // 全局actions
  const setActiveTab = useCallback((tab) => {
    dispatch({ type: ACTIONS.SET_ACTIVE_TAB, payload: tab });
  }, []);
  
  const clearAllData = useCallback(() => {
    dispatch({ type: ACTIONS.CLEAR_ALL_DATA });
    localStorage.removeItem('ai_research_app_state');
    message.success('所有數據已清除');
  }, []);
  
  const exportData = useCallback(() => {
    try {
      const dataToExport = {
        ...state,
        exportDate: new Date().toISOString(),
        version: '1.0.0'
      };
      const blob = new Blob([JSON.stringify(dataToExport, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `ai_research_data_${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      message.success('數據導出成功');
    } catch (error) {
      console.error('❌ [APP-STATE] 導出數據失敗:', error);
      message.error('數據導出失敗');
    }
  }, [state]);
  
  const importData = useCallback((data) => {
    try {
      dispatch({ type: ACTIONS.IMPORT_DATA, payload: data });
      message.success('數據導入成功');
    } catch (error) {
      console.error('❌ [APP-STATE] 導入數據失敗:', error);
      message.error('數據導入失敗');
    }
  }, []);
  
  const value = {
    // 狀態
    state,
    
    // Proposal actions
    setProposalFormData,
    setProposalResult,
    setProposalExperiment,
    clearProposal,
    
    // Search actions
    setSearchQuery,
    setSearchResults,
    clearSearch,
    
    // KnowledgeQuery actions
    setKnowledgeFormData,
    setKnowledgeResult,
    clearKnowledge,
    
    // Global actions
    setActiveTab,
    clearAllData,
    exportData,
    importData
  };
  
  return (
    <AppStateContext.Provider value={value}>
      {children}
    </AppStateContext.Provider>
  );
}; 