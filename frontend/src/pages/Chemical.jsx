import React, { useState } from 'react';
import { Card, Input, Button, Table, Typography, Space, message, Tag, Image, List } from 'antd';
import { SearchOutlined, ExperimentOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Title, Paragraph } = Typography;
const { Search } = Input;

const API_URL = 'http://localhost:8000/api/v1';

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
    setChemicalData(null);
    try {
      const response = await axios.post(`${API_URL}/chemical/search`, {
        chemical_name: searchQuery,
      });

      if (response.data && !response.data.error) {
        const data = response.data;
        const formattedData = {
          name: data.name,
          formula: data.formula,
          molecularWeight: data.molecular_weight,
          casNumber: data.cas_number,
          properties: {
            meltingPoint: data.melting_point,
            boilingPoint: data.boiling_point,
            density: data.properties?.density,
            solubility: data.properties?.solubility,
          },
          structure_url: data.image_url,
          safety: {
            hazards: data.hazard_statements || [],
            precautions: data.precautionary_statements || [],
            ghs_icons: data.safety_data?.ghs_icons || [],
          }
        };
        setChemicalData(formattedData);
        message.success('Chemical information found');
      } else {
        message.error(response.data.error || 'Failed to find chemical information');
      }
    } catch (error) {
      message.error('An error occurred while fetching chemical data.');
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
    ].filter(item => item.value);

    return (
      <div>
        <Card
          title="Chemical Properties"
          style={{ marginBottom: 16 }}
        >
          <Table
            columns={columns}
            dataSource={propertiesData}
            pagination={false}
            size="small"
          />
        </Card>

        <Card
          title="Safety Information"
          style={{ marginBottom: 16 }}
        >
          <Space direction="vertical" style={{ width: '100%' }}>
            <div>
              <strong>GHS Icons:</strong>
              <Space style={{ marginLeft: 8 }}>
                {chemicalData.safety.ghs_icons.map((icon, index) => (
                  <Image key={index} src={icon} width={40} preview={false} />
                ))}
              </Space>
            </div>
            <div>
              <strong>Hazard Statements:</strong>
              <List
                size="small"
                dataSource={chemicalData.safety.hazards}
                renderItem={(item) => <List.Item>{item}</List.Item>}
              />
            </div>
            <div>
              <strong>Precautionary Statements:</strong>
              <List
                size="small"
                dataSource={chemicalData.safety.precautions}
                renderItem={(item) => <List.Item>{item}</List.Item>}
              />
            </div>
          </Space>
        </Card>

        <Card title="Molecular Structure">
          <div style={{ textAlign: 'center', padding: '20px' }}>
            {chemicalData.structure_url ? (
              <Image src={chemicalData.structure_url} width={200} />
            ) : (
              <>
                <ExperimentOutlined style={{ fontSize: '48px', color: '#1890ff' }} />
                <p>Structure image not available</p>
              </>
            )}
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