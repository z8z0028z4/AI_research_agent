# 知識庫查詢功能 Workflow

## 功能概述

知識庫查詢功能允許用戶基於已上傳的文獻進行智能問答，支持兩種回答模式：
- **嚴謹引用模式**：基於文獻進行準確引用，適合學術研究
- **推論模式**：允許基於文獻進行推論和創新建議，適合創新研究

## 技術架構

### 前端組件
- **KnowledgeQuery.jsx**：主要的查詢界面
- **App.jsx**：路由配置
- **AppSidebar.jsx**：側邊欄菜單

### 後端API
- **knowledge.py**：知識庫查詢API路由
- **rag_core.py**：核心RAG功能

## 完整 Workflow

### 1. 用戶界面交互
```
用戶輸入查詢問題 → 選擇回答模式 → 設定檢索文檔數量 → 點擊查詢
```

### 2. 前端處理
```javascript
// KnowledgeQuery.jsx
const onQuery = async () => {
  const question = form.getFieldValue('question');
  const data = await callApi('/knowledge/query', {
    body: JSON.stringify({ 
      question: question,
      retrieval_count: retrievalCount,
      answer_mode: answerMode  // 'rigorous' 或 'inference'
    }),
  });
  // 處理返回結果
};
```

### 3. 後端API處理
```python
# knowledge.py
@router.post("/query")
async def query_knowledge(request: KnowledgeQueryRequest):
    # 1. 載入向量數據庫
    vectorstore = load_paper_vectorstore()
    
    # 2. 檢索文檔片段（直接使用用戶問題）
    chunks = retrieve_chunks_multi_query(
        vectorstore=vectorstore,
        query_list=[request.question],  # 直接使用用戶問題
        k=request.retrieval_count,
        fetch_k=request.retrieval_count * 2,
        score_threshold=0.35
    )
    
    # 4. 根據回答模式選擇prompt
    if request.answer_mode == "rigorous":
        system_prompt, citations = build_prompt(chunks, request.question)
         elif request.answer_mode == "inference":
         system_prompt, citations = build_inference_prompt(chunks, request.question)
    
    # 5. 調用LLM生成回答
    answer = call_llm(system_prompt)
    
    # 6. 返回結果
    return KnowledgeQueryResponse(
        answer=answer,
        citations=citations,
        chunks=serializable_chunks
    )
```

### 4. 核心RAG功能

#### 4.1 文檔檢索 (retrieve_chunks_multi_query)
```python
# 使用MMR搜索算法檢索相關文檔片段
chunks = retrieve_chunks_multi_query(
    vectorstore=vectorstore,
    query_list=expanded_queries,
    k=retrieval_count,
    fetch_k=retrieval_count * 2,
    score_threshold=0.35
)
```

#### 4.3 Prompt構建

**嚴謹引用模式 (build_prompt)**：
```python
system_prompt = f"""
You are a research literature search assistant. Please answer questions based only on the provided literature excerpts.
Please use [1], [2], etc. to cite paragraph sources in your answers, and do not repeat the sources at the end.
If the paragraphs mention specific experimental conditions (temperature, time, etc.), please be sure to include them in your answer.
Important: You can only cite the provided literature excerpts. The current literature excerpt numbers are [1] to [{len(chunks)}] (total {len(chunks)} excerpts)

--- Literature Summary ---
{context_text}

--- Question ---
{question}
"""
```

**推論模式 (build_inference_prompt)**：
```python
system_prompt = f"""
You are a materials synthesis consultant who understands and excels at comparing the chemical and physical properties of materials. You can propose innovative suggestions based on known experimental conditions for situations where there is no clear literature.

Please conduct extended thinking based on the following literature and experimental data:
- You can propose new combinations, temperatures, times, or pathways.
- Even combinations not yet documented in the literature can be suggested, but you must provide reasonable reasoning.
- When making inferences and extended thinking, please try to mention "what literature clues this idea originates from" to support your explanation. The current literature excerpt numbers are [1] to [{len(chunks)}] (total {len(chunks)} excerpts)

--- Literature Summary ---
{context_text}

--- Question ---
{question}
"""
```

#### 4.4 LLM調用 (call_llm)
```python
# 支持GPT-5 Responses API和GPT-4 Chat Completions API
if current_model.startswith('gpt-5'):
    # 使用Responses API
    response = client.responses.create(**responses_params)
    # 處理incomplete狀態和重試邏輯
else:
    # 使用Chat Completions API
    llm = ChatOpenAI(**llm_params)
    response = llm.invoke(prompt)
```

### 5. 結果展示

前端接收並展示：
- **AI回答**：格式化的文本回答
- **引用文獻**：包含標籤、標題、來源、頁碼、摘要
- **檢索片段**：可折疊的原始文檔片段

## 技術特點

### 1. 雙模式支持
- **嚴謹引用**：適合學術研究，確保每個論點都有文獻支持
- **推論模式**：適合創新研究，允許基於文獻進行推論和建議

### 2. 智能檢索
- **直接查詢**：直接使用用戶問題進行檢索
- **MMR搜索**：最大邊際相關性，避免重複內容
- **相似度閾值**：確保檢索結果的相關性

### 3. 響應式設計
- **文檔數量選擇**：5-30個文檔可選
- **實時狀態顯示**：檢索進度、實際檢索數量等
- **錯誤處理**：完善的錯誤提示和fallback機制

### 4. API兼容性
- **GPT-5支持**：使用Responses API，支持incomplete狀態處理
- **GPT-4支持**：使用Chat Completions API作為fallback
- **重試機制**：自動處理API調用失敗和token不足

## 使用流程

1. **進入知識庫查詢頁面**
   - 點擊側邊欄「知識庫查詢」

2. **輸入查詢問題**
   - 在文本框中輸入研究問題
   - 例如：「請介紹金屬有機骨架材料的合成方法」

3. **選擇回答模式**
   - **嚴謹引用**：基於文獻進行準確引用
   - **推論**：允許基於文獻進行推論和創新建議

4. **設定檢索參數**
   - 選擇檢索文檔數量（5-30個）

5. **執行查詢**
   - 點擊「開始查詢」按鈕
   - 等待AI生成回答

6. **查看結果**
   - 查看AI回答
   - 檢查引用文獻
   - 瀏覽檢索到的文檔片段

## 測試驗證

運行測試文件驗證功能：
```bash
python test_knowledge_query.py
```

測試將驗證：
- 向量數據庫載入
- 查詢擴展功能
- 文檔檢索功能
- Prompt構建功能
- LLM調用功能

## 注意事項

1. **文獻依賴**：功能需要先上傳相關文獻到系統
2. **模型配置**：確保正確配置了OpenAI API Key和模型參數
3. **檢索質量**：檢索結果質量取決於文獻的數量和相關性
4. **API限制**：注意OpenAI API的調用限制和費用 