import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Input, 
  Button, 
  List, 
  Typography, 
  Space, 
  Select, 
  message, 
  Row, 
  Col, 
  Statistic,
  Tag,
  Divider,
  Spin,
  Empty,
  Tooltip
} from 'antd';
import { 
  SearchOutlined, 
  FileTextOutlined, 
  ExperimentOutlined,
  DownloadOutlined,
  EyeOutlined,
  FolderOutlined,
  FilePdfOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { Title, Paragraph } = Typography;
const { Search } = Input;
const { Option } = Select;

const SearchPage = () => {
  const [loading, setLoading] = useState(false);
  const [paperLoading, setPaperLoading] = useState(false);
  const [papers, setPapers] = useState([]);
  const [paperStats, setPaperStats] = useState({});
  const [searchQuery, setSearchQuery] = useState('');
  const [searchType, setSearchType] = useState('all');
  const [results, setResults] = useState([]);
  const [hasSearched, setHasSearched] = useState(false);

  // 載入文獻統計資訊
  const loadPaperStats = async () => {
    try {
      const response = await axios.get('/api/v1/paper/stats');
      setPaperStats(response.data);
    } catch (error) {
      console.error('獲取文獻統計失敗:', error);
    }
  };

  // 載入文獻列表
  const loadPapers = async (search = '') => {
    setPaperLoading(true);
    try {
      const params = search ? { search, limit: 100 } : { limit: 100 };
      const response = await axios.get('/api/v1/paper/list', { params });
      setPapers(response.data.papers || []);
    } catch (error) {
      console.error('載入文獻列表失敗:', error);
      message.error('載入文獻列表失敗');
    } finally {
      setPaperLoading(false);
    }
  };

  // 搜尋文獻
  const searchPapers = async (query) => {
    if (!query.trim()) {
      message.warning('請輸入搜尋關鍵字');
      return;
    }

    setLoading(true);
    try {
      const response = await axios.get('/api/v1/paper/search', {
        params: { query, limit: 50 }
      });
      setResults(response.data.papers || []);
      setHasSearched(true);
      message.success(`找到 ${response.data.total_count} 個文獻`);
    } catch (error) {
      console.error('搜尋文獻失敗:', error);
      message.error('搜尋文獻失敗');
    } finally {
      setLoading(false);
    }
  };

  // 處理搜尋
  const handleSearch = async () => {
    if (searchType === 'papers' || searchType === 'all') {
      await searchPapers(searchQuery);
    } else {
      // 其他類型的搜尋（實驗等）
      message.info('此功能尚未實現');
    }
  };

  // 下載文獻
  const downloadPaper = (filename) => {
    const downloadUrl = `/api/v1/paper/download/${filename}`;
    window.open(downloadUrl, '_blank');
  };

  // 查看文獻
  const viewPaper = (filename) => {
    const viewUrl = `/api/v1/paper/view/${filename}`;
    window.open(viewUrl, '_blank');
  };

  // 格式化文件大小
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // 格式化時間
  const formatTime = (timestamp) => {
    return new Date(timestamp * 1000).toLocaleString('zh-TW');
  };

  // 渲染文獻項目
  const renderPaperItem = (paper) => (
    <List.Item
      actions={[
        <Tooltip title="查看文獻">
          <Button 
            type="link" 
            icon={<EyeOutlined />} 
            onClick={() => viewPaper(paper.filename)}
          >
            查看
          </Button>
        </Tooltip>,
        <Tooltip title="下載文獻">
          <Button 
            type="link" 
            icon={<DownloadOutlined />} 
            onClick={() => downloadPaper(paper.filename)}
          >
            下載
          </Button>
        </Tooltip>
      ]}
    >
      <List.Item.Meta
        avatar={<FilePdfOutlined style={{ fontSize: '24px', color: '#ff4d4f' }} />}
        title={
          <Space>
            <span>{paper.display_name}</span>
            <Tag color="blue">PDF</Tag>
          </Space>
        }
        description={
          <div>
            <div><strong>文件名:</strong> {paper.filename}</div>
            <div><strong>文件大小:</strong> {formatFileSize(paper.size)}</div>
            <div><strong>修改時間:</strong> {formatTime(paper.modified_time)}</div>
            <div><strong>文獻ID:</strong> {paper.paper_id}</div>
          </div>
        }
      />
    </List.Item>
  );

  // 渲染搜尋結果
  const renderSearchResult = (paper) => (
    <List.Item
      actions={[
        <Tooltip title="查看文獻">
          <Button 
            type="link" 
            icon={<EyeOutlined />} 
            onClick={() => viewPaper(paper.filename)}
          >
            查看
          </Button>
        </Tooltip>,
        <Tooltip title="下載文獻">
          <Button 
            type="link" 
            icon={<DownloadOutlined />} 
            onClick={() => downloadPaper(paper.filename)}
          >
            下載
          </Button>
        </Tooltip>
      ]}
    >
      <List.Item.Meta
        avatar={<FilePdfOutlined style={{ fontSize: '24px', color: '#ff4d4f' }} />}
        title={
          <Space>
            <span>{paper.display_name}</span>
            <Tag color="blue">PDF</Tag>
            {paper.match_score > 0 && <Tag color="green">匹配度: {paper.match_score}</Tag>}
          </Space>
        }
        description={
          <div>
            <div><strong>文件名:</strong> {paper.filename}</div>
            <div><strong>文件大小:</strong> {formatFileSize(paper.size)}</div>
            <div><strong>修改時間:</strong> {formatTime(paper.modified_time)}</div>
          </div>
        }
      />
    </List.Item>
  );

  // 初始化載入
  useEffect(() => {
    loadPaperStats();
    loadPapers();
  }, []);

  return (
    <div>
      <Title level={2}>文獻搜尋與瀏覽</Title>
      <Paragraph>
        瀏覽和搜尋 papers/ 資料夾中的文獻文件，支援線上查看和下載功能。
      </Paragraph>

      {/* 文獻統計資訊 */}
      <Card title="文獻統計" style={{ marginBottom: 24 }}>
        <Row gutter={16}>
          <Col span={6}>
            <Statistic
              title="總文獻數"
              value={paperStats.total_papers || 0}
              prefix={<FileTextOutlined />}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="總大小"
              value={paperStats.total_size_mb || 0}
              suffix="MB"
              prefix={<FolderOutlined />}
            />
          </Col>
          <Col span={6}>
            <Statistic
              title="資料夾"
              value={paperStats.directory || 'experiment_data/papers'}
              prefix={<FolderOutlined />}
            />
          </Col>
          <Col span={6}>
            <Button 
              icon={<ReloadOutlined />} 
              onClick={loadPaperStats}
              loading={paperLoading}
            >
              刷新統計
            </Button>
          </Col>
        </Row>
      </Card>

      {/* 搜尋功能 */}
      <Card title="文獻搜尋" style={{ marginBottom: 24 }}>
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Space>
            <Search
              placeholder="輸入搜尋關鍵字..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onPressEnter={handleSearch}
              style={{ width: 400 }}
            />
            <Select
              value={searchType}
              onChange={setSearchType}
              style={{ width: 150 }}
            >
              <Option value="papers">文獻</Option>
              <Option value="experiments">實驗</Option>
              <Option value="all">全部</Option>
            </Select>
            <Button
              type="primary"
              icon={<SearchOutlined />}
              onClick={handleSearch}
              loading={loading}
            >
              搜尋
            </Button>
          </Space>
        </Space>
      </Card>

      {/* 搜尋結果 */}
      {hasSearched && (
        <Card title={`搜尋結果 (${results.length})`} style={{ marginBottom: 24 }}>
          {results.length > 0 ? (
            <List
              itemLayout="horizontal"
              dataSource={results}
              renderItem={renderSearchResult}
            />
          ) : (
            <Empty description="沒有找到匹配的文獻" />
          )}
        </Card>
      )}

      <Divider />

      {/* 文獻瀏覽 */}
      <Card 
        title="文獻瀏覽" 
        extra={
          <Space>
            <Search
              placeholder="篩選文獻..."
              onSearch={loadPapers}
              style={{ width: 200 }}
              allowClear
            />
            <Button 
              icon={<ReloadOutlined />} 
              onClick={() => loadPapers()}
              loading={paperLoading}
            >
              刷新
            </Button>
          </Space>
        }
      >
        <Spin spinning={paperLoading}>
          {papers.length > 0 ? (
            <List
              itemLayout="horizontal"
              dataSource={papers}
              renderItem={renderPaperItem}
              pagination={{
                pageSize: 10,
                showSizeChanger: true,
                showQuickJumper: true,
                showTotal: (total, range) => 
                  `第 ${range[0]}-${range[1]} 項，共 ${total} 項`
              }}
            />
          ) : (
            <Empty description="沒有找到文獻文件" />
          )}
        </Spin>
      </Card>
    </div>
  );
};

export default SearchPage;