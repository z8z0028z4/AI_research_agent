# Fallback 移除日誌

## 移除的 Fallback 機制

### 1. 模型配置 Fallback
**位置**: 多個函數中的 `except Exception as e:` 區塊
**移除內容**:
```python
# 使用fallback配置
llm_params = {
    "model": "gpt-4-1106-preview",
    "temperature": 0.3,  # 或 0.0 (結構化輸出)
    "max_tokens": 4000,
    "timeout": 120,
}
```

### 2. API 格式 Fallback
**位置**: `call_llm()` 函數 (第680-685行)
**移除內容**:
```python
else:
    # GPT-4系列使用Chat Completions API (LangChain)
    llm = ChatOpenAI(**llm_params)
    response = llm.invoke(prompt)
    return response.content
```

### 3. Function Calling Fallback
**位置**: 多個結構化函數中的 `else:` 分支
**移除內容**:
```python
else:
    # GPT-4系列使用Chat Completions API with function calling
    response = client.chat.completions.create(
        model=current_model,
        messages=[...],
        functions=[{
            "name": "create_research_proposal",
            "parameters": current_schema
        }],
        function_call={"name": "create_research_proposal"}
    )
```

### 4. 查詢擴展 Fallback
**位置**: `expand_query()` 函數 (第1672-1688行)
**移除內容**:
```python
else:
    # GPT-4系列使用Chat Completions API (LangChain)
    llm = ChatOpenAI(**llm_params)
    output = llm.predict(full_prompt).strip()

# 最後的 fallback
except Exception as e:
    print(f"❌ 查詢擴展失敗：{e}")
    # 返回原始查詢作為fallback
    return [user_prompt]
```

### 5. 結構化輸出 Fallback
**位置**: `generate_proposal_with_fallback()` 函數 (第2042-2139行)
**移除內容**: 整個函數，包括文本格式回退邏輯

### 6. 輸出解析 Fallback
**位置**: 多個函數中的輸出提取邏輯
**移除內容**: 複雜的 output 陣列解析邏輯

### 7. JSON 解析 Fallback
**位置**: 查詢擴展函數 (第1683-1688行)
**移除內容**: eval() 和文本解析 fallback

## 移除日期
2024年12月

## 移除原因
- 簡化代碼結構
- 只支援 GPT-5 模型
- 只使用 Responses API
- 只保留結構化輸出
- 提高可維護性
