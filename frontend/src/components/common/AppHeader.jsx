import React from 'react'
import { Layout, Typography, Space, Button, Avatar } from 'antd'
import { ExperimentOutlined, UserOutlined } from '@ant-design/icons'

const { Header } = Layout
const { Title } = Typography

const AppHeader = () => {
  return (
    <Header
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: '0 24px',
        height: '64px',
        lineHeight: '64px',
      }}
    >
      <Space>
        <ExperimentOutlined style={{ fontSize: '24px', color: 'white' }} />
        <Title level={3} style={{ color: 'white', margin: 0 }}>
          AI Research Assistant
        </Title>
      </Space>
      
      <Space>
        <Button type="text" style={{ color: 'white' }}>
          <UserOutlined />
          用戶中心
        </Button>
        <Avatar icon={<UserOutlined />} />
      </Space>
    </Header>
  )
}

export default AppHeader 