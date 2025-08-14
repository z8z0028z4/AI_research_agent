import React, { useState } from 'react';
import { Card, Input, Button, Table, Typography, Space, message, Tag } from 'antd';
import { SearchOutlined, ExperimentOutlined } from '@ant-design/icons';

const { Title, Paragraph } = Typography;
const { Search } = Input;

const Chemical = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [chemicalData, setChemicalData] = useState(null);

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      message.warning('Please enter a chemical name or formula');
      return;
    }

    setLoading(true);
    try {
      // TODO: Implement API call to backend
      console.log('Searching for chemical:', searchQuery);
      
      // Mock chemical data
      const mockData = {
        name: searchQuery,
        formula: 'C6H12O6',
        molecularWeight: '180.16 g/mol',
        casNumber: '50-99-7',
        properties: {
          meltingPoint: '146°C',
          boilingPoint: 'Decomposes',
          density: '1.54 g/cm³',
          solubility: 'Soluble in water'
        },
        structure: 'Sample structure data',
        safety: {
          hazards: ['Irritant'],
          precautions: ['Wear protective equipment']
        }
      };
      
      setChemicalData(mockData);
      message.success('Chemical information found');
    } catch (error) {
      message.error('Failed to find chemical information');
      console.error('Chemical search error:', error);
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    {
      title: 'Property',
      dataIndex: 'property',
      key: 'property',
      width: '30%',
    },
    {
      title: 'Value',
      dataIndex: 'value',
      key: 'value',
      width: '70%',
    },
  ];

  const renderChemicalInfo = () => {
    if (!chemicalData) return null;

    const propertiesData = [
      { key: '1', property: 'Molecular Formula', value: chemicalData.formula },
      { key: '2', property: 'Molecular Weight', value: chemicalData.molecularWeight },
      { key: '3', property: 'CAS Number', value: chemicalData.casNumber },
      { key: '4', property: 'Melting Point', value: chemicalData.properties.meltingPoint },
      { key: '5', property: 'Boiling Point', value: chemicalData.properties.boilingPoint },
      { key: '6', property: 'Density', value: chemicalData.properties.density },
      { key: '7', property: 'Solubility', value: chemicalData.properties.solubility },
    ];

    return (
      <div>
        <Card 
          title="Chemical Properties" 
          style={{ 
            marginBottom: 16,
            fontSize: '16px'
          }}
          headStyle={{
            fontSize: '18px',
            fontWeight: 'bold',
            color: '#1890ff'
          }}
        >
          <Table
            columns={columns}
            dataSource={propertiesData}
            pagination={false}
            size="small"
            style={{
              fontSize: '16px'
            }}
          />
        </Card>

        <Card 
          title="Safety Information" 
          style={{ 
            marginBottom: 16,
            fontSize: '16px'
          }}
          headStyle={{
            fontSize: '18px',
            fontWeight: 'bold',
            color: '#1890ff'
          }}
        >
          <Space direction="vertical" style={{ width: '100%' }}>
            <div style={{ fontSize: '16px' }}>
              <strong>Hazards:</strong>
              <Space style={{ marginLeft: 8 }}>
                {chemicalData.safety.hazards.map((hazard, index) => (
                  <Tag key={index} color="red" style={{ fontSize: '14px' }}>{hazard}</Tag>
                ))}
              </Space>
            </div>
            <div>
              <strong>Precautions:</strong>
              <ul style={{ margin: '8px 0 0 0' }}>
                {chemicalData.safety.precautions.map((precaution, index) => (
                  <li key={index}>{precaution}</li>
                ))}
              </ul>
            </div>
          </Space>
        </Card>

        <Card title="Molecular Structure">
          <div style={{ textAlign: 'center', padding: '20px' }}>
            <ExperimentOutlined style={{ fontSize: '48px', color: '#1890ff' }} />
            <p>Structure visualization would be displayed here</p>
          </div>
        </Card>
      </div>
    );
  };

  return (
    <div>
      <Title level={2}>Chemical Database</Title>
      <Paragraph>
        Search for chemical compounds and view their properties, safety information, and molecular structures.
      </Paragraph>

      <Card title="Chemical Search" style={{ marginBottom: 24 }}>
        <Space>
          <Search
            placeholder="Enter chemical name or formula (e.g., glucose, C6H12O6)"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onPressEnter={handleSearch}
            style={{ width: 400 }}
          />
          <Button
            type="primary"
            icon={<SearchOutlined />}
            onClick={handleSearch}
            loading={loading}
          >
            Search
          </Button>
        </Space>
      </Card>

      {renderChemicalInfo()}
    </div>
  );
};

export default Chemical; 