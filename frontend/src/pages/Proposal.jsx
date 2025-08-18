import React, { useMemo, useState, useRef } from 'react';
import { Card, Form, Input, Button, message, Space, Typography, List, Tag, Divider, Collapse, Select } from 'antd';

const { Title, Paragraph, Text } = Typography;
const { TextArea } = Input;
const { Option } = Select;

const API_BASE = '/api/v1';

const Proposal = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [proposal, setProposal] = useState('');
  const [chemicals, setChemicals] = useState([]);
  const [notFound, setNotFound] = useState([]);
  const [citations, setCitations] = useState([]);
  const [chunks, setChunks] = useState([]);
  const [experimentDetail, setExperimentDetail] = useState('');
  const [retrievalCount, setRetrievalCount] = useState(10); // 預設檢索 10 個文檔
  const [showReviseInput, setShowReviseInput] = useState(false); // 控制修訂輸入框顯示
  const [reviseFeedback, setReviseFeedback] = useState(''); // 修訂意見
  const [hasGeneratedContent, setHasGeneratedContent] = useState(false); // 追蹤是否已生成內容
  const [isTextareaFocused, setIsTextareaFocused] = useState(false); // 追蹤輸入框是否被聚焦
  const [isReviseInputFocused, setIsReviseInputFocused] = useState(false); // 追蹤修訂輸入框是否被聚焦
  const reviseInputRef = useRef(null); // 修訂輸入框的 ref
  
  // 結構化數據狀態
  const [structuredProposal, setStructuredProposal] = useState(null); // 結構化提案數據

  const hasResult = useMemo(
    () => Boolean(proposal) || chemicals.length > 0 || citations.length > 0,
    [proposal, chemicals, citations]
  );

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
      
      setProposal(data.proposal || '');
      setChemicals(data.chemicals || []);
      setNotFound(data.not_found || []);
      setCitations(data.citations || []);
      setChunks(data.chunks || []);
      setExperimentDetail('');
      setHasGeneratedContent(true); // 設置為已生成內容
      
      // 新增：處理結構化提案數據
      if (data.structured_proposal) {
        setStructuredProposal(data.structured_proposal);
      } else {
        setStructuredProposal(null);
      }
      

      
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
      
      setProposal(data.proposal || '');
      setChemicals(data.chemicals || []);
      setNotFound(data.not_found || []);
      setCitations(data.citations || []);
      setChunks(data.chunks || []);
      setExperimentDetail('');
      setShowReviseInput(false); // 隱藏修訂輸入框
      setReviseFeedback(''); // 清空修訂意見
      setHasGeneratedContent(true); // 設置為已生成內容
      
             // 新增：處理結構化提案數據
       if (data.structured_proposal) {
         setStructuredProposal(data.structured_proposal);
       } else {
         setStructuredProposal(null);
       }
       

      
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
      setShowReviseInput(false);
      setReviseFeedback('');
      setIsReviseInputFocused(false);
    } else {
      // 如果未顯示，則顯示並聚焦
      setShowReviseInput(true);
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
      setExperimentDetail(data.experiment_detail || '');
      
      // 處理結構化實驗細節數據
      if (data.structured_experiment) {
        console.log('🔍 收到結構化實驗細節:', data.structured_experiment);
      }
      
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
        <Form form={form} layout="vertical">
          <Form.Item name="goal" label="Research Goal" rules={[{ required: true, message: 'Please enter your research goal' }]}> 
            <TextArea 
              rows={hasGeneratedContent && !isTextareaFocused ? 1 : 12} 
              placeholder="Please enter your research goal"
              onFocus={() => setIsTextareaFocused(true)}
              onBlur={() => setIsTextareaFocused(false)}
            />
          </Form.Item>

          <Form.Item label="Document Retrieval Count">
            <Select
              value={retrievalCount}
              onChange={setRetrievalCount}
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
          {/* 文本視圖 */}
          <Collapse
            defaultActiveKey={['proposal']}
            style={{ marginBottom: 16 }}
            items={[
              {
                key: 'proposal',
                label: <span style={{ fontWeight: 700, fontSize: 27 }}>🤖 Generated proposal</span>,
                children: (
                  <div style={{ 
                    whiteSpace: 'pre-wrap', 
                    fontSize: '16px', 
                    lineHeight: '1.6',
                    wordBreak: 'break-word',
                    overflowWrap: 'break-word',
                    maxWidth: '100%',
                    width: '100%'
                  }}>
                    {proposal
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
                    }
                  </div>
                ),
              },
            ]}
          />

                    {experimentDetail && (
            <Collapse
              defaultActiveKey={['experiment']}
              style={{ marginBottom: 16 }}
              items={[
                {
                  key: 'experiment',
                   label: <span style={{ fontWeight: 700, fontSize: 27 }}>🔬 Suggested experiment details</span>,
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
                      {experimentDetail
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
                      }
                    </div>
                  ),
                },
              ]}
            />
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
                      renderItem={(c, index) => (
                        <List.Item style={{ padding: '16px 0', borderBottom: '1px solid #f0f0f0' }}>
                          <div style={{ width: '100%' }}>
                            <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-start' }}>
                              {/* Structure Image */}
                              <div style={{ flex: '0 0 150px' }}>
                                {c.image_url && (
                                  <img 
                                    src={c.image_url} 
                                    alt="structure" 
                                    style={{ width: '120px', height: '120px', objectFit: 'contain' }}
                                  />
                                )}
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
                                  <div style={{ 
                                    fontSize: '14px', 
                                    lineHeight: '1.5',
                                    wordBreak: 'break-word',
                                    overflowWrap: 'break-word'
                                  }}>
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
                      )}
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
                      setShowReviseInput(false);
                      setReviseFeedback('');
                    }}
                  >
                    ✕ Close
                  </Button>
                </div>
                <Space>
                  <TextArea
                    placeholder="Your revision idea"
                    value={reviseFeedback}
                    onChange={(e) => setReviseFeedback(e.target.value)}
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