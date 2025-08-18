import React, { useMemo, useState } from 'react';
import { Card, Form, Input, Button, message, Space, Typography, List, Tag, Divider, Select, Radio, Collapse } from 'antd';

const { Title, Paragraph, Text } = Typography;
const { TextArea } = Input;
const { Option } = Select;

const API_BASE = '/api/v1';

const KnowledgeQuery = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [answer, setAnswer] = useState('');
  const [citations, setCitations] = useState([]);
  const [chunks, setChunks] = useState([]);
  const [retrievalCount, setRetrievalCount] = useState(10); // 預設檢索 10 個文檔
  const [answerMode, setAnswerMode] = useState('rigorous'); // 預設嚴謹模式

  const hasResult = useMemo(
    () => Boolean(answer) || citations.length > 0,
    [answer, citations]
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

  const onQuery = async () => {
    const question = form.getFieldValue('question');
    if (!question) return message.warning('Please enter your question');
    setLoading(true);
    try {
      const data = await callApi('/knowledge/query', {
        body: JSON.stringify({ 
          question: question,
          retrieval_count: retrievalCount,
          answer_mode: answerMode
        }),
      });
      setAnswer(data.answer || '');
      setCitations(data.citations || []);
      setChunks(data.chunks || []);
    } catch (e) {
      showError(e, 'Query failed');
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const onClear = () => {
    form.resetFields();
    setAnswer('');
    setCitations([]);
    setChunks([]);
  };

  return (
    <div>
      <Title level={2}>Knowledge Query</Title>
      <Paragraph>
        Intelligent Q&A based on uploaded literature, supporting rigorous citation and inference modes.
      </Paragraph>

      <Card title="Query Settings" style={{ marginBottom: 16 }}>
        <Form form={form} layout="vertical">
          <Form.Item
            label="Query Question"
            name="question"
            rules={[{ required: true, message: 'Please enter your question' }]}
          >
            <TextArea
              rows={4}
              placeholder="Enter your question, e.g., 'Please introduce the synthesis methods of metal-organic framework materials'"
            />
          </Form.Item>

          <Space direction="vertical" style={{ width: '100%' }}>
            <div>
              <Text strong>Answer Mode:</Text>
              <Radio.Group 
                value={answerMode} 
                onChange={(e) => setAnswerMode(e.target.value)}
                style={{ marginLeft: 16 }}
              >
                <Radio.Button value="rigorous">Rigorous Citation</Radio.Button>
                <Radio.Button value="inference">Inference</Radio.Button>
              </Radio.Group>
            </div>

            <div>
              <Text strong>Retrieval Count:</Text>
              <Select
                value={retrievalCount}
                onChange={setRetrievalCount}
                style={{ width: 120, marginLeft: 16 }}
              >
                <Option value={5}>5 docs</Option>
                <Option value={10}>10 docs</Option>
                <Option value={15}>15 docs</Option>
                <Option value={20}>20 docs</Option>
                <Option value={25}>25 docs</Option>
                <Option value={30}>30 docs</Option>
              </Select>
            </div>
          </Space>

          <Form.Item style={{ marginTop: 16 }}>
            <Space>
              <Button 
                type="primary" 
                onClick={onQuery} 
                loading={loading}
                size="large"
              >
                Start Query
              </Button>
              <Button onClick={onClear} size="large">
                Clear Results
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>

      {hasResult && (
        <>
          {/* Query Result Summary */}
          <Card style={{ marginBottom: 16 }}>
            <div style={{ marginBottom: 16 }}>
              <Tag color="blue">Mode: {answerMode === 'rigorous' ? 'Rigorous Citation' : 'Inference'}</Tag>
              <Tag color="green">Retrieval: {retrievalCount} docs</Tag>
              <Tag color="orange">Found: {chunks.length} docs</Tag>
            </div>
          </Card>

          {/* AI Answer - Collapsible Card */}
          <Collapse
            defaultActiveKey={['answer']}
            style={{ marginBottom: 16 }}
            items={[
              {
                key: 'answer',
                label: <span style={{ fontWeight: 700, fontSize: 27 }}>🤖 AI Answer</span>,
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
                    {answer
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
                        // 檢查是否為主要標題行
                        if (line.match(/^(推薦|Recommendation|結論|Conclusion|總結|Summary|分析|Analysis|討論|Discussion)/)) {
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

          {/* Citations - Collapsible Card */}
          {citations.length > 0 && (
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
                      renderItem={(citation, index) => (
                        <List.Item style={{ padding: '16px 0', borderBottom: '1px solid #f0f0f0' }}>
                          <div style={{ width: '100%' }}>
                            <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-start' }}>
                              {/* Citation Label */}
                              <div style={{ flex: '0 0 60px' }}>
                                <Tag color="blue" style={{ fontSize: '16px', fontWeight: 'bold' }}>
                                  {citation.label}
                                </Tag>
                              </div>

                              {/* Citation Content */}
                              <div style={{ flex: '1' }}>
                                <Text strong style={{ fontSize: '18px', marginBottom: '8px', display: 'block', color: '#1890ff' }}>
                                  <a 
                                    href={`${API_BASE}/documents/${encodeURIComponent(citation.source)}`} 
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    style={{ color: '#1890ff', textDecoration: 'underline' }}
                                  >
                                    {citation.title || citation.source || 'Unknown Title'}
                                  </a>
                                </Text>
                                <div style={{ 
                                  fontSize: '14px', 
                                  lineHeight: '1.5',
                                  wordBreak: 'break-word',
                                  overflowWrap: 'break-word'
                                }}>
                                  <div><strong>Source:</strong> {citation.source}</div>
                                  {citation.page && citation.page !== '?' && (
                                    <div><strong>Page:</strong> {citation.page}</div>
                                  )}
                                  <div style={{ marginTop: '8px' }}>
                                    <strong>Snippet:</strong> {citation.snippet}
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </List.Item>
                      )}
                    />
                  ),
                },
              ]}
            />
          )}

          {/* Retrieved Document Chunks - Collapsible Card */}
          {chunks.length > 0 && (
            <Collapse
              defaultActiveKey={['chunks']}
              style={{ marginBottom: 16 }}
              items={[
                {
                  key: 'chunks',
                  label: <span style={{ fontWeight: 700, fontSize: 27 }}>📄 Retrieved Document Chunks</span>,
                  children: (
                    <List
                      dataSource={chunks}
                      renderItem={(chunk, index) => (
                        <List.Item style={{ padding: '16px 0', borderBottom: '1px solid #f0f0f0' }}>
                          <div style={{ width: '100%' }}>
                            <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-start' }}>
                              {/* Chunk Number */}
                              <div style={{ flex: '0 0 80px' }}>
                                <Tag color="green" style={{ fontSize: '16px', fontWeight: 'bold' }}>
                                  Chunk {index + 1}
                                </Tag>
                              </div>

                              {/* Chunk Content */}
                              <div style={{ flex: '1' }}>
                                <Text strong style={{ fontSize: '18px', marginBottom: '8px', display: 'block', color: '#1890ff' }}>
                                  {chunk.metadata?.title || chunk.metadata?.filename || 'Unknown Title'}
                                </Text>
                                <div style={{ 
                                  fontSize: '14px', 
                                  lineHeight: '1.5',
                                  wordBreak: 'break-word',
                                  overflowWrap: 'break-word'
                                }}>
                                  <div><strong>Source:</strong> {chunk.metadata?.filename || chunk.metadata?.source || 'Unknown Source'}</div>
                                  {chunk.metadata?.page_number && (
                                    <div><strong>Page:</strong> {chunk.metadata.page_number}</div>
                                  )}
                                  <div style={{ 
                                    marginTop: '12px', 
                                    background: '#f8f9fa', 
                                    padding: '12px', 
                                    borderRadius: '6px',
                                    maxHeight: '200px',
                                    overflow: 'auto',
                                    fontSize: '14px',
                                    lineHeight: '1.6'
                                  }}>
                                    <Text>{chunk.page_content}</Text>
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
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

export default KnowledgeQuery; 