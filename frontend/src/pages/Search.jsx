import React, { useState } from 'react';
import { Card, Input, Button, List, Typography, Space, Select, message } from 'antd';
import { SearchOutlined, FileTextOutlined, ExperimentOutlined } from '@ant-design/icons';

const { Title, Paragraph } = Typography;
const { Search } = Input;
const { Option } = Select;

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
    try {
      // TODO: Implement API call to backend
      console.log('Searching for:', searchQuery, 'Type:', searchType);
      
      // Mock results for now
      const mockResults = [
        {
          id: 1,
          title: 'Sample Research Paper',
          authors: 'John Doe, Jane Smith',
          abstract: 'This is a sample research paper abstract...',
          type: 'paper'
        },
        {
          id: 2,
          title: 'Sample Experiment',
          description: 'This is a sample experiment description...',
          type: 'experiment'
        }
      ];
      
      setResults(mockResults);
      message.success(`Found ${mockResults.length} results`);
    } catch (error) {
      message.error('Search failed');
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
            description={
              <div>
                <div><strong>Authors:</strong> {item.authors}</div>
                <div><strong>Abstract:</strong> {item.abstract}</div>
              </div>
            }
          />
        </List.Item>
      );
    } else {
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