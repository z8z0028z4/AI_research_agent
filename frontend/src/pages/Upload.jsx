import React, { useState, useRef, useEffect } from 'react';
import { Card, Upload, Button, Typography, Space, message, Progress, List, Tag, Statistic, Row, Col } from 'antd';
import { InboxOutlined, FileTextOutlined, UploadOutlined, DatabaseOutlined } from '@ant-design/icons';
import axios from 'axios';

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
  const pollingRef = useRef(null);

  // 獲取向量統計信息
  const fetchVectorStats = async () => {
    try {
      console.log('📊 開始獲取向量統計信息...');
      const response = await axios.get('/api/v1/upload/stats', {
        timeout: 5000, // 5秒超時
        headers: {
          'Content-Type': 'application/json',
        }
      });
      console.log('📊 向量統計響應:', response.data);
      setVectorStats(response.data);
    } catch (error) {
      console.error('❌ 獲取向量統計失敗:', error);
      // 如果是網絡錯誤，設置默認值
      if (error.code === 'ECONNREFUSED' || error.code === 'ERR_NETWORK') {
        console.log('⚠️ 後端不可用，使用默認統計');
        setVectorStats({ paper_vectors: 0, experiment_vectors: 0, total_vectors: 0 });
      }
    }
  };

  // 刷新向量統計信息（重新計算）
  const refreshVectorStats = async () => {
    try {
      console.log('🔄 開始刷新向量統計信息...');
      const response = await axios.post('/api/v1/upload/refresh-stats', {}, {
        timeout: 10000, // 10秒超時，因為需要重新計算
        headers: {
          'Content-Type': 'application/json',
        }
      });
      console.log('🔄 向量統計刷新響應:', response.data);
      setVectorStats(response.data);
    } catch (error) {
      console.error('❌ 刷新向量統計失敗:', error);
      // 如果刷新失敗，嘗試獲取緩存數據
      fetchVectorStats();
    }
  };

  // 頁面加載時獲取統計信息（現在使用後端緩存，響應更快）
  useEffect(() => {
    fetchVectorStats();
  }, []);

  const handleUpload = async () => {
    if (fileList.length === 0) {
      message.warning('Please select files to upload');
      return;
    }

    console.log('🚀 開始文件上傳流程...');
    console.log('📁 選中的文件:', fileList.map(f => f.name));

    setUploading(true);
    setUploadProgress(0);
    setServerMessage('');
    setResults(null);

    try {
      const formData = new FormData();
      fileList.forEach((file) => {
        formData.append('files', file);
        console.log('📄 添加文件到FormData:', file.name, '大小:', file.size);
      });

      console.log('📤 開始上傳文件到後端...');
      const resp = await axios.post('/api/v1/upload/files', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (evt) => {
          // 移除文件上傳進度顯示，只顯示工作流程進度
          // 文件上傳完成後，進度條會從後端更新
        },
      });

      console.log('✅ 文件上傳成功，響應:', resp.data);
      const { file_info } = resp.data;
      const newTaskId = file_info?.task_id;
      console.log('🆔 任務ID:', newTaskId);
      setTaskId(newTaskId);
      message.success('Upload started. Processing on server...');

      // 開始輪詢任務狀態
      const poll = async () => {
        try {
          console.log('🔄 開始輪詢任務狀態:', newTaskId);
          const statusResp = await axios.get(`/api/v1/upload/status/${newTaskId}`);
          const { status, progress, message: msg, results: r } = statusResp.data;
          
          console.log('📊 後端狀態響應:', {
            status,
            progress,
            message: msg,
            hasResults: !!r
          });
          
          // 直接同步後端進度：後端進度就是前端進度
          // 處理progress可能為null或undefined的情況
          const safeProgress = progress !== null && progress !== undefined ? progress : 0;
          // 直接使用後端進度，不再轉換
          const backendProgress = safeProgress;
          console.log('📈 進度同步:', {
            後端進度: progress,
            安全進度: safeProgress,
            前端進度: backendProgress,
            說明: '直接同步後端進度'
          });
          
          // 確保進度不會倒退，只會向前更新
          setUploadProgress(prevProgress => {
            const newProgress = Math.max(prevProgress, backendProgress);
            if (newProgress !== prevProgress) {
              console.log(`📈 進度更新: ${prevProgress}% → ${newProgress}%`);
            }
            return newProgress;
          });
          setServerMessage(msg || '');
          
          if (status === 'completed') {
            console.log('✅ 任務完成，結果:', r);
            setResults(r || {});
            setUploading(false);
            setFileList([]);
            setTaskId(null);
            setUploadProgress(100);
            pollingRef.current && clearTimeout(pollingRef.current);
            message.success('Processing completed.');
            // 更新統計信息
            fetchVectorStats();
            return;
          }
          if (status === 'failed' || status === 'cancelled') {
            console.log('❌ 任務失敗或取消:', status, msg);
            setUploading(false);
            setTaskId(null);
            pollingRef.current && clearTimeout(pollingRef.current);
            message.error(msg || 'Processing failed');
            return;
          }
          
          console.log('⏳ 任務進行中，繼續輪詢...');
          // 繼續輪詢，縮短輪詢間隔以更頻繁地更新進度
          pollingRef.current = setTimeout(poll, 500);
        } catch (e) {
          console.error('❌ 輪詢狀態失敗:', e);
          pollingRef.current && clearTimeout(pollingRef.current);
          setUploading(false);
          setTaskId(null);
          message.error('Failed to get processing status');
        }
      };
      poll();

    } catch (error) {
      console.error('❌ 文件上傳失敗:', error);
      message.error('Upload failed');
      setUploading(false);
      setUploadProgress(0);
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