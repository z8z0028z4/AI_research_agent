import { Button, Card, Collapse, Divider, Form, Input, List, message, Select, Space, Typography } from 'antd';
import React, { useMemo, useRef, useState, useEffect } from 'react';
import SmilesDrawer from '../components/SmilesDrawer';
import { useTextHighlight } from '../components/TextHighlight/TextHighlightProvider';
import { useAppState } from '../contexts/AppStateContext';

const { Title, Paragraph, Text } = Typography;
const { TextArea } = Input;
const { Option } = Select;

const API_BASE = '/api/v1';

const Proposal = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [isTextareaFocused, setIsTextareaFocused] = useState(false); // 追蹤輸入框是否被聚焦
  const [isReviseInputFocused, setIsReviseInputFocused] = useState(false); // 追蹤修訂輸入框是否被聚焦
  const reviseInputRef = useRef(null); // 修訂輸入框的 ref

  // 使用全局狀態管理
  const { 
    state, 
    setProposalFormData, 
    setProposalResult, 
    setProposalExperiment 
  } = useAppState();
  
  const {
    formData,
    proposal,
    chemicals,
    notFound,
    citations,
    chunks,
    experimentDetail,
    structuredExperiment,
    structuredProposal,
    retrievalCount,
    hasGeneratedContent,
    showReviseInput,
    reviseFeedback
  } = state.proposal;

  // 文字反白功能
  const { setMode, setProposal: setTextHighlightProposal, setText, handleTextSelection, setReviseCallback } = useTextHighlight();

  const hasResult = useMemo(
    () => Boolean(proposal) || chemicals.length > 0 || citations.length > 0,
    [proposal, chemicals, citations]
  );

  // 設置文字反白模式
  useEffect(() => {
    setMode('make proposal');
  }, [setMode]);

  // 同步表單數據
  useEffect(() => {
    if (formData.goal !== form.getFieldValue('goal')) {
      form.setFieldsValue(formData);
    }
  }, [formData, form]);

  // 設置文字反白功能的修改回調
  useEffect(() => {
    setReviseCallback((result) => {
      console.log('🔍 [PROPOSAL] 文字反白修改回調被調用');
      console.log('🔍 [PROPOSAL] result:', result);
      console.log('🔍 [PROPOSAL] result.answer:', result.answer);
      console.log('🔍 [PROPOSAL] result.structured_proposal:', result.structured_proposal);
      console.log('🔍 [PROPOSAL] result.structured_experiment:', result.structured_experiment);
      
      // 根據互動類型處理不同的修改
      if (result.interaction_type === 'revise') {
        if (result.structured_proposal) {
          // 修改提案
          setProposalResult({
            proposal: result.answer || '',
            structuredProposal: result.structured_proposal,
            chemicals: result.chemicals || [],
            notFound: result.not_found || [],
            citations: result.citations || [],
            chunks: result.chunks || [],
            experimentDetail: '', // 清空實驗細節
            structuredExperiment: null // 清空結構化實驗細節
          });
        } else if (result.structured_experiment) {
          // 修改實驗細節
          setProposalExperiment({
            experimentDetail: result.answer || '',
            structuredExperiment: result.structured_experiment,
            citations: result.citations || []
          });
        }
        
        // 更新文字反白功能的數據
        setTextHighlightProposal(result.answer || '', result.chunks || []);
        setText(result.answer || '');
        
        console.log('✅ [PROPOSAL] 文字反白修改已應用');
        console.log('✅ [PROPOSAL] 修改類型:', result.structured_proposal ? 'proposal' : 'experiment');
      }
    });
  }, [setReviseCallback, setTextHighlightProposal, setText, setProposalResult, setProposalExperiment]);

  // 監控 chemicals 狀態變化
  useEffect(() => {
    console.log('🔍 [PROPOSAL] chemicals 狀態變化:', chemicals);
    console.log('🔍 [PROPOSAL] chemicals 長度:', chemicals.length);
    if (chemicals.length > 0) {
      console.log('🔍 [PROPOSAL] 第一個化學品:', chemicals[0]);
      console.log('🔍 [PROPOSAL] 第一個化學品的鍵:', Object.keys(chemicals[0]));
    }
  }, [chemicals]);

  const callApi = async (path, options = {}) => {
    const res = await fetch(`${API_BASE}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      ...options,
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  };

  const showError = (e, fallbackMsg) => {
    try {
      const msg = e?.message || '';
      const data = JSON.parse(msg);
      const detail = data?.detail || msg;
      message.error(detail || fallbackMsg);
    } catch (_) {
      message.error(fallbackMsg);
    }
  };

  const onGenerate = async () => {
    const goal = form.getFieldValue('goal');
    if (!goal) return message.warning('請輸入研究目標');

    // 保存表單數據到全局狀態
    setProposalFormData({ goal });

    // 生成唯一的請求 ID
    const requestId = Math.random().toString(36).substr(2, 8);
    const startTime = Date.now();

    console.log(`🚀 [FRONTEND-${requestId}] ========== 開始生成提案 ==========`);
    console.log(`🚀 [FRONTEND-${requestId}] 時間戳: ${new Date().toLocaleString()}`);
    console.log(`🚀 [FRONTEND-${requestId}] 研究目標: ${goal}`);
    console.log(`🚀 [FRONTEND-${requestId}] 檢索數量: ${retrievalCount}`);
    console.log(`🚀 [FRONTEND-${requestId}] loading 狀態: ${loading}`);

    setLoading(true);
    try {
      console.log(`🔍 [FRONTEND-${requestId}] 發送 API 請求...`);
      const data = await callApi('/proposal/generate', {
        body: JSON.stringify({
          research_goal: goal,
          retrieval_count: retrievalCount
        }),
      });

      const endTime = Date.now();
      const duration = endTime - startTime;

      console.log(`✅ [FRONTEND-${requestId}] ========== API 響應成功 ==========`);
      console.log(`✅ [FRONTEND-${requestId}] 總耗時: ${duration}ms`);
      console.log(`✅ [FRONTEND-${requestId}] 提案長度: ${data.proposal?.length || 0}`);
      console.log(`✅ [FRONTEND-${requestId}] 化學品數量: ${data.chemicals?.length || 0}`);
      console.log(`✅ [FRONTEND-${requestId}] 引用數量: ${data.citations?.length || 0}`);
      console.log(`✅ [FRONTEND-${requestId}] 文檔塊數量: ${data.chunks?.length || 0}`);

      // 使用全局狀態管理更新結果
      setProposalResult({
        proposal: data.proposal || '',
        chemicals: data.chemicals || [],
        notFound: data.not_found || [],
        citations: data.citations || [],
        chunks: data.chunks || [],
        experimentDetail: '',
        structuredProposal: data.structured_proposal || null,
        structuredExperiment: null,
        retrievalCount: retrievalCount
      });

      // 設置文字反白功能的數據
      setTextHighlightProposal(data.proposal || '', data.chunks || []);
      setText(data.proposal || '');

      console.log(`✅ [FRONTEND-${requestId}] 狀態更新完成`);

    } catch (e) {
      const endTime = Date.now();
      const duration = endTime - startTime;

      console.error(`❌ [FRONTEND-${requestId}] ========== 生成失敗 ==========`);
      console.error(`❌ [FRONTEND-${requestId}] 總耗時: ${duration}ms`);
      console.error(`❌ [FRONTEND-${requestId}] 錯誤:`, e);

      showError(e, '生成提案失敗');
    } finally {
      setLoading(false);
      console.log(`🔚 [FRONTEND-${requestId}] loading 狀態設為 false`);
    }
  };

  const onRevise = async () => {
    console.log('🔍 FRONTEND DEBUG: onRevise called');
    console.log('🔍 FRONTEND DEBUG: reviseFeedback:', reviseFeedback);
    console.log('🔍 FRONTEND DEBUG: proposal exists:', !!proposal);

    if (!reviseFeedback) return message.warning('請輸入修訂意見');
    if (!proposal) return message.warning('請先生成提案');

    setLoading(true);
    try {
      console.log('🔍 FRONTEND DEBUG: Sending revise request to backend');
      const data = await callApi('/proposal/revise', {
        body: JSON.stringify({
          original_proposal: proposal,
          user_feedback: reviseFeedback,
          chunks,
        }),
      });
      console.log('🔍 FRONTEND DEBUG: Revise response received:', data);

      // 使用全局狀態管理更新結果
      setProposalResult({
        proposal: data.proposal || '',
        chemicals: data.chemicals || [],
        notFound: data.not_found || [],
        citations: data.citations || [],
        chunks: data.chunks || [],
        experimentDetail: '',
        structuredProposal: data.structured_proposal || null,
        structuredExperiment: null,
        showReviseInput: false, // 隱藏修訂輸入框
        reviseFeedback: '' // 清空修訂意見
      });

      // 更新文字反白功能的數據
      setTextHighlightProposal(data.proposal || '', data.chunks || []);
      setText(data.proposal || '');

      message.success('提案修訂成功！');
    } catch (e) {
      console.error('❌ FRONTEND DEBUG: Revise failed:', e);
      showError(e, '修訂失敗');
    } finally {
      setLoading(false);
    }
  };

  const onShowReviseInput = () => {
    if (showReviseInput) {
      // 如果已經顯示，則直接隱藏
      setProposalFormData({ showReviseInput: false, reviseFeedback: '' });
      setIsReviseInputFocused(false);
    } else {
      // 如果未顯示，則顯示並聚焦
      setProposalFormData({ showReviseInput: true });
      // 使用 setTimeout 確保 DOM 更新後再聚焦
      setTimeout(() => {
        reviseInputRef.current?.focus();
      }, 0);
    }
  };

  const onGenerateExperimentDetail = async () => {
    if (!proposal) return message.warning('請先生成或修訂提案');
    setLoading(true);
    try {
      const data = await callApi('/proposal/experiment-detail', {
        body: JSON.stringify({ proposal, chunks }),
      });

      // 使用全局狀態管理更新實驗細節
      setProposalExperiment({
        experimentDetail: data.experiment_detail || '',
        structuredExperiment: data.structured_experiment || null,
        citations: data.citations || citations // 如果有新的citations則更新，否則保留原有的
      });

      // 顯示重試信息
      if (data.retry_info) {
        console.log('🔄 重試信息:', data.retry_info);
        if (data.retry_info.retry_count > 0) {
          message.info(`重試 ${data.retry_info.retry_count} 次，最終使用 ${data.retry_info.final_tokens} tokens`);
        }
      }
    } catch (e) {
      showError(e, '生成實驗細節失敗');
      // eslint-disable-next-line no-console
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const onDownloadDocx = async () => {
    if (!proposal) return message.warning('請先生成提案');
    setLoading(true);
    try {
      console.log('🔍 FRONTEND DEBUG: 開始下載 DOCX');
      console.log('🔍 FRONTEND DEBUG: proposal 長度:', proposal.length);
      console.log('🔍 FRONTEND DEBUG: chemicals 數量:', chemicals.length);
      console.log('🔍 FRONTEND DEBUG: experiment_detail 長度:', experimentDetail.length);
      console.log('🔍 FRONTEND DEBUG: citations 數量:', citations.length);

      // 清理 markdown 格式的函數
      const cleanMarkdownText = (text) => {
        if (!text) return "";
        return text
          .replace(/\*\*(.*?)\*\*/g, '$1') // 移除粗體標記
          .replace(/\*(.*?)\*/g, '$1') // 移除斜體標記
          .replace(/`(.*?)`/g, '$1') // 移除代碼標記
          .replace(/^#+\s*(.*)$/gm, '$1') // 移除標題標記
          .replace(/^\s*[-*+]\s+/gm, '- ') // 統一項目符號
          .replace(/^\s*\d+\.\s+/gm, (match) => match.replace(/^\s*\d+\.\s+/, '')) // 移除編號
          .replace(/\n\s*\n\s*\n/g, '\n\n') // 移除多餘空行
          .replace(/\n\s*\*\*/g, '\n') // 移除粗體前的換行
          .replace(/\*\*\s*\n/g, '\n'); // 移除粗體後的換行
      };

      const response = await fetch(`${API_BASE}/proposal/generate-docx`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          proposal: cleanMarkdownText(proposal),
          chemicals,
          not_found: notFound,
          experiment_detail: cleanMarkdownText(experimentDetail),
          citations,
        }),
      });

      console.log('🔍 FRONTEND DEBUG: 響應狀態:', response.status);
      console.log('🔍 FRONTEND DEBUG: 響應頭:', Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ FRONTEND DEBUG: 響應錯誤:', errorText);
        throw new Error(`下載失敗: ${response.status} - ${errorText}`);
      }

      // 創建下載鏈接
      const blob = await response.blob();
      console.log('🔍 FRONTEND DEBUG: blob 大小:', blob.size);

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'proposal_report.docx';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      message.success('文件下載成功！');
    } catch (e) {
      console.error('❌ FRONTEND DEBUG: 下載失敗:', e);
      showError(e, '下載失敗');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Title level={2}>Research Proposal</Title>
      <Paragraph>Generate your comprehensive research proposals with minimal input.</Paragraph>

      <Card title="New Proposal" style={{ marginBottom: 24, position: 'relative' }}>
        <Form form={form} layout="vertical" initialValues={formData}>
          <Form.Item name="goal" label="Research Goal" rules={[{ required: true, message: 'Please enter your research goal' }]}>
            <TextArea
              rows={hasGeneratedContent && !isTextareaFocused ? 1 : 12}
              placeholder="Please enter your research goal"
              onFocus={() => setIsTextareaFocused(true)}
              onBlur={() => setIsTextareaFocused(false)}
              onChange={(e) => setProposalFormData({ goal: e.target.value })}
            />
          </Form.Item>

          <Form.Item label="Document Retrieval Count">
            <Select
              value={retrievalCount}
              onChange={(value) => setProposalFormData({ retrievalCount: value })}
              style={{ width: 200 }}
            >
              <Option value={1}>1 document (Dev Test)</Option>
              <Option value={5}>5 documents (Fast)</Option>
              <Option value={10}>10 documents (Balanced)</Option>
              <Option value={15}>15 documents (Comprehensive)</Option>
              <Option value={20}>20 documents (Thorough)</Option>
            </Select>
          </Form.Item>



          <Space wrap>
            <Button type="primary" size="large" onClick={onGenerate} loading={loading}>
              ✍️ Generate proposal
            </Button>
          </Space>
        </Form>

        {/* 下載按鈕 - 只在有提案時顯示 */}
        {proposal && (
          <div style={{
            position: 'absolute',
            bottom: '16px',
            right: '16px'
          }}>
            <Button
              type="primary"
              size="large"
              onClick={onDownloadDocx}
              loading={loading}
              icon="📥"
            >
              Download DOCX
            </Button>
          </div>
        )}
      </Card>

      {hasResult && (
        <>
          {/* 修訂說明卡片 - 僅在修訂提案時顯示 */}
          {structuredProposal?.revision_explanation && (
            <Collapse
              defaultActiveKey={['revision']}
              style={{ marginBottom: 16 }}
              items={[
                {
                  key: 'revision',
                  label: <span style={{ fontWeight: 700, fontSize: 27 }}>📝 Revision Explanation</span>,
                  children: (
                    <div style={{
                      whiteSpace: 'pre-wrap',
                      fontSize: '16px',
                      lineHeight: '1.6',
                      wordBreak: 'break-word',
                      overflowWrap: 'break-word',
                      maxWidth: '100%',
                      width: '100%',
                      fontWeight: 'normal'
                    }}>
                      {structuredProposal.revision_explanation}
                    </div>
                  ),
                },
              ]}
            />
          )}

          {/* 提案卡片 - 第一次提案和修訂提案都顯示 */}
          <Collapse
            defaultActiveKey={['proposal']}
            style={{ marginBottom: 16 }}
            items={[
              {
                key: 'proposal',
                label: <span style={{ fontWeight: 700, fontSize: 27 }}>🤖 Generated proposal</span>,
                children: (
                  <div 
                    data-area="proposal"
                    data-testid="proposal-content"
                    onMouseUp={handleTextSelection}
                    style={{
                      whiteSpace: 'pre-wrap',
                      fontSize: '16px',
                      lineHeight: '1.6',
                      wordBreak: 'break-word',
                      overflowWrap: 'break-word',
                      maxWidth: '100%',
                      width: '100%',
                      fontWeight: 'normal',
                      cursor: 'text'
                    }}
                  >
                    {structuredProposal ? (
                      // 渲染結構化提案數據
                      <>
                        {/* 提案標題 */}
                        {structuredProposal.proposal_title && (
                          <>
                            <div style={{
                              fontSize: '24px',
                              fontWeight: 'bold',
                              color: '#1890ff',
                              marginTop: '16px',
                              marginBottom: '8px'
                            }}>
                              Proposal
                            </div>
                            <div style={{ marginBottom: '16px' }}>
                              {structuredProposal.proposal_title}
                            </div>
                          </>
                        )}

                        {/* 研究需求 */}
                        {structuredProposal.need && (
                          <>
                            <div style={{
                              fontSize: '24px',
                              fontWeight: 'bold',
                              color: '#1890ff',
                              marginTop: '12px',
                              marginBottom: '6px'
                            }}>
                              Need
                            </div>
                            <div style={{ marginBottom: '16px' }}>
                              {structuredProposal.need}
                            </div>
                          </>
                        )}

                        {/* 解決方案 */}
                        {structuredProposal.solution && (
                          <>
                            <div style={{
                              fontSize: '24px',
                              fontWeight: 'bold',
                              color: '#1890ff',
                              marginTop: '12px',
                              marginBottom: '6px'
                            }}>
                              Solution
                            </div>
                            <div style={{ marginBottom: '16px' }}>
                              {structuredProposal.solution}
                            </div>
                          </>
                        )}

                        {/* 差異化 */}
                        {structuredProposal.differentiation && (
                          <>
                            <div style={{
                              fontSize: '24px',
                              fontWeight: 'bold',
                              color: '#1890ff',
                              marginTop: '12px',
                              marginBottom: '6px'
                            }}>
                              Differentiation
                            </div>
                            <div style={{ marginBottom: '16px' }}>
                              {structuredProposal.differentiation}
                            </div>
                          </>
                        )}

                        {/* 效益 */}
                        {structuredProposal.benefit && (
                          <>
                            <div style={{
                              fontSize: '24px',
                              fontWeight: 'bold',
                              color: '#1890ff',
                              marginTop: '12px',
                              marginBottom: '6px'
                            }}>
                              Benefit
                            </div>
                            <div style={{ marginBottom: '16px' }}>
                              {structuredProposal.benefit}
                            </div>
                          </>
                        )}

                        {/* 實驗概述 */}
                        {structuredProposal.experimental_overview && (
                          <>
                            <div style={{
                              fontSize: '24px',
                              fontWeight: 'bold',
                              color: '#1890ff',
                              marginTop: '12px',
                              marginBottom: '6px'
                            }}>
                              Experimental Overview
                            </div>
                            <div style={{ marginBottom: '16px' }}>
                              {structuredProposal.experimental_overview}
                            </div>
                          </>
                        )}
                      </>
                    ) : (
                      // 渲染傳統文本格式（作為 fallback）
                      proposal
                        .replace(/\*\*(.*?)\*\*/g, '$1') // 移除粗體標記
                        .replace(/\*(.*?)\*/g, '$1') // 移除斜體標記
                        .replace(/`(.*?)`/g, '$1') // 移除代碼標記
                        .replace(/^#+\s*(.*)$/gm, '$1') // 移除標題標記
                        .replace(/^\s*[-*+]\s+/gm, '- ') // 統一項目符號
                        .replace(/^\s*\d+\.\s+/gm, (match) => match.replace(/^\s*\d+\.\s+/, '')) // 移除編號
                        .replace(/\n\s*\n\s*\n/g, '\n\n') // 移除多餘空行
                        .replace(/\n\s*\*\*/g, '\n') // 移除粗體前的換行
                        .replace(/\*\*\s*\n/g, '\n') // 移除粗體後的換行
                        .split('\n')
                        .map((line, index) => {
                          if (line.match(/^(Revision Explanation:|Proposal:|Need:|Solution:|Differentiation:|Benefit:|Experimental overview:)/)) {
                            return (
                              <div key={index} style={{
                                fontSize: '24px',
                                fontWeight: 'bold',
                                color: '#1890ff',
                                marginTop: '16px',
                                marginBottom: '8px'
                              }}>
                                {line}
                              </div>
                            );
                          }
                          return <div key={index}>{line}</div>;
                        })
                    )}
                  </div>
                ),
              },
            ]}
          />

          {(experimentDetail || structuredExperiment) && (
            <>
              {/* 修訂說明卡片 - 僅在修訂實驗細節時顯示 */}
              {structuredExperiment?.revision_explanation && (
                <Collapse
                  defaultActiveKey={['revision']}
                  style={{ marginBottom: 16 }}
                  items={[
                    {
                      key: 'revision',
                      label: <span style={{ fontWeight: 700, fontSize: 27 }}>📝 Revision Explanation</span>,
                      children: (
                        <div style={{
                          whiteSpace: 'pre-wrap',
                          fontSize: '16px',
                          lineHeight: '1.6',
                          wordBreak: 'break-word',
                          overflowWrap: 'break-word',
                          maxWidth: '100%',
                          width: '100%',
                          fontWeight: 'normal'
                        }}>
                          {structuredExperiment.revision_explanation}
                        </div>
                      ),
                    },
                  ]}
                />
              )}

              {/* 實驗細節卡片 */}
              <Collapse
                defaultActiveKey={['experiment']}
                style={{ marginBottom: 16 }}
                items={[
                  {
                    key: 'experiment',
                    label: <span style={{ fontWeight: 700, fontSize: 27 }}>🔬 Suggested experiment details</span>,
                    children: (
                      <div 
                        data-area="experiment"
                        data-testid="experiment-content"
                        onMouseUp={handleTextSelection}
                        style={{
                          whiteSpace: 'pre-wrap',
                          fontSize: '16px',
                          lineHeight: '1.6',
                          wordBreak: 'break-word',
                          overflowWrap: 'break-word',
                          maxWidth: '100%',
                          width: '100%',
                          fontWeight: 'normal',
                          cursor: 'text'
                        }}
                      >
                        {structuredExperiment ? (
                          // 渲染結構化實驗細節數據
                          <>
                            {/* 合成過程 */}
                            {structuredExperiment.synthesis_process && (
                              <>
                                <div style={{
                                  fontSize: '24px',
                                  fontWeight: 'bold',
                                  color: '#1890ff',
                                  marginTop: '12px',
                                  marginBottom: '6px'
                                }}>
                                  Synthesis Process
                                </div>
                                <div style={{ marginBottom: '16px' }}>
                                  {structuredExperiment.synthesis_process
                                    .replace(/^(SYNTHESIS PROCESS|Synthesis Process|合成過程)[:\s]*/i, '')
                                    .trim()}
                                </div>
                              </>
                            )}

                            {/* 材料和條件 */}
                            {structuredExperiment.materials_and_conditions && (
                              <>
                                <div style={{
                                  fontSize: '24px',
                                  fontWeight: 'bold',
                                  color: '#1890ff',
                                  marginTop: '12px',
                                  marginBottom: '6px'
                                }}>
                                  Materials and Conditions
                                </div>
                                <div style={{ marginBottom: '16px' }}>
                                  {structuredExperiment.materials_and_conditions
                                    .replace(/^(MATERIALS AND CONDITIONS|Materials and Conditions|材料和條件)[:\s]*/i, '')
                                    .trim()}
                                </div>
                              </>
                            )}

                            {/* 分析方法 */}
                            {structuredExperiment.analytical_methods && (
                              <>
                                <div style={{
                                  fontSize: '24px',
                                  fontWeight: 'bold',
                                  color: '#1890ff',
                                  marginTop: '12px',
                                  marginBottom: '6px'
                                }}>
                                  Analytical Methods
                                </div>
                                <div style={{ marginBottom: '16px' }}>
                                  {structuredExperiment.analytical_methods
                                    .replace(/^(ANALYTICAL METHODS|Analytical Methods|分析方法)[:\s]*/i, '')
                                    .trim()}
                                </div>
                              </>
                            )}

                            {/* 注意事項 */}
                            {structuredExperiment.precautions && (
                              <>
                                <div style={{
                                  fontSize: '24px',
                                  fontWeight: 'bold',
                                  color: '#1890ff',
                                  marginTop: '12px',
                                  marginBottom: '6px'
                                }}>
                                  Precautions
                                </div>
                                <div style={{ marginBottom: '16px' }}>
                                  {structuredExperiment.precautions
                                    .replace(/^(PRECAUTIONS|Precautions|注意事項)[:\s]*/i, '')
                                    .trim()}
                                </div>
                              </>
                            )}
                          </>
                        ) : (
                          // 渲染傳統文本格式（作為 fallback）
                          experimentDetail
                            .replace(/\*\*(.*?)\*\*/g, '$1') // 移除粗體標記
                            .replace(/\*(.*?)\*/g, '$1') // 移除斜體標記
                            .replace(/`(.*?)`/g, '$1') // 移除代碼標記
                            .replace(/^#{3,}\s*(.*)$/gm, '$1') // 只移除 ### 及以上的標題標記，保留 ##
                            .replace(/^\s*[-*+]\s+/gm, '- ') // 統一項目符號
                            .replace(/^\s*\d+\.\s+/gm, (match) => match.replace(/^\s*\d+\.\s+/, '')) // 移除編號
                            .replace(/\n\s*\n\s*\n/g, '\n\n') // 移除多餘空行
                            .replace(/\n\s*\*\*/g, '\n') // 移除粗體前的換行
                            .replace(/\*\*\s*\n/g, '\n') // 移除粗體後的換行
                            .split('\n')
                            .map((line, index) => {
                              // 檢查是否為實驗細節的主要標題行（與提案區域相同的樣式）
                              if (line.match(/^(##\s*)?(合成過程|材料和條件|分析方法|注意事項|Synthesis Process|Materials and Conditions|Analytical Methods|Precautions|實驗細節|Experimental Details)/)) {
                                return (
                                  <div key={index} style={{
                                    fontSize: '24px',
                                    fontWeight: 'bold',
                                    color: '#1890ff',
                                    marginTop: '16px',
                                    marginBottom: '8px'
                                  }}>
                                    {line.replace(/^##\s*/, '')}
                                  </div>
                                );
                              }
                              // 檢查是否為子標題行（保持原有的樣式）
                              if (line.match(/^(\d+\)\s*)?(前處理與配方計算|微波輔助骨架合成|活化|微波促進的後合成接枝|Pre-treatment and Formulation Calculation|Microwave-assisted Framework Synthesis|Activation|Microwave-promoted Post-synthesis Grafting|材料\(IUPAC 名稱以便辨識\)|Materials \(IUPAC names for identification\))/)) {
                                return (
                                  <div key={index} style={{
                                    fontSize: '20px',
                                    fontWeight: 'bold',
                                    color: '#262626',
                                    marginTop: '12px',
                                    marginBottom: '6px'
                                  }}>
                                    {line}
                                  </div>
                                );
                              }
                              return <div key={index} style={{ fontWeight: 'normal' }}>{line}</div>;
                            })
                        )}
                      </div>
                    ),
                  },
                ]}
              />
            </>
          )}

          <Collapse
            defaultActiveKey={['chemicals']}
            style={{ marginBottom: 16 }}
            items={[
              {
                key: 'chemicals',
                label: <span style={{ fontWeight: 700, fontSize: 27 }}>🧪 Chemical Summary</span>,
                children: (
                  <>
                                         <List
                       dataSource={chemicals}
                       renderItem={(c, index) => {
                         console.log(`🔍 [CHEMICAL-SUMMARY] 渲染化學品 ${index}:`, c);
                         console.log(`🔍 [CHEMICAL-SUMMARY] 化學品 ${index} 的鍵:`, Object.keys(c));
                         console.log(`🔍 [CHEMICAL-SUMMARY] 化學品 ${index} 是否有 svg_structure:`, 'svg_structure' in c);
                         console.log(`🔍 [CHEMICAL-SUMMARY] 化學品 ${index} 是否有 png_structure:`, 'png_structure' in c);
                         
                                                  return (
                          <List.Item style={{ padding: '16px 0', borderBottom: '1px solid #f0f0f0' }}>
                            <div style={{ width: '100%' }}>
                              <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-start' }}>
                                {/* Structure Image - 優先使用 SMILES 繪製的結構圖 */}
                                <div style={{ flex: '0 0 150px' }}>
                                  <SmilesDrawer
                                    svgStructure={c.svg_structure}
                                    pngStructure={c.png_structure}
                                    smiles={c.smiles}
                                    name={c.name}
                                    width={120}
                                    height={120}
                                    showSmiles={false}
                                    loading={false}
                                    error={null}
                                  />
                                </div>

                                {/* Chemical Name and Properties */}
                                <div style={{ flex: '1', display: 'flex', gap: '24px' }}>
                                  {/* Properties */}
                                  <div style={{ flex: '1' }}>
                                    <Text strong style={{ fontSize: '24px', marginBottom: '8px', display: 'block' }}>
                                      {c.pubchem_url ? (
                                        <a href={c.pubchem_url} target="_blank" rel="noopener noreferrer" style={{ color: '#1890ff', fontSize: '24px', fontWeight: 'bold' }}>
                                          {c.name}
                                        </a>
                                      ) : (
                                        <span style={{ color: '#1890ff', fontSize: '24px', fontWeight: 'bold' }}>{c.name}</span>
                                      )}
                                    </Text>
                                    <div 
                                      onMouseUp={handleTextSelection}
                                      style={{
                                        fontSize: '14px',
                                        lineHeight: '1.5',
                                        wordBreak: 'break-word',
                                        overflowWrap: 'break-word',
                                        cursor: 'text'
                                      }}
                                    >
                                      <div><strong>Formula:</strong> <code>{c.formula || '-'}</code></div>
                                      <div><strong>MW:</strong> <code>{c.weight || '-'}</code></div>
                                      <div><strong>Boiling Point:</strong> <code>{c.boiling_point_c || '-'}</code></div>
                                      <div><strong>Melting Point:</strong> <code>{c.melting_point_c || '-'}</code></div>
                                      <div><strong>CAS No.:</strong> <code>{c.cas || '-'}</code></div>
                                      <div><strong>SMILES:</strong> <code>{c.smiles || '-'}</code></div>
                                    </div>
                                  </div>

                                  {/* Safety Icons */}
                                  <div style={{ flex: '0 0 150px' }}>
                                    <Text strong style={{ fontSize: '14px', marginBottom: '8px', display: 'block' }}>
                                      Handling Safety
                                    </Text>
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                      {/* NFPA Diamond */}
                                      {c.safety_icons?.nfpa_image && (
                                        <img
                                          src={c.safety_icons.nfpa_image}
                                          alt="NFPA"
                                          style={{ width: '50px', height: '50px' }}
                                        />
                                      )}
                                      {/* GHS Icons */}
                                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', maxWidth: '120px' }}>
                                        {c.safety_icons?.ghs_icons?.map((icon, index) => (
                                          <img
                                            key={index}
                                            src={icon}
                                            alt="GHS"
                                            style={{ width: '40px', height: '40px' }}
                                          />
                                        ))}
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </List.Item>
                         );
                       }}
                      grid={{ gutter: 16, column: 2 }}
                    />
                    {!!notFound.length && (
                      <>
                        <Divider />
                        <Paragraph style={{ color: '#ff4d4f', fontSize: '16px' }}>
                          ⚠️ Not Found: {notFound.join(', ')}
                        </Paragraph>
                      </>
                    )}
                  </>
                ),
              },
            ]}
          />

          {/* Action Buttons - 只在有結果時顯示 */}
          <Card style={{ marginBottom: 16 }}>
            <Space wrap>
              <Button
                size="large"
                onClick={onShowReviseInput}
                loading={loading}
                type={showReviseInput ? "primary" : "default"}
              >
                💡 Generate New Idea
              </Button>
              <Button size="large" onClick={onGenerateExperimentDetail} loading={loading}>
                ✅ Accept & Generate Experiment Detail
              </Button>
            </Space>

            {/* 修訂輸入框 - 點擊 Generate New Idea 後顯示 */}
            {showReviseInput && (
              <div style={{ marginTop: 16, padding: 16, backgroundColor: '#f5f5f5', borderRadius: 6 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                  <Text strong>Enter your revision idea:</Text>
                  <Button
                    type="text"
                    size="small"
                    onClick={() => {
                      setProposalFormData({ showReviseInput: false, reviseFeedback: '' });
                    }}
                  >
                    ✕ Close
                  </Button>
                </div>
                <Space>
                  <TextArea
                    placeholder="Your revision idea"
                    value={reviseFeedback}
                    onChange={(e) => setProposalFormData({ reviseFeedback: e.target.value })}
                    rows={isReviseInputFocused ? 6 : 2}
                    style={{ width: 800 }}
                    onFocus={() => setIsReviseInputFocused(true)}
                    onBlur={() => {
                      setIsReviseInputFocused(false);
                    }}
                    ref={reviseInputRef} // 將 ref 綁定到 TextArea
                  />
                  <Button
                    type="primary"
                    size="large"
                    onClick={() => {
                      console.log('🔍 FRONTEND DEBUG: Revise it! button clicked');
                      onRevise();
                    }}
                    loading={loading}
                  >
                    Revise it!
                  </Button>
                </Space>
              </div>
            )}
          </Card>

          {!!citations.length && (
            <Collapse
              defaultActiveKey={['citations']}
              style={{ marginBottom: 16 }}
              items={[
                {
                  key: 'citations',
                  label: <span style={{ fontWeight: 700, fontSize: 27 }}>📚 Citations</span>,
                  children: (
                    <List
                      dataSource={citations}
                      renderItem={(c, i) => (
                        <List.Item>
                          <Text style={{
                            fontSize: '16px',
                            lineHeight: '1.6',
                            wordBreak: 'break-word',
                            overflowWrap: 'break-word',
                            maxWidth: '100%',
                            width: '100%'
                          }}>
                            [{i + 1}] <a
                              href={`${API_BASE}/documents/${encodeURIComponent(c.source)}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              style={{ color: '#1890ff', textDecoration: 'underline' }}
                            >
                              {c.title || c.source || 'Unknown Title'}
                            </a> | Page {c.page || ''} | Snippet: {c.snippet || ''}
                          </Text>
                        </List.Item>
                      )}
                    />
                  ),
                },
              ]}
            />
          )}
        </>
      )}
    </div>
  );
};

export default Proposal;