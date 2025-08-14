# Prompt 函數用途說明

## 函數分類與用途

### 1. 知識庫查詢相關函數

#### `build_prompt` - 嚴謹引用模式
- **用途**：基於文獻進行準確引用
- **適用場景**：知識庫查詢的嚴謹引用模式
- **特點**：
  - 嚴格基於提供的文獻片段回答
  - 確保每個論點都有文獻支持
  - 適合學術研究，需要準確引用的場景
- **參數**：`(chunks: List[Document], question: str)`
- **返回**：`(system_prompt: str, citations: List[Dict])`

#### `build_inference_prompt` - 推論模式
- **用途**：允許基於文獻進行推論和創新建議
- **適用場景**：知識庫查詢的推論模式
- **特點**：
  - 可以進行綜合分析
  - 提出新的合成路徑和條件建議
  - 允許基於已知實驗條件提出創新建議
  - 適合創新研究，需要推論和創新建議的場景
- **參數**：`(chunks: List[Document], question: str)`
- **返回**：`(system_prompt: str, citations: List[Dict])`

### 2. 實驗建議相關函數

#### `build_dual_inference_prompt` - 雙重推論模式
- **用途**：納入文獻與實驗實際資料來給出改進建議
- **適用場景**：未來要納入實驗建議的功能
- **特點**：
  - 同時載入文獻向量庫和實驗向量庫
  - 結合文獻知識和實驗數據
  - 提供更全面的改進建議
  - 需要實驗數據支持
- **參數**：`(chunks_paper: List[Document], question: str, experiment_chunks: List[Document])`
- **返回**：`(system_prompt: str, citations: List[Dict])`

## 使用場景對照表

| 功能模組 | 嚴謹模式 | 推論模式 | 雙重推論模式 |
|---------|---------|---------|-------------|
| 知識庫查詢 | `build_prompt` | `build_inference_prompt` | ❌ 不適用 |
| 實驗建議 | ❌ 不適用 | ❌ 不適用 | `build_dual_inference_prompt` |
| 研究提案 | 其他函數 | 其他函數 | ❌ 不適用 |

## 重要提醒

### ❌ 常見錯誤
1. **錯誤使用 `build_dual_inference_prompt` 於知識庫查詢**
   - 這個函數需要實驗數據，知識庫查詢不應該使用
   - 正確應該使用 `build_inference_prompt`

2. **混淆推論模式函數**
   - `build_inference_prompt`：僅基於文獻的推論
   - `build_dual_inference_prompt`：基於文獻+實驗數據的推論

### ✅ 正確使用方式

#### 知識庫查詢
```python
# 嚴謹引用模式
if answer_mode == "rigorous":
    system_prompt, citations = build_prompt(chunks, question)

# 推論模式
elif answer_mode == "inference":
    system_prompt, citations = build_inference_prompt(chunks, question)
```

#### 實驗建議（未來功能）
```python
# 雙重推論模式（需要實驗數據）
system_prompt, citations = build_dual_inference_prompt(
    chunks_paper=paper_chunks,
    question=question,
    experiment_chunks=experiment_chunks
)
```

## 函數簽名對比

```python
# 知識庫查詢函數
def build_prompt(chunks: List[Document], question: str) -> Tuple[str, List[Dict]]
def build_inference_prompt(chunks: List[Document], question: str) -> Tuple[str, List[Dict]]

# 實驗建議函數
def build_dual_inference_prompt(
    chunks_paper: List[Document], 
    question: str, 
    experiment_chunks: List[Document]
) -> Tuple[str, List[Dict]]
```

## 注意事項

1. **參數差異**：
   - 知識庫查詢函數：只需要 `chunks` 和 `question`
   - 雙重推論函數：需要 `chunks_paper`、`question` 和 `experiment_chunks`

2. **使用時機**：
   - 知識庫查詢：用戶直接提問，基於文獻回答
   - 實驗建議：需要結合實驗數據給出改進建議

3. **未來擴展**：
   - `build_dual_inference_prompt` 為未來實驗建議功能預留
   - 當前知識庫查詢不應該使用此函數 