import React, { useState, useEffect } from 'react'
import { Card, Form, Select, Button, message, Space, Typography, Divider, Slider, InputNumber, Row, Col, Alert } from 'antd'
import { SettingOutlined, SaveOutlined, InfoCircleOutlined, ReloadOutlined } from '@ant-design/icons'

const { Title, Text } = Typography
const { Option } = Select

const Settings = () => {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [currentModel, setCurrentModel] = useState('')
  const [selectedModel, setSelectedModel] = useState('') // 新增：追蹤當前選擇的模型
  const [llmParams, setLlmParams] = useState({
    temperature: 0.3,
    max_tokens: 4000,
    timeout: 120,
    reasoning_effort: 'medium',
    verbosity: 'medium'
  })
  const [supportedParams, setSupportedParams] = useState({})
  const [modelParamsInfo, setModelParamsInfo] = useState({})

  // 可用的LLM模型選項
  const modelOptions = [
    {
      value: 'gpt-5',
      label: 'GPT-5',
      description: '最新的GPT-5模型，功能最強大，支援推理控制和工具鏈'
    },
    {
      value: 'gpt-5-nano',
      label: 'GPT-5 Nano',
      description: 'GPT-5的輕量版本，速度最快，適合簡單格式化任務'
    },
    {
      value: 'gpt-5-mini',
      label: 'GPT-5 Mini',
      description: 'GPT-5的平衡版本，速度與功能兼具，支援推理控制'
    },
    {
      value: 'gpt-4-1106-preview',
      label: 'GPT-4 Turbo Preview (1106)',
      description: '穩定可靠的GPT-4模型，使用傳統API介面'
    }
  ]

  // 載入當前設定
  useEffect(() => {
    loadCurrentSettings()
  }, [])

  // 當選擇的模型改變時重新載入參數資訊
  useEffect(() => {
    if (selectedModel) {
      loadModelParametersInfo(selectedModel)
    }
  }, [selectedModel])

  const loadCurrentSettings = async () => {
    try {
      setLoading(true)
      
      // 載入模型設定
      const modelResponse = await fetch('/api/v1/settings/model', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      
      // 載入LLM參數設定
      const paramsResponse = await fetch('/api/v1/settings/llm-parameters', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      
      if (modelResponse.ok && paramsResponse.ok) {
        const modelData = await modelResponse.json()
        const paramsData = await paramsResponse.json()
        
        setCurrentModel(modelData.current_model)
        setSelectedModel(modelData.current_model) // 初始化選擇的模型
        setLlmParams(paramsData)
        
        form.setFieldsValue({
          llm_model: modelData.current_model,
          ...paramsData
        })
      } else {
        message.error('載入設定失敗')
      }
    } catch (error) {
      console.error('載入設定錯誤:', error)
      message.error('載入設定時發生錯誤')
    } finally {
      setLoading(false)
    }
  }

  const loadModelParametersInfo = async (modelName) => {
    try {
      const response = await fetch(`/api/v1/settings/model-parameters-info?model_name=${modelName}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      
      if (response.ok) {
        const data = await response.json()
        setSupportedParams(data.supported_parameters)
        setModelParamsInfo(data)
        
        // 更新表單的初始值以反映新模型的參數
        // 但保留用戶已修改但尚未保存的設定
        const currentFormValues = form.getFieldsValue()
        const newFormValues = {
          ...data.current_parameters,
          llm_model: currentFormValues.llm_model || selectedModel
        }
        form.setFieldsValue(newFormValues)
      }
    } catch (error) {
      console.error('載入模型參數資訊錯誤:', error)
    }
  }

  // 處理模型選擇變更
  const handleModelChange = (value) => {
    setSelectedModel(value)
    console.log('模型選擇變更為:', value)
  }

  // 儲存所有設定（模型 + 參數）
  const handleSaveAllSettings = async (values) => {
    try {
      setLoading(true)
      
      // 1. 儲存模型設定
      const modelResponse = await fetch('/api/v1/settings/model', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          llm_model: values.llm_model
        }),
      })
      
      if (!modelResponse.ok) {
        const errorData = await modelResponse.json()
        message.error(errorData.detail || '儲存模型設定失敗')
        return
      }
      
      // 2. 儲存LLM參數設定
      const paramsToSend = {}
      Object.keys(supportedParams).forEach(key => {
        if (values[key] !== undefined) {
          paramsToSend[key] = values[key]
        }
      })
      
      const paramsResponse = await fetch('/api/v1/settings/llm-parameters', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(paramsToSend),
      })
      
      if (paramsResponse.ok) {
        message.success('所有設定已成功儲存')
        setCurrentModel(values.llm_model)
        
        // 重新載入設定以確保同步
        await loadCurrentSettings()
      } else {
        const errorData = await paramsResponse.json()
        message.error(errorData.detail || '儲存LLM參數失敗')
      }
    } catch (error) {
      console.error('儲存設定錯誤:', error)
      message.error('儲存設定時發生錯誤')
    } finally {
      setLoading(false)
    }
  }

  // 重置為預設設定
  const handleResetToDefault = async () => {
    try {
      setLoading(true)
      
      // 設定預設值：gpt-4-1106-preview 與低溫設定
      const defaultSettings = {
        llm_model: 'gpt-4-1106-preview',
        temperature: 0.2,
        max_tokens: 4000,
        timeout: 120,
        reasoning_effort: 'medium',
        verbosity: 'medium'
      }
      
      // 1. 儲存模型設定
      const modelResponse = await fetch('/api/v1/settings/model', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          llm_model: defaultSettings.llm_model
        }),
      })
      
      if (!modelResponse.ok) {
        message.error('重置模型設定失敗')
        return
      }
      
      // 2. 儲存參數設定
      const paramsResponse = await fetch('/api/v1/settings/llm-parameters', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          temperature: defaultSettings.temperature,
          max_tokens: defaultSettings.max_tokens,
          timeout: defaultSettings.timeout,
          reasoning_effort: defaultSettings.reasoning_effort,
          verbosity: defaultSettings.verbosity
        }),
      })
      
      if (paramsResponse.ok) {
        message.success('已重置為預設設定 (GPT-4-1106-preview, 低溫 0.2)')
        
        // 更新本地狀態
        setCurrentModel(defaultSettings.llm_model)
        setSelectedModel(defaultSettings.llm_model)
        setLlmParams({
          temperature: defaultSettings.temperature,
          max_tokens: defaultSettings.max_tokens,
          timeout: defaultSettings.timeout,
          reasoning_effort: defaultSettings.reasoning_effort,
          verbosity: defaultSettings.verbosity
        })
        
        // 更新表單
        form.setFieldsValue({
          llm_model: defaultSettings.llm_model,
          temperature: defaultSettings.temperature,
          max_tokens: defaultSettings.max_tokens,
          timeout: defaultSettings.timeout,
          reasoning_effort: defaultSettings.reasoning_effort,
          verbosity: defaultSettings.verbosity
        })
        
        // 重新載入參數資訊
        await loadModelParametersInfo(defaultSettings.llm_model)
      } else {
        message.error('重置參數設定失敗')
      }
    } catch (error) {
      console.error('重置設定錯誤:', error)
      message.error('重置設定時發生錯誤')
    } finally {
      setLoading(false)
    }
  }

  // 渲染參數控制項
  const renderParameterControl = (paramName, paramConfig) => {
    const currentValue = llmParams[paramName] || paramConfig.default

    switch (paramConfig.type) {
      case 'float':
        return (
          <Slider
            min={paramConfig.range[0]}
            max={paramConfig.range[1]}
            step={0.1}
            marks={{
              [paramConfig.range[0]]: paramConfig.range[0].toString(),
              [(paramConfig.range[0] + paramConfig.range[1]) / 2]: ((paramConfig.range[0] + paramConfig.range[1]) / 2).toFixed(1),
              [paramConfig.range[1]]: paramConfig.range[1].toString()
            }}
            tooltip={{
              formatter: (value) => `${value}`,
            }}
          />
        )
      
      case 'int':
        return (
          <InputNumber
            min={paramConfig.range[0]}
            max={paramConfig.range[1]}
            style={{ width: '100%' }}
            placeholder={`設定${paramName}`}
          />
        )
      
      case 'select':
        return (
          <Select
            placeholder={`選擇${paramName}`}
            style={{ width: '100%' }}
          >
            {paramConfig.options.map(option => (
              <Option key={option} value={option}>
                {option}
              </Option>
            ))}
          </Select>
        )
      
      default:
        return null
    }
  }

  // 渲染參數說明
  const renderParameterDescription = (paramName, paramConfig) => {
    const descriptions = {
      temperature: {
        low: "低值 (0.0-0.3): 回應更確定、一致",
        medium: "中值 (0.3-0.7): 平衡創造性和一致性", 
        high: "高值 (0.7-2.0): 回應更創造性、多樣化"
      },
      max_tokens: {
        low: "較小值: 回應更簡潔，成本更低",
        medium: "較大值: 回應更詳細，但成本更高",
        suggestion: "建議: 根據需求調整，一般2000-8000較合適"
      },
      timeout: {
        low: "較小值: 響應更快，但可能超時",
        medium: "較大值: 更穩定，但等待時間長",
        suggestion: "建議: 一般60-180秒較合適"
      },
      reasoning_effort: {
        minimal: "minimal: 最低推理成本，適合簡單任務",
        low: "low: 較低推理成本，適合一般任務",
        medium: "medium: 平衡推理能力和成本",
        high: "high: 最高推理能力，適合複雜任務"
      },
      verbosity: {
        low: "low: 簡潔輸出，適合快速回應",
        medium: "medium: 平衡詳盡度",
        high: "high: 詳細輸出，適合需要解釋的任務"
      }
    }

    const desc = descriptions[paramName]
    if (!desc) return null

    return (
      <div style={{ 
        background: '#f6f8fa', 
        padding: '12px', 
        borderRadius: '6px',
        fontSize: '12px',
        lineHeight: '1.4'
      }}>
        {Object.entries(desc).map(([key, text]) => (
          <div key={key}>
            <Text strong>{text.split(':')[0]}:</Text> {text.split(':')[1]}
          </div>
        ))}
      </div>
    )
  }

  return (
    <div style={{ maxWidth: 1000, margin: '0 auto' }}>
      <Title level={2}>
        <SettingOutlined style={{ marginRight: 8 }} />
        系統設定
      </Title>
      
      {/* 語言模型設定 */}
      <Card style={{ marginBottom: 16 }}>
        <Title level={4}>語言模型設定</Title>
        <Text type="secondary">
          選擇用於整個系統的語言模型。不同的模型在性能和成本上有所差異。
        </Text>
        
        <Divider />
        
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSaveAllSettings}
          initialValues={{
            llm_model: currentModel
          }}
        >
          <Form.Item
            label="LLM 模型"
            name="llm_model"
            rules={[
              {
                required: true,
                message: '請選擇一個語言模型',
              },
            ]}
          >
            <Select
              placeholder="選擇語言模型"
              style={{ width: '100%' }}
              loading={loading}
              optionLabelProp="label"
              onChange={handleModelChange} // 新增：處理模型選擇變更
            >
              {modelOptions.map((option) => (
                <Option 
                  key={option.value} 
                  value={option.value}
                  label={option.label}
                >
                  <div style={{ padding: '4px 0' }}>
                    <div style={{ 
                      fontWeight: 'bold', 
                      fontSize: '14px',
                      lineHeight: '1.4',
                      marginBottom: '4px'
                    }}>
                      {option.label}
                    </div>
                    <div style={{ 
                      fontSize: '12px', 
                      color: '#666',
                      lineHeight: '1.3'
                    }}>
                      {option.description}
                    </div>
                  </div>
                </Option>
              ))}
            </Select>
          </Form.Item>

          {selectedModel && (
            <div style={{ 
              background: '#f6f8fa', 
              padding: '12px', 
              borderRadius: '6px',
              marginBottom: '16px'
            }}>
              <Text strong>目前選擇的模型：</Text> {selectedModel}
              {selectedModel !== currentModel && (
                <div style={{ marginTop: '4px' }}>
                  <Text type="warning">⚠️ 模型已變更，請儲存設定以套用變更</Text>
                </div>
              )}
            </div>
          )}

          <Form.Item>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                loading={loading}
                icon={<SaveOutlined />}
              >
                儲存所有設定
              </Button>
              <Button 
                onClick={handleResetToDefault} 
                disabled={loading}
                icon={<ReloadOutlined />}
              >
                重置為預設 (GPT-4, 低溫)
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>

      {/* LLM參數設定 */}
      {selectedModel && Object.keys(supportedParams).length > 0 && (
        <Card>
          <Title level={4}>LLM 參數設定</Title>
          <Text type="secondary">
            調整語言模型的生成參數，影響回應的創造性、長度和響應時間。
            {selectedModel.startsWith('gpt-5') && (
              <span style={{ color: '#1890ff' }}>
                {' '}GPT-5系列支援額外的推理控制和輸出詳盡度參數。
              </span>
            )}
          </Text>
          
          <Divider />
          
          <Form
            form={form}
            layout="vertical"
            onFinish={handleSaveAllSettings}
          >
            {Object.entries(supportedParams).map(([paramName, paramConfig]) => (
              <Row gutter={24} key={paramName} style={{ marginBottom: 24 }}>
                <Col span={12}>
                  <Form.Item
                    label={
                      <Space>
                        <Text>{paramName.charAt(0).toUpperCase() + paramName.slice(1)}</Text>
                        {paramConfig.type === 'float' && (
                          <Text type="secondary" style={{ fontSize: '12px' }}>
                            ({paramConfig.range[0]} - {paramConfig.range[1]})
                          </Text>
                        )}
                        {paramConfig.type === 'int' && (
                          <Text type="secondary" style={{ fontSize: '12px' }}>
                            ({paramConfig.range[0]} - {paramConfig.range[1]})
                          </Text>
                        )}
                        {paramConfig.type === 'select' && (
                          <Text type="secondary" style={{ fontSize: '12px' }}>
                            ({paramConfig.options.join(', ')})
                          </Text>
                        )}
                      </Space>
                    }
                    name={paramName}
                    rules={[
                      {
                        required: true,
                        message: `請設定${paramName}值`,
                      },
                    ]}
                  >
                    {renderParameterControl(paramName, paramConfig)}
                  </Form.Item>
                </Col>
                
                <Col span={12}>
                  <Form.Item
                    label={`${paramName.charAt(0).toUpperCase() + paramName.slice(1)} 說明`}
                    style={{ marginBottom: 0 }}
                  >
                    {renderParameterDescription(paramName, paramConfig)}
                  </Form.Item>
                </Col>
              </Row>
            ))}
          </Form>
        </Card>
      )}

      {/* 模型特性說明 */}
      {selectedModel && (
        <Card>
          <Title level={4}>模型特性說明</Title>
          <Alert
            message="模型特性"
            description={
              <div>
                {selectedModel.startsWith('gpt-5') ? (
                  <div>
                    <p><strong>GPT-5系列特性：</strong></p>
                    <ul>
                      <li><strong>推理控制 (reasoning.effort)：</strong> 控制模型的推理密度和成本</li>
                      <li><strong>輸出詳盡度 (verbosity)：</strong> 控制回應的詳細程度</li>
                      <li><strong>工具鏈支援：</strong> 支援function calling和工具使用</li>
                      <li><strong>結構化輸出：</strong> 支援JSON等格式的強制輸出</li>
                    </ul>
                  </div>
                ) : (
                  <div>
                    <p><strong>GPT-4系列特性：</strong></p>
                    <ul>
                      <li><strong>穩定可靠：</strong> 使用成熟的API介面</li>
                      <li><strong>廣泛支援：</strong> 支援大多數標準參數</li>
                      <li><strong>成本效益：</strong> 相比GPT-5系列成本較低</li>
                    </ul>
                  </div>
                )}
              </div>
            }
            type="info"
            showIcon
            icon={<InfoCircleOutlined />}
          />
        </Card>
      )}
    </div>
  )
}

export default Settings 