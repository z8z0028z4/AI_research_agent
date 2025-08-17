import React, { useState, useEffect } from 'react';
import { Card, Upload, Button, Typography, Space, message, Progress, List, Tag, Statistic, Row, Col } from 'antd';
import { InboxOutlined, FileTextOutlined, UploadOutlined, DatabaseOutlined } from '@ant-design/icons';
import axios from 'axios';
import { useQuery } from 'react-query';

const { Title, Paragraph } = Typography;
const { Dragger } = Upload;

const UploadPage = () => {
  const [fileList, setFileList] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [taskId, setTaskId] = useState(null);
  const [serverMessage, setServerMessage] = useState('');
  const [results, setResults] = useState(null);
  const [vectorStats, setVectorStats] = useState({ paper_vectors: 0, experiment_vectors: 0, total_vectors: 0 });

  const fetchVectorStats = async () => {
    try {
      const response = await axios.get('/api/v1/upload/stats');
      setVectorStats(response.data);
    } catch (error) {
      console.error('Failed to fetch vector stats:', error);
    }
  };

  const refreshVectorStats = async () => {
    try {
      const response = await axios.post('/api/v1/upload/refresh-stats');
      setVectorStats(response.data);
    } catch (error) {
      console.error('Failed to refresh vector stats:', error);
      fetchVectorStats();
    }
  };

  useEffect(() => {
    fetchVectorStats();
  }, []);

  useQuery(
    ['uploadStatus', taskId],
    async () => {
      const { data } = await axios.get(`/api/v1/upload/status/${taskId}`);
      return data;
    },
    {
      enabled: !!taskId && uploading,
      refetchInterval: 500,
      onSuccess: (data) => {
        const { status, progress, message: msg, results: r } = data;

        const safeProgress = progress !== null && progress !== undefined ? progress : 0;
        setUploadProgress(prev => Math.max(prev, safeProgress));
        setServerMessage(msg || '');

        if (status === 'completed') {
          setResults(r || {});
          setUploading(false);
          setFileList([]);
          setTaskId(null);
          setUploadProgress(100);
          message.success('Processing completed.');
          fetchVectorStats();
        } else if (status === 'failed' || status === 'cancelled') {
          setUploading(false);
          setTaskId(null);
          message.error(msg || 'Processing failed');
        }
      },
      onError: () => {
        message.error('Failed to get processing status');
        setUploading(false);
        setTaskId(null);
      },
    }
  );

  const handleUpload = async () => {
    if (fileList.length === 0) {
      message.warning('Please select files to upload');
      return;
    }

    setUploading(true);
    setUploadProgress(0);
    setServerMessage('');
    setResults(null);
    setTaskId(null);

    const formData = new FormData();
    fileList.forEach((file) => {
      formData.append('files', file);
    });

    try {
      const resp = await axios.post('/api/v1/upload/files', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      const { file_info } = resp.data;
      const newTaskId = file_info?.task_id;
      setTaskId(newTaskId);
      message.success('Upload started. Processing on server...');
    } catch (error) {
      console.error('Upload failed:', error);
      message.error('Upload failed');
      setUploading(false);
    }
  };

  const uploadProps = {
    name: 'file',
    multiple: true,
    fileList: fileList,
    beforeUpload: (file) => {
      // Check file type
      const isAccepted = file.type === 'application/pdf' || 
                        file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ||
                        file.type === 'application/vnd.ms-excel' ||
                        file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
                        file.type === 'text/plain';
      
      if (!isAccepted) {
        message.error('You can only upload PDF, Word, Excel, or text files!');
        return false;
      }

      // Check file size (10MB limit)
      const isLt10M = file.size / 1024 / 1024 < 10;
      if (!isLt10M) {
        message.error('File must be smaller than 10MB!');
        return false;
      }

      setFileList(prev => [...prev, file]);
      return false; // Prevent default upload behavior
    },
    onRemove: (file) => {
      setFileList(prev => prev.filter(item => item.uid !== file.uid));
    },
  };

  const getFileIcon = (file) => {
    if (file.type === 'application/pdf') {
      return <FileTextOutlined style={{ color: '#ff4d4f' }} />;
    } else if (file.type.includes('word')) {
      return <FileTextOutlined style={{ color: '#1890ff' }} />;
    } else if (file.type.includes('excel')) {
      return <FileTextOutlined style={{ color: '#52c41a' }} />;
    } else {
      return <FileTextOutlined style={{ color: '#faad14' }} />;
    }
  };

  return (
    <div>
      <Title level={2}>File Upload</Title>
      <Paragraph>
        Upload research papers, documents, and data files for analysis and processing.
      </Paragraph>

      {/* 向量數據庫統計信息 */}
      <Card 
        title="Vector Database Statistics" 
        style={{ marginBottom: 24 }}
        extra={
          <Button 
            type="primary" 
            size="small" 
            onClick={refreshVectorStats}
            icon={<DatabaseOutlined />}
          >
            Refresh
          </Button>
        }
      >
        <Row gutter={16}>
          <Col span={8}>
            <Statistic
              title="Total Vector Chunks"
              value={vectorStats.total_vectors}
              prefix={<DatabaseOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Col>
          <Col span={8}>
            <Statistic
              title="Paper Vectors"
              value={vectorStats.paper_vectors}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Col>
          <Col span={8}>
            <Statistic
              title="Experiment Vectors"
              value={vectorStats.experiment_vectors}
              prefix={<DatabaseOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Col>
        </Row>
      </Card>

      <Card title="Upload Files" style={{ marginBottom: 24 }}>
        <Dragger {...uploadProps} disabled={uploading}>
          <p className="ant-upload-drag-icon">
            <InboxOutlined />
          </p>
          <p className="ant-upload-text">Click or drag files to this area to upload</p>
          <p className="ant-upload-hint">
            Support for PDF, Word, Excel, and text files. Max file size: 10MB
          </p>
        </Dragger>

        {fileList.length > 0 && (
          <div style={{ marginTop: 16 }}>
            <List
              size="small"
              dataSource={fileList}
              renderItem={(file) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={getFileIcon(file)}
                    title={file.name}
                    description={`${(file.size / 1024 / 1024).toFixed(2)} MB`}
                  />
                </List.Item>
              )}
            />
          </div>
        )}

        {uploading && (
          <div style={{ marginTop: 16 }}>
            <Progress 
              percent={uploadProgress} 
              status="active" 
              strokeColor={{
                '0%': '#108ee9',
                '100%': '#87d068',
              }}
              format={(percent) => `${percent}%`}
            />
            {serverMessage && (
              <div style={{ marginTop: 8 }}>
                <Paragraph style={{ margin: 0, color: '#1890ff' }}>
                  {serverMessage}
                </Paragraph>
                {/* 根據進度顯示處理階段 */}
                <div style={{ marginTop: 4 }}>
                  {uploadProgress >= 0 && uploadProgress < 25 && (
                    <Tag color="blue">🔍 文件分析階段</Tag>
                  )}
                  {uploadProgress >= 25 && uploadProgress < 50 && (
                    <Tag color="orange">📄 元數據提取階段</Tag>
                  )}
                  {uploadProgress >= 50 && uploadProgress < 95 && (
                    <Tag color="green">🔢 向量嵌入階段</Tag>
                  )}
                  {uploadProgress >= 95 && uploadProgress < 98 && (
                    <Tag color="cyan">📊 統計更新階段</Tag>
                  )}
                  {uploadProgress >= 98 && uploadProgress < 100 && (
                    <Tag color="purple">🎯 完成處理階段</Tag>
                  )}
                  {uploadProgress === 100 && (
                    <Tag color="success">✅ 處理完成</Tag>
                  )}
                </div>
                {/* 根據消息內容顯示詳細狀態 */}
                {uploadProgress > 0 && uploadProgress < 100 && (
                  <div style={{ marginTop: 4 }}>
                    {(serverMessage.includes('分析文件類型') || serverMessage.includes('開始處理論文資料')) && (
                      <Tag color="blue">🔍 文件分析</Tag>
                    )}
                    {(serverMessage.includes('提取文件元數據') || serverMessage.includes('提取第') && serverMessage.includes('個文件元數據')) && (
                      <Tag color="blue">📄 提取文件元數據</Tag>
                    )}
                    {(serverMessage.includes('檢查') && serverMessage.includes('重複')) && (
                      <Tag color="orange">🔍 檢查文件重複</Tag>
                    )}
                    {(serverMessage.includes('開始文件分塊處理') || (serverMessage.includes('處理第') && serverMessage.includes('個文件：'))) && (
                      <Tag color="cyan">📚 文件分塊處理</Tag>
                    )}
                    {(serverMessage.includes('開始向量嵌入') || serverMessage.includes('向量嵌入批次')) && (
                      <Tag color="green">🔢 向量嵌入處理</Tag>
                    )}
                    {(serverMessage.includes('處理實驗資料') || serverMessage.includes('處理實驗文件')) && (
                      <Tag color="purple">🧪 處理實驗數據</Tag>
                    )}
                    {serverMessage.includes('完成處理') && (
                      <Tag color="success">✅ 完成處理</Tag>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        <div style={{ marginTop: 16 }}>
          <Space>
            <Button
              type="primary"
              icon={<UploadOutlined />}
              onClick={handleUpload}
              loading={uploading}
              disabled={fileList.length === 0}
            >
              {uploading ? 'Uploading...' : 'Upload Files'}
            </Button>
            <Button 
              onClick={() => setFileList([])}
              disabled={fileList.length === 0 || uploading}
            >
              Clear All
            </Button>
          </Space>
        </div>
      </Card>

      {results && (
        <Card title="Processing Results" style={{ marginBottom: 24 }}>
          <Paragraph>Embedding finished. Summary:</Paragraph>
          <ul>
            {results.file_info && (
              <li>
                Files classified: 
                <Space size="small" style={{ marginLeft: 8 }}>
                  <Tag color="blue">papers: {results.file_info.papers?.length || 0}</Tag>
                  <Tag color="green">experiments: {results.file_info.experiments?.length || 0}</Tag>
                  {results.file_info.others && results.file_info.others.length > 0 && (
                    <Tag>others: {results.file_info.others.length}</Tag>
                  )}
                </Space>
              </li>
            )}
            {Array.isArray(results.paper_results) && (
              <li>Paper metadata processed: {results.paper_results.length}</li>
            )}
            {Array.isArray(results.experiment_results) && (
              <li>Experiment txt embedded: {results.experiment_results.reduce((acc, x) => acc + (x.embedded_count || 0), 0)}</li>
            )}
            {results.vector_stats && (
              <li>
                Vector chunks in database: 
                <Space size="small" style={{ marginLeft: 8 }}>
                  <Tag color="blue">papers: {results.vector_stats.paper_vectors || 0}</Tag>
                  <Tag color="green">experiments: {results.vector_stats.experiment_vectors || 0}</Tag>
                </Space>
              </li>
            )}
          </ul>
        </Card>
      )}

      <Card title="Upload Guidelines">
        <ul>
          <li>Supported file types: PDF, Word (.docx), Excel (.xlsx), and text files</li>
          <li>Maximum file size: 10MB per file</li>
          <li>Files will be processed for text extraction and analysis</li>
          <li>Uploaded files will be stored securely and can be accessed later</li>
        </ul>
      </Card>
    </div>
  );
};

export default UploadPage; 