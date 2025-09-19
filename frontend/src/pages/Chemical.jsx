import React, { useState, useEffect } from 'react';
import { Card, Input, Button, Table, Typography, Space, message, Tag, List, Switch, Row, Col, Statistic, Spin, Image, Divider, Collapse } from 'antd';
import { SearchOutlined, ExperimentOutlined, DatabaseOutlined, SaveOutlined, EyeOutlined } from '@ant-design/icons';
import SmilesDrawer from '../components/SmilesDrawer';

const { Title, Paragraph, Text } = Typography;
const { Search } = Input;

const Chemical = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [chemicalData, setChemicalData] = useState(null);
  const [databaseStats, setDatabaseStats] = useState(null);
  // 移除不需要的狀態變量
  const [databaseChemicals, setDatabaseChemicals] = useState([]);
  const [showDatabase, setShowDatabase] = useState(false);
  const [databaseSearchQuery, setDatabaseSearchQuery] = useState('');
  const [filteredDatabaseChemicals, setFilteredDatabaseChemicals] = useState([]);

  const API_BASE = '/api/v1';

  // Load database statistics
  const loadDatabaseStats = async () => {
    try {
      const response = await fetch(`${API_BASE}/chemical/database-stats`);
      if (response.ok) {
        const stats = await response.json();
        setDatabaseStats(stats);
      }
    } catch (error) {
      console.error('Failed to load database stats:', error);
    }
  };

  // Load database chemicals
  const loadDatabaseChemicals = async () => {
    try {
      console.log('🔄 [DATABASE-LIST] 開始載入數據庫化學品列表...');
      const response = await fetch(`${API_BASE}/chemical/database-list`);
      if (response.ok) {
        const data = await response.json();
        console.log('🔄 [DATABASE-LIST] 載入完成，化學品數量:', data.chemicals?.length || 0);
        setDatabaseChemicals(data.chemicals || []);
        // 初始化過濾列表
        setFilteredDatabaseChemicals(data.chemicals || []);
      }
    } catch (error) {
      console.error('Failed to load database chemicals:', error);
    }
  };

  // Filter database chemicals based on search query
  const filterDatabaseChemicals = (query) => {
    if (!query.trim()) {
      setFilteredDatabaseChemicals(databaseChemicals);
    } else {
      const filtered = databaseChemicals.filter(chemical => 
        chemical.name.toLowerCase().includes(query.toLowerCase()) ||
        (chemical.formula && chemical.formula.toLowerCase().includes(query.toLowerCase())) ||
        (chemical.cas && chemical.cas.toLowerCase().includes(query.toLowerCase()))
      );
      setFilteredDatabaseChemicals(filtered);
    }
  };

  // Load initial data
  useEffect(() => {
    loadDatabaseStats();
  }, []);

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      message.warning('Please enter a chemical name or formula');
      return;
    }

    setLoading(true);
    try {
      console.log('Searching for chemical:', searchQuery);
      
      const response = await fetch(`${API_BASE}/chemical/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chemical_name: searchQuery,
          include_safety: true,
          include_properties: true,
          include_structure: true,
          save_to_database: true
        })
      });

      if (!response.ok) {
        throw new Error(await response.text());
      }

      const data = await response.json();
      
      console.log('🔍 [CHEMICAL-SEARCH] API 響應數據:', data);
      console.log('🔍 [CHEMICAL-SEARCH] 是否有 svg_structure:', !!data.svg_structure);
      console.log('🔍 [CHEMICAL-SEARCH] 是否有 png_structure:', !!data.png_structure);
      console.log('🔍 [CHEMICAL-SEARCH] 是否有 safety_data:', !!data.safety_data);
      console.log('🔍 [CHEMICAL-SEARCH] safety_data 內容:', data.safety_data);
      
      if (data.error) {
        message.error(data.error);
        setChemicalData(null);
      } else {
        setChemicalData(data);
        message.success(`Chemical information found${data.saved_to_database ? ' and saved to database' : ''}`);
        
        // Refresh database stats and list if saved
        if (data.saved_to_database) {
          console.log('🔄 [CHEMICAL-SEARCH] 化學品已保存到數據庫，開始刷新...');
          loadDatabaseStats();
          // 如果 Database 視圖已經打開，重新載入列表
          if (showDatabase) {
            console.log('🔄 [CHEMICAL-SEARCH] Database 視圖已打開，重新載入列表...');
            loadDatabaseChemicals();
          } else {
            console.log('🔄 [CHEMICAL-SEARCH] Database 視圖未打開，跳過列表刷新');
          }
        }
      }
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

    return (
      <Collapse
        defaultActiveKey={['chemicals']}
        style={{ marginBottom: 16 }}
        items={[
          {
            key: 'chemicals',
            label: <span style={{ fontWeight: 700, fontSize: 27 }}>🧪 Chemical Information</span>,
            children: (
              <List
                dataSource={[chemicalData]}
                renderItem={(c, index) => {
                  console.log('🔍 [CHEMICAL-DISPLAY] 化學品數據:', c);
                  console.log('🔍 [CHEMICAL-DISPLAY] 是否有 svg_structure:', !!c.svg_structure);
                  console.log('🔍 [CHEMICAL-DISPLAY] 是否有 png_structure:', !!c.png_structure);
                  console.log('🔍 [CHEMICAL-DISPLAY] 是否有 safety_icons:', !!c.safety_icons);
                  console.log('🔍 [CHEMICAL-DISPLAY] safety_icons 內容:', c.safety_icons);
                  
                  return (
                    <List.Item style={{ padding: '16px 0', borderBottom: '1px solid #f0f0f0' }}>
                      <div style={{ width: '100%' }}>
                        <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-start' }}>
                          {/* Structure Image - 優先使用 SMILES 繪製的結構圖 */}
                          <div style={{ flex: '0 0 150px' }}>
                            <SmilesDrawer
                              svgStructure={c.svg_structure}
                              pngStructure={c.png_structure}
                              smiles={c.smiles}
                              name={c.name}
                              width={120}
                              height={120}
                              showSmiles={false}
                              loading={false}
                              error={null}
                            />
                            {/* 調試信息 */}
                            <div style={{ fontSize: '10px', color: '#666', marginTop: '4px' }}>
                              Debug: SVG={!!c.svg_structure}, PNG={!!c.png_structure}, SMILES={c.smiles}
                            </div>
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
                                <div><strong>MW:</strong> <code>{c.weight || c.molecular_weight || '-'}</code></div>
                                <div><strong>Boiling Point:</strong> <code>{c.boiling_point_c || c.boiling_point || '-'}</code></div>
                                <div><strong>Melting Point:</strong> <code>{c.melting_point_c || c.melting_point || '-'}</code></div>
                                <div><strong>CAS No.:</strong> <code>{c.cas || c.cas_number || '-'}</code></div>
                                <div><strong>SMILES:</strong> <code>{c.smiles || '-'}</code></div>
                                {c.cid && <div><strong>PubChem CID:</strong> <code>{c.cid}</code></div>}
                              </div>
                            </div>

                            {/* Safety Icons */}
                            <div style={{ flex: '0 0 150px' }}>
                              <Text strong style={{ fontSize: '14px', marginBottom: '8px', display: 'block' }}>
                                Handling Safety
                              </Text>
                              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                {/* NFPA Diamond */}
                                {(c.safety_icons?.nfpa_image || c.safety_data?.nfpa_image) && (
                                  <img
                                    src={c.safety_icons?.nfpa_image || c.safety_data?.nfpa_image}
                                    alt="NFPA"
                                    style={{ width: '50px', height: '50px' }}
                                  />
                                )}
                                {/* GHS Icons */}
                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', maxWidth: '120px' }}>
                                  {(c.safety_icons?.ghs_icons || c.safety_data?.ghs_icons || []).map((icon, index) => (
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
                  );
                }}
              />
            ),
          },
        ]}
      />
    );
  };

  return (
    <div>
      <Title level={2}>化學品查詢 (Chemical Database)</Title>
      <Paragraph>
        Search for chemical compounds and view their properties, safety information, and molecular structures. 
        Results can be automatically saved to the database for future reference.
      </Paragraph>

      {/* Search Section */}
      <Card title="Chemical Search" style={{ marginBottom: 24 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
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
            <Button 
              icon={<EyeOutlined />}
              onClick={() => {
                setShowDatabase(!showDatabase);
                if (!showDatabase) {
                  loadDatabaseChemicals();
                }
              }}
            >
              {showDatabase ? 'Hide' : 'View'} Database ({databaseStats?.total_chemicals || 0})
            </Button>
          </Space>
          
          {/* 移除不需要的選項 */}
        </Space>
      </Card>

      {/* Chemical Information Display - 移到前面 */}
      {renderChemicalInfo()}

      {/* Database Chemicals List - 移到後面，使用固定高度 */}
      {showDatabase && (
        <Card title="Database Chemicals" style={{ marginBottom: 24 }}>
          {/* 搜尋功能 */}
          <div style={{ marginBottom: 16 }}>
            <Search
              placeholder="搜尋化學品名稱、分子式或 CAS 號碼"
              value={databaseSearchQuery}
              onChange={(e) => {
                setDatabaseSearchQuery(e.target.value);
                filterDatabaseChemicals(e.target.value);
              }}
              onSearch={(value) => filterDatabaseChemicals(value)}
              style={{ width: '100%' }}
            />
          </div>
          
          <Spin spinning={databaseChemicals.length === 0}>
            <div style={{ 
              maxHeight: '400px', 
              overflowY: 'auto',
              border: '1px solid #f0f0f0',
              borderRadius: '6px',
              padding: '8px'
            }}>
              <List
                dataSource={filteredDatabaseChemicals}
                renderItem={(chemical) => (
                <List.Item
                  actions={[
                    <Button 
                      type="link" 
                      onClick={async () => {
                        setSearchQuery(chemical.name);
                        setLoading(true);
                        try {
                          console.log('Auto-searching for chemical:', chemical.name);
                          
                          const response = await fetch(`${API_BASE}/chemical/search`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                              chemical_name: chemical.name,
                              include_safety: true,
                              include_properties: true,
                              include_structure: true,
                              save_to_database: true
                            })
                          });

                          if (!response.ok) {
                            throw new Error(await response.text());
                          }

                          const data = await response.json();
                          
                          console.log('🔍 [CHEMICAL-SEARCH] API 響應數據:', data);
                          console.log('🔍 [CHEMICAL-SEARCH] 是否有 svg_structure:', !!data.svg_structure);
                          console.log('🔍 [CHEMICAL-SEARCH] 是否有 png_structure:', !!data.png_structure);
                          console.log('🔍 [CHEMICAL-SEARCH] 是否有 safety_data:', !!data.safety_data);
                          console.log('🔍 [CHEMICAL-SEARCH] safety_data 內容:', data.safety_data);
                          
                          if (data.error) {
                            message.error(data.error);
                            setChemicalData(null);
                          } else {
                            setChemicalData(data);
                            message.success(`Chemical information found${data.saved_to_database ? ' and saved to database' : ''}`);
                            
                            // Refresh database stats and list if saved
                            if (data.saved_to_database) {
                              loadDatabaseStats();
                              // 如果 Database 視圖已經打開，重新載入列表
                              if (showDatabase) {
                                loadDatabaseChemicals();
                              }
                            }
                          }
                        } catch (error) {
                          message.error('Failed to find chemical information');
                          console.error('Chemical search error:', error);
                        } finally {
                          setLoading(false);
                        }
                      }}
                    >
                      View Details
                    </Button>
                  ]}
                >
                  <List.Item.Meta
                    title={chemical.name}
                    description={`Formula: ${chemical.formula || 'N/A'} | CAS: ${chemical.cas || chemical.cas_number || 'N/A'}`}
                  />
                </List.Item>
              )}
              />
            </div>
          </Spin>
        </Card>
      )}
    </div>
  );
};

export default Chemical; 