import React, { useMemo, useState } from 'react'
import { Typography, Row, Col, Card, Form, Select, DatePicker, Button, Table, Space, Tag, Divider, message } from 'antd'
import { DatabaseOutlined, LineChartOutlined, DownloadOutlined } from '@ant-design/icons'

const { Title, Paragraph, Text } = Typography
const { RangePicker } = DatePicker

const metricCards = [
  {
    key: 'datasets',
    title: 'Active Datasets',
    value: 12,
    icon: <DatabaseOutlined />,
    description: 'Dynamic collections synced from experiments and uploads.'
  },
  {
    key: 'trends',
    title: 'Detected Trends',
    value: 47,
    icon: <LineChartOutlined />,
    description: 'Signals with statistically significant variations.'
  },
  {
    key: 'exports',
    title: 'Exports This Week',
    value: 8,
    icon: <DownloadOutlined />,
    description: 'Reports generated and downloaded by the research team.'
  }
]

const datasetOptions = [
  { label: 'Experiment Results', value: 'experiment_results' },
  { label: 'Sensor Streams', value: 'sensor_streams' },
  { label: 'Literature Insights', value: 'literature_insights' }
]

const columns = [
  {
    title: 'Feature',
    dataIndex: 'feature',
    key: 'feature'
  },
  {
    title: 'Signal Strength',
    dataIndex: 'signal',
    key: 'signal',
    render: (value) => <Tag color={value > 0.75 ? 'red' : value > 0.45 ? 'orange' : 'blue'}>{value.toFixed(2)}</Tag>
  },
  {
    title: 'Last Updated',
    dataIndex: 'updatedAt',
    key: 'updatedAt'
  },
  {
    title: 'Recommended Action',
    dataIndex: 'action',
    key: 'action'
  }
]

const mockData = {
  experiment_results: [
    { key: '1', feature: 'Catalyst Efficiency', signal: 0.82, updatedAt: '2025-09-15 10:20', action: 'Schedule deeper experiment review.' },
    { key: '2', feature: 'Yield Consistency', signal: 0.63, updatedAt: '2025-09-14 16:05', action: 'Monitor next batch closely.' },
    { key: '3', feature: 'Thermal Stability', signal: 0.34, updatedAt: '2025-09-13 09:12', action: 'No action required.' }
  ],
  sensor_streams: [
    { key: '1', feature: 'Ambient Humidity', signal: 0.58, updatedAt: '2025-09-15 07:44', action: 'Correlate with material deviation logs.' },
    { key: '2', feature: 'Reactive Emissions', signal: 0.77, updatedAt: '2025-09-14 21:18', action: 'Escalate to safety officer.' },
    { key: '3', feature: 'Equipment Vibration', signal: 0.49, updatedAt: '2025-09-14 18:56', action: 'Flag for maintenance diagnostics.' }
  ],
  literature_insights: [
    { key: '1', feature: 'Emerging Catalysts', signal: 0.71, updatedAt: '2025-09-10 13:34', action: 'Prioritise for proposal drafting.' },
    { key: '2', feature: 'Safety Regulations', signal: 0.28, updatedAt: '2025-09-08 08:22', action: 'Archive for compliance reference.' },
    { key: '3', feature: 'Process Innovations', signal: 0.66, updatedAt: '2025-09-11 11:05', action: 'Share digest with wider team.' }
  ]
}

const DataAnalyzer = () => {
  const [selectedDataset, setSelectedDataset] = useState('experiment_results')
  const [selectedRange, setSelectedRange] = useState(null)

  const tableData = useMemo(() => mockData[selectedDataset] || [], [selectedDataset])

  const handleAnalyze = () => {
    message.success('Analysis request queued. You will receive a notification when it is ready.')
  }

  const handleExport = () => {
    message.info('Export preparation started. Download will begin automatically when complete.')
  }

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <div>
        <Title level={2}>Data Analyzer</Title>
        <Paragraph>
          Explore consolidated datasets, surface actionable signals, and orchestrate exports for your research workflow.
        </Paragraph>
      </div>

      <Row gutter={[16, 16]}>
        {metricCards.map((card) => (
          <Col key={card.key} xs={24} sm={12} lg={8}>
            <Card>
              <Space direction="vertical" size="middle">
                <Space size="middle" align="center">
                  {card.icon}
                  <div>
                    <Text strong>{card.title}</Text>
                    <Paragraph type="secondary" style={{ marginBottom: 0 }}>
                      {card.description}
                    </Paragraph>
                  </div>
                </Space>
                <Title level={3} style={{ margin: 0 }}>
                  {card.value}
                </Title>
              </Space>
            </Card>
          </Col>
        ))}
      </Row>

      <Card title="Analysis Controls" bordered>
        <Form layout="vertical">
          <Row gutter={16}>
            <Col xs={24} md={8}>
              <Form.Item label="Dataset" required>
                <Select
                  options={datasetOptions}
                  value={selectedDataset}
                  onChange={setSelectedDataset}
                />
              </Form.Item>
            </Col>
            <Col xs={24} md={10}>
              <Form.Item label="Time Range">
                <RangePicker
                  style={{ width: '100%' }}
                  value={selectedRange}
                  onChange={setSelectedRange}
                  allowEmpty={[true, true]}
                  showTime
                />
              </Form.Item>
            </Col>
            <Col xs={24} md={6}>
              <Form.Item label="Actions">
                <Space>
                  <Button type="primary" onClick={handleAnalyze}>
                    Run Analysis
                  </Button>
                  <Button onClick={handleExport}>
                    Export Report
                  </Button>
                </Space>
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Card>

      <Card title="Signal Overview" bordered>
        <Table
          columns={columns}
          dataSource={tableData}
          pagination={{ pageSize: 5 }}
        />
      </Card>

      <Divider plain>Analysis Notes</Divider>
      <Paragraph type="secondary">
        The Data Analyzer provides a consolidated view of signals surfaced by background jobs. Refine parameters to
        focus on the metrics that matter most and coordinate actions with your team in real time.
      </Paragraph>
    </Space>
  )
}

export default DataAnalyzer
