# AI 研究助理系統架構說明
## Architecture Overview

### 🏗️ 整體架構 (Overall Architecture)

```
AI 研究助理系統
├── 🚀 入口層 (Entry Layer)
│   ├── main.py                    # 主程序入口，啟動器
│   └── research_gui.py            # Streamlit GUI界面
│
├── 🔍 搜索層 (Search Layer)
│   ├── search_agent.py            # 搜索代理
│   ├── perplexity_search_fallback.py  # Perplexity搜索備用
│   ├── europepmc_handler.py      # 歐洲PMC數據庫處理
│   └── pubchem_handler.py        # PubChem化學數據庫處理
│
├── 🧠 知識處理層 (Knowledge Processing Layer)
│   ├── knowledge_agent.py         # 知識代理
│   ├── rag_core.py               # RAG核心功能
│   ├── chunk_embedding.py        # 文檔分塊和嵌入
│   └── semantic_lookup.py        # 語義查找
│
├── 📄 文檔處理層 (Document Processing Layer)
│   ├── file_upload.py            # 文件上傳處理
│   ├── pdf_read_and_chunk_page_get.py  # PDF讀取和分頁
│   ├── document_renamer.py       # 文檔重命名
│   ├── excel_to_txt_by_row.py   # Excel轉TXT處理
│   └── metadata_extractor.py     # 元數據提取
│
├── 🗄️ 數據管理層 (Data Management Layer)
│   ├── config.py                 # 配置文件
│   ├── metadata_registry.py      # 元數據註冊表
│   ├── metadata_experiment_registry.py  # 實驗元數據註冊表
│   └── query_parser.py           # 查詢解析器
│
├── 🖥️ 用戶界面層 (UI Layer)
│   ├── browser.py                # 文件選擇器
│   └── research_gui.py           # 主GUI界面
│
└── 🧪 測試層 (Testing Layer)
    ├── test_svglib.py           # SVG轉換測試
    ├── test_ghs_icons.py        # GHS圖標測試
    └── test_svglib_integration.py  # SVG集成測試
```

### 📋 核心模塊功能說明

#### 1. 🚀 入口層 (Entry Layer)
- **main.py**: 系統啟動器，負責解析命令行參數並啟動相應界面
- **research_gui.py**: Streamlit Web界面，提供用戶交互功能

#### 2. 🔍 搜索層 (Search Layer)
- **search_agent.py**: 智能搜索代理，協調多個搜索源
- **perplexity_search_fallback.py**: 使用Perplexity API進行備用搜索
- **europepmc_handler.py**: 處理歐洲PMC醫學文獻數據庫
- **pubchem_handler.py**: 處理PubChem化學數據庫，提取化學品信息

#### 3. 🧠 知識處理層 (Knowledge Processing Layer)
- **knowledge_agent.py**: 知識代理，整合多源信息
- **rag_core.py**: RAG（檢索增強生成）核心功能
- **chunk_embedding.py**: 文檔分塊和向量嵌入
- **semantic_lookup.py**: 語義搜索和查找

#### 4. 📄 文檔處理層 (Document Processing Layer)
- **file_upload.py**: 處理用戶上傳的文件
- **pdf_read_and_chunk_page_get.py**: PDF文檔讀取和分頁處理
- **document_renamer.py**: 自動重命名文檔
- **excel_to_txt_by_row.py**: Excel文件轉換為文本格式
- **metadata_extractor.py**: 從文檔中提取元數據

#### 5. 🗄️ 數據管理層 (Data Management Layer)
- **config.py**: 系統配置文件
- **metadata_registry.py**: 元數據註冊和管理
- **metadata_experiment_registry.py**: 實驗相關元數據管理
- **query_parser.py**: 用戶查詢解析和處理

### 🔄 數據流 (Data Flow)

```
用戶輸入 → 查詢解析 → 搜索代理 → 多源數據收集 → 知識處理 → 結果生成 → 界面展示
    ↓           ↓           ↓              ↓            ↓           ↓
  GUI界面    query_parser  search_agent  各數據庫     rag_core    research_gui
```

### 🎯 主要功能流程

#### 1. 文檔處理流程
```
文件上傳 → 格式檢測 → 內容提取 → 分塊處理 → 向量嵌入 → 存儲到知識庫
```

#### 2. 查詢處理流程
```
用戶查詢 → 語義解析 → 多源搜索 → 結果整合 → 知識推理 → 答案生成
```

#### 3. 化學品信息處理流程
```
化學品名稱 → PubChem查詢 → 元數據提取 → 安全信息 → 實驗建議
```

### 🛠️ 技術棧 (Technology Stack)

- **Web框架**: Streamlit
- **搜索API**: Perplexity, Europe PMC, PubChem
- **文檔處理**: PyPDF2, python-docx, pandas
- **向量數據庫**: 內嵌向量存儲
- **圖像處理**: svglib, PyMuPDF, PIL
- **Web自動化**: Selenium

### 📁 目錄結構說明

- **experiment_data/**: 實驗數據存儲目錄
- **test_output/**: 測試輸出目錄
- **.vscode/**: VS Code配置
- **__pycache__/**: Python緩存文件

### 🔧 配置文件

- **requirements_svglib.txt**: 依賴包列表
- **config.py**: 系統配置
- **SVGLIB_MIGRATION.md**: SVG轉換遷移說明
- **CAIRO_FIX_README.md**: Cairo依賴修復說明

### 🎓 學習重點

1. **模塊化設計**: 每個功能都有獨立的模塊
2. **錯誤處理**: 完善的異常處理機制
3. **配置管理**: 集中的配置管理
4. **測試驅動**: 包含完整的測試套件
5. **文檔化**: 詳細的代碼註解和架構說明 