import React from 'react'
import { Row, Col, Card, Statistic, Typography, Space, Button } from 'antd'
import {
  FileTextOutlined,
  SearchOutlined,
  ExperimentOutlined,
  UploadOutlined,
  RocketOutlined,
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'

const { Title, Paragraph } = Typography

const Dashboard = () => {
  const navigate = useNavigate()

  const quickActions = [
    {
      title: '生成研究提案',
      icon: <FileTextOutlined />,
      description: '基於研究目標生成詳細的研究提案',
      path: '/proposal',
      color: '#1890ff',
    },
    {
      title: '搜尋文獻',
      icon: <SearchOutlined />,
      description: '搜尋並下載相關研究文獻',
      path: '/search',
      color: '#52c41a',
    },
    {
      title: '查詢化學品',
      icon: <ExperimentOutlined />,
      description: '查詢化學品信息和安全數據',
      path: '/chemical',
      color: '#faad14',
    },
    {
      title: '上傳文件',
      icon: <UploadOutlined />,
      description: '上傳並處理研究文件',
      path: '/upload',
      color: '#722ed1',
    },
  ]

  return (
    <div>
      <Title level={2}>歡迎使用 AI Research Assistant</Title>
      <Paragraph>
        智能研究助理，幫助您更高效地進行科學研究
      </Paragraph>

      <Row gutter={[16, 16]} style={{ marginTop: '24px' }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="已處理文件"
              value={42}
              prefix={<FileTextOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="下載文獻"
              value={156}
              prefix={<SearchOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="查詢化學品"
              value={89}
              prefix={<ExperimentOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="生成提案"
              value={23}
              prefix={<RocketOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Title level={3} style={{ marginTop: '32px', marginBottom: '16px' }}>
        快速操作
      </Title>

      <Row gutter={[16, 16]}>
        {quickActions.map((action, index) => (
          <Col xs={24} sm={12} lg={6} key={index}>
            <Card
              hoverable
              className="custom-card"
              onClick={() => navigate(action.path)}
              style={{ cursor: 'pointer' }}
            >
              <Space direction="vertical" style={{ width: '100%' }}>
                <div
                  style={{
                    fontSize: '32px',
                    color: action.color,
                    textAlign: 'center',
                  }}
                >
                  {action.icon}
                </div>
                <Title level={4} style={{ margin: 0, textAlign: 'center' }}>
                  {action.title}
                </Title>
                <Paragraph
                  style={{
                    margin: 0,
                    textAlign: 'center',
                    color: '#666',
                  }}
                >
                  {action.description}
                </Paragraph>
                <Button
                  type="primary"
                  style={{
                    background: action.color,
                    borderColor: action.color,
                    width: '100%',
                  }}
                >
                  開始使用
                </Button>
              </Space>
            </Card>
          </Col>
        ))}
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: '32px' }}>
        <Col xs={24} lg={12}>
          <Card title="最近活動" className="custom-card">
            <Paragraph>
              • 生成了新的研究提案：有機合成方法優化
            </Paragraph>
            <Paragraph>
              • 下載了 5 篇相關文獻
            </Paragraph>
            <Paragraph>
              • 查詢了 3 個化學品的安全信息
            </Paragraph>
            <Paragraph>
              • 上傳並處理了實驗數據文件
            </Paragraph>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="系統狀態" className="custom-card">
            <Paragraph>
              ✅ AI 服務正常運行
            </Paragraph>
            <Paragraph>
              ✅ 文獻搜尋服務可用
            </Paragraph>
            <Paragraph>
              ✅ 化學品數據庫連接正常
            </Paragraph>
            <Paragraph>
              ✅ 文件處理服務正常
            </Paragraph>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Dashboard 