import React, { useState } from 'react';
import { Card, Input, Button, List, Typography, Space, Select, message } from 'antd';
import { SearchOutlined, FileTextOutlined, ExperimentOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Title, Paragraph } = Typography;
const { Search } = Input;
const { Option } = Select;

const API_URL = 'http://localhost:8000/api/v1';

const SearchPage = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchType, setSearchType] = useState('papers');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      message.warning('Please enter a search query');
      return;
    }

    setLoading(true);
    setResults([]);

    if (searchType !== 'papers') {
      message.warning('Search for experiments and other types is not yet implemented.');
      setLoading(false);
      return;
    }

    try {
      const response = await axios.post(`${API_URL}/search/literature`, {
        query: searchQuery,
        max_results: 10,
      });

      if (response.data.success) {
        const aipResults = response.data.results.map((item, index) => ({
          id: index,
          title: item.filename,
          size: item.size,
          type: 'paper',
        }));
        setResults(aipResults);
        message.success(response.data.message || `Found ${response.data.total_count} results`);
      } else {
        message.error(response.data.message || 'Search failed');
      }
    } catch (error) {
      message.error('An error occurred during the search.');
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderResultItem = (item) => {
    if (item.type === 'paper') {
      return (
        <List.Item>
          <List.Item.Meta
            avatar={<FileTextOutlined style={{ fontSize: '24px', color: '#1890ff' }} />}
            title={item.title}
            description={`Size: ${(item.size / 1024).toFixed(2)} KB`}
          />
        </List.Item>
      );
    } else {
      // This part is not used for now, but kept for future implementation
      return (
        <List.Item>
          <List.Item.Meta
            avatar={<ExperimentOutlined style={{ fontSize: '24px', color: '#52c41a' }} />}
            title={item.title}
            description={item.description}
          />
        </List.Item>
      );
    }
  };

  return (
    <div>
      <Title level={2}>Research Search</Title>
      <Paragraph>
        Search through papers, experiments, and research data.
      </Paragraph>

      <Card title="Search" style={{ marginBottom: 24 }}>
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Space>
            <Search
              placeholder="Enter your search query..."
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
              <Option value="papers">Papers</Option>
              <Option value="experiments">Experiments</Option>
              <Option value="all">All</Option>
            </Select>
            <Button
              type="primary"
              icon={<SearchOutlined />}
              onClick={handleSearch}
              loading={loading}
            >
              Search
            </Button>
          </Space>
        </Space>
      </Card>

      {results.length > 0 && (
        <Card title={`Search Results (${results.length})`}>
          <List
            itemLayout="horizontal"
            dataSource={results}
            renderItem={renderResultItem}
          />
        </Card>
      )}
    </div>
  );
};

export default SearchPage; 