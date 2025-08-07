# AI 研究助理系統學習指南
## Learning Guide

### 🎯 學習目標

通過這個學習指南，您將能夠：
1. 理解整個AI研究助理系統的架構設計
2. 掌握各個模塊的功能和實現原理
3. 學會如何擴展和維護系統
4. 了解現代AI應用的開發模式

### 📚 學習路徑

#### 第一階段：系統概覽
1. **閱讀架構文檔** (`ARCHITECTURE_OVERVIEW.md`)
   - 了解整體架構設計
   - 理解各層之間的關係
   - 掌握數據流向

2. **運行主程序** (`main.py`)
   ```bash
   python main.py
   ```
   - 觀察啟動過程
   - 理解錯誤處理機制
   - 學習命令行參數處理

#### 第二階段：核心模塊學習

##### 1. 配置管理 (`config.py`)
**學習重點：**
- 環境變量管理
- 路徑配置設計
- 配置驗證機制

**關鍵概念：**
```python
# 環境變量載入
load_dotenv()

# 路徑配置
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# 配置驗證
def validate_config():
    # 檢查API密鑰和目錄
```

##### 2. 查詢解析 (`query_parser.py`)
**學習重點：**
- GPT模型集成
- 關鍵詞提取算法
- 多語言處理

**關鍵概念：**
```python
# GPT模型調用
response = client.chat.completions.create(
    model=LLM_MODEL_NAME,
    messages=[{"role": "user", "content": prompt}],
    temperature=0.2,
)

# 結果解析
keywords = ast.literal_eval(match.group(0))
```

##### 3. 搜索代理 (`search_agent.py`)
**學習重點：**
- 多源搜索協調
- 錯誤處理策略
- 結果整合機制

**關鍵概念：**
```python
# 關鍵詞提取
keywords = extract_keywords(user_input)

# 多源搜索
results = search_source(keywords, limit=top_k)

# 文件下載
filepath = download_and_store(result, storage_dir)
```

##### 4. 文件處理 (`file_upload.py`)
**學習重點：**
- 文件格式驗證
- 元數據提取
- 進度回調機制

**關鍵概念：**
```python
# 文件格式驗證
valid_exts = [".pdf", ".docx"]

# 元數據提取
metadata = extract_metadata(path)

# 進度回調
if status_callback:
    status_callback(f"正在處理：{filename}")
```

#### 第三階段：高級功能學習

##### 1. 知識處理層
- **RAG核心** (`rag_core.py`): 檢索增強生成
- **文檔嵌入** (`chunk_embedding.py`): 向量化處理
- **語義查找** (`semantic_lookup.py`): 語義搜索

##### 2. 數據管理層
- **元數據註冊** (`metadata_registry.py`): 數據管理
- **實驗註冊** (`metadata_experiment_registry.py`): 實驗數據
- **查詢解析** (`query_parser.py`): 查詢處理

##### 3. 搜索層
- **Europe PMC** (`europepmc_handler.py`): 醫學文獻
- **PubChem** (`pubchem_handler.py`): 化學數據
- **Perplexity** (`perplexity_search_fallback.py`): 備用搜索

### 🔧 實踐練習

#### 練習1：理解配置系統
```python
# 運行配置驗證
python config.py

# 觀察輸出，理解配置檢查過程
```

#### 練習2：測試查詢解析
```python
# 創建測試腳本
from query_parser import extract_keywords

# 測試不同語言的查詢
queries = [
    "如何進行二氧化碳捕獲？",
    "machine learning in chemistry",
    "MOF材料合成方法"
]

for query in queries:
    keywords = extract_keywords(query)
    print(f"查詢：{query}")
    print(f"關鍵詞：{keywords}\n")
```

#### 練習3：文件處理流程
```python
# 測試文件上傳處理
from file_upload import process_uploaded_files

# 準備測試文件
test_files = ["test_paper.pdf", "test_document.docx"]

# 處理文件
results = process_uploaded_files(test_files)
print(f"處理了 {len(results)} 個文件")
```

### 🎓 學習技巧

#### 1. 代碼閱讀技巧
- **從入口開始**：先看 `main.py`，理解程序啟動流程
- **按層次學習**：從配置層到應用層，逐層深入
- **關注註解**：每個函數都有詳細的中文註解
- **理解數據流**：追蹤數據在各模塊間的流動

#### 2. 調試技巧
```python
# 添加調試輸出
print(f"🔍 調試信息：{variable}")

# 使用斷點
import pdb; pdb.set_trace()

# 檢查變量類型
print(f"類型：{type(variable)}")
```

#### 3. 擴展開發技巧
- **模塊化設計**：新功能應該作為獨立模塊
- **配置驅動**：使用配置文件管理參數
- **錯誤處理**：每個函數都要有完善的異常處理
- **文檔化**：為新功能添加詳細註解

### 🚀 進階學習

#### 1. 架構設計模式
- **分層架構**：UI層、業務層、數據層分離
- **依賴注入**：通過配置文件管理依賴
- **觀察者模式**：使用回調函數通知狀態變化
- **策略模式**：支持多種搜索源和處理方式

#### 2. AI集成模式
- **API調用**：安全地調用外部AI服務
- **提示工程**：設計有效的提示詞
- **結果解析**：處理AI模型的輸出
- **錯誤恢復**：處理API調用失敗

#### 3. 數據處理模式
- **ETL流程**：提取、轉換、加載
- **元數據管理**：統一管理文件信息
- **向量化處理**：將文本轉換為向量
- **語義搜索**：基於內容相似度搜索

### 📖 推薦學習資源

#### 1. Python相關
- **類型提示**：`typing` 模塊的使用
- **異常處理**：`try-except` 最佳實踐
- **路徑處理**：`os.path` 和 `pathlib`
- **環境變量**：`python-dotenv` 的使用

#### 2. AI/ML相關
- **OpenAI API**：GPT模型調用
- **向量嵌入**：文本向量化技術
- **RAG架構**：檢索增強生成
- **提示工程**：有效的提示詞設計

#### 3. Web開發相關
- **Streamlit**：快速Web應用開發
- **文件上傳**：多文件處理
- **進度顯示**：用戶體驗優化
- **錯誤處理**：用戶友好的錯誤信息

### 🎯 學習檢查清單

- [ ] 理解整體架構設計
- [ ] 掌握配置管理機制
- [ ] 學會查詢解析流程
- [ ] 理解搜索代理功能
- [ ] 掌握文件處理流程
- [ ] 了解知識處理層
- [ ] 學會數據管理方式
- [ ] 掌握錯誤處理策略
- [ ] 理解模塊間通信
- [ ] 學會擴展新功能

### 💡 學習建議

1. **循序漸進**：按照學習路徑逐步深入
2. **動手實踐**：每個概念都要動手測試
3. **理解原理**：不僅要知道怎麼做，還要理解為什麼
4. **記錄筆記**：記錄學習過程中的疑問和發現
5. **嘗試修改**：嘗試修改代碼，觀察變化
6. **尋求幫助**：遇到問題時查看註解或詢問

### 🔄 持續學習

這個系統是一個很好的學習平台，您可以：
- 添加新的搜索源
- 改進UI界面
- 優化AI模型調用
- 擴展文件格式支持
- 添加新的分析功能

記住：**最好的學習方式是動手實踐！** 🚀 