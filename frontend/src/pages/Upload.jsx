import React, { useState, useRef } from 'react';
import { Card, Upload, Button, Typography, Space, message, Progress, List, Tag } from 'antd';
import { InboxOutlined, FileTextOutlined, UploadOutlined } from '@ant-design/icons';
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
  const pollingRef = useRef(null);

  const handleUpload = async () => {
    if (fileList.length === 0) {
      message.warning('Please select files to upload');
      return;
    }

    setUploading(true);
    setUploadProgress(0);
    setServerMessage('');
    setResults(null);

    try {
      const formData = new FormData();
      fileList.forEach((file) => {
        formData.append('files', file);
      });

      const resp = await axios.post('/api/v1/upload/files', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (evt) => {
          if (evt.total) {
            const percent = Math.round((evt.loaded * 100) / evt.total);
            setUploadProgress(percent > 95 ? 95 : percent); // 95% 前為上傳進度，剩餘由後端處理進度更新
          }
        },
      });

      const { file_info } = resp.data;
      const newTaskId = file_info?.task_id;
      setTaskId(newTaskId);
      message.success('Upload started. Processing on server...');

      // 開始輪詢任務狀態
      const poll = async () => {
        try {
          const statusResp = await axios.get(`/api/v1/upload/status/${newTaskId}`);
          const { status, progress, message: msg, results: r } = statusResp.data;
          setUploadProgress(progress);
          setServerMessage(msg || '');
          if (status === 'completed') {
            setResults(r || {});
            setUploading(false);
            setFileList([]);
            setTaskId(null);
            setUploadProgress(100);
            pollingRef.current && clearTimeout(pollingRef.current);
            message.success('Processing completed.');
            return;
          }
          if (status === 'failed' || status === 'cancelled') {
            setUploading(false);
            setTaskId(null);
            pollingRef.current && clearTimeout(pollingRef.current);
            message.error(msg || 'Processing failed');
            return;
          }
          // 繼續輪詢
          pollingRef.current = setTimeout(poll, 1000);
        } catch (e) {
          pollingRef.current && clearTimeout(pollingRef.current);
          setUploading(false);
          setTaskId(null);
          message.error('Failed to get processing status');
        }
      };
      poll();

    } catch (error) {
      message.error('Upload failed');
      console.error('Upload error:', error);
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
            <Progress percent={uploadProgress} status="active" />
            {serverMessage && (
              <Paragraph style={{ marginTop: 8 }}>{serverMessage}</Paragraph>
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