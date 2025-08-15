"""
RAG核心模組
==========

基於檢索增強生成的AI研究助手核心功能
整合文獻檢索、知識提取和智能問答
"""

import os
import json
import time
import re
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from collections import defaultdict


# 導入必要的模組
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from chunk_embedding import get_chroma_instance
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import openai

# 導入配置和橋接模組
from config import (
    OPENAI_API_KEY, 
    VECTOR_INDEX_DIR, 
    EMBEDDING_MODEL_NAME,
    MAX_TOKENS,
    CHUNK_SIZE,
    CHUNK_OVERLAP
)
from model_config_bridge import get_model_params, get_current_model

# 設定OpenAI API Key
openai.api_key = OPENAI_API_KEY

def get_dynamic_schema_params():
    """
    從設定管理器獲取動態的 JSON Schema 參數
    
    Returns:
        Dict: 包含 min_length 和 max_length 的字典
    """
    try:
        # 導入設定管理器
        import sys
        backend_path = os.path.join(os.path.dirname(__file__), "..", "backend")
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        
        from core.settings_manager import settings_manager
        json_schema_params = settings_manager.get_json_schema_parameters()
        
        return {
            "min_length": json_schema_params.get("min_length", 5),
            "max_length": json_schema_params.get("max_length", 100)
        }
    except Exception as e:
        print(f"⚠️ 無法獲取動態 schema 參數，使用預設值: {e}")
        return {
            "min_length": 5,
            "max_length": 100
        }

def create_research_proposal_schema():
    """
    動態創建研究提案的 JSON Schema
    
    Returns:
        Dict: 研究提案的 JSON Schema
    """
    schema_params = get_dynamic_schema_params()
    
    return {
        "type": "object",
        "title": "ResearchProposal",
        "additionalProperties": False,
        "required": [
            "proposal_title",
            "need",
            "solution", 
            "differentiation",
            "benefit",
            "experimental_overview",
            "materials_list"
        ],
        "properties": {
            "proposal_title": {
                "type": "string",
                "description": "研究提案的標題，總結研究目標和創新點",
                "minLength": 10
                #"maxLength": 1000
            },
            "need": {
                "type": "string", 
                "description": "研究需求和現有解決方案的局限性，明確需要解決的技術瓶頸",
                "minLength": 10
                #"maxLength": 600  # 允許更長的描述
            },
            "solution": {
                "type": "string",
                "description": "具體的設計和開發策略，包括新的結構、組成或方法",
                "minLength": 10
                #"maxLength": 1000
            },
            "differentiation": {
                "type": "string",
                "description": "與現有文獻或技術的比較，強調結構、性能或實施方面的突破",
                "minLength": 10
                #"maxLength": 800
            },
            "benefit": {
                "type": "string",
                "description": "預期的性能改進或應用範圍擴展，盡可能提供定量估計",
                "minLength": 10
                #"maxLength": 600
            },
            "experimental_overview": {
                "type": "string",
                "description": "實驗概述，包括起始材料、條件、儀器設備和步驟描述",
                "minLength": 10
                #"maxLength": 600
            },
            "materials_list": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "CRITICAL: 僅列出IUPAC化學品名稱，每個項目必須是單一化學品名稱，不包含任何描述、備註、括號說明或其他文字。嚴禁包含如'(dobpdc)'、'(representative...)'、'(trifluoromethyl-substituted...)'等括號內容。每個化學品名稱必須是標準的IUPAC命名，例如：magnesium nitrate hexahydrate, 4,4'-dioxidobiphenyl-3,3'-dicarboxylic acid, 2-(2,2,2-trifluoroethylamino)ethan-1-amine, N,N-dimethylacetamide",
                "minItems": 1
            }
        }
    }

def create_experimental_detail_schema():
    """
    動態創建實驗細節的 JSON Schema
    
    Returns:
        Dict: 實驗細節的 JSON Schema
    """
    schema_params = get_dynamic_schema_params()
    
    # 根據測試報告，簡化 schema 以避免過長輸出
    return {
        "type": "object",
        "title": "ExperimentalDetail",
        "additionalProperties": False,
        "required": [
            "synthesis_process",
            "materials_and_conditions",
            "analytical_methods",
            "precautions"
        ],
        "properties": {
            "synthesis_process": {
                "type": "string",
                "description": "詳細的合成過程，包括步驟、條件、時間等",
                "minLength": 10
                #"maxLength": 1000  # 限制長度避免過長輸出
            },
            "materials_and_conditions": {
                "type": "string",
                "description": "使用的材料和反應條件，包括濃度、溫度、壓力等",
                "minLength": 10
                #"maxLength": 600  # 限制長度
            },
            "analytical_methods": {
                "type": "string",
                "description": "分析方法和表徵技術，如XRD、SEM、NMR等",
                "minLength": 10
                #"maxLength": 400  # 限制長度
            },
            "precautions": {
                "type": "string",
                "description": "實驗注意事項和安全預防措施",
                "minLength": 10
                #"maxLength": 400  # 限制長度
            }
        }
    }

def create_revision_explain_schema():
    """
    動態創建修訂說明的 JSON Schema
    
    Returns:
        Dict: 修訂說明的 JSON Schema
    """
    schema_params = get_dynamic_schema_params()
    
    return {
        "type": "object",
        "title": "RevisionExplain",
        "additionalProperties": False,
        "required": [
            "revision_explain"
        ],
        "properties": {
            "revision_explain": {
                "type": "string",
                "description": "詳細說明修訂的原因、改進點和新的研究方向，包括技術創新點和預期效果",
                "minLength": 10
                #"maxLength": 1000  # 允許較長的說明
            }
        }
    }

def create_revision_proposal_schema():
    """
    動態創建修訂提案的 JSON Schema (包含修訂說明)
    
    Returns:
        Dict: 修訂提案的 JSON Schema
    """
    schema_params = get_dynamic_schema_params()
    
    return {
        "type": "object",
        "title": "RevisionProposal",
        "additionalProperties": False,
        "required": [
            "revision_explanation",
            "proposal_title",
            "need",
            "solution", 
            "differentiation",
            "benefit",
            "experimental_overview",
            "materials_list"
        ],
        "properties": {
            "revision_explanation": {
                "type": "string",
                "description": "簡要說明修訂的邏輯和主要改進點，基於用戶反饋對原始提案的修改原因",
                "minLength": 10
            },
            "proposal_title": {
                "type": "string",
                "description": "研究提案的標題，總結研究目標和創新點",
                "minLength": 10
            },
            "need": {
                "type": "string", 
                "description": "研究需求和現有解決方案的局限性，明確需要解決的技術瓶頸",
                "minLength": 10
            },
            "solution": {
                "type": "string",
                "description": "具體的設計和開發策略，包括新的結構、組成或方法",
                "minLength": 10
            },
            "differentiation": {
                "type": "string",
                "description": "與現有文獻或技術的比較，強調結構、性能或實施方面的突破",
                "minLength": 10
            },
            "benefit": {
                "type": "string",
                "description": "預期的性能改進或應用範圍擴展，盡可能提供定量估計",
                "minLength": 10
            },
            "experimental_overview": {
                "type": "string",
                "description": "實驗概述，包括起始材料、條件、儀器設備和步驟描述",
                "minLength": 10
            },
            "materials_list": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "CRITICAL: 僅列出IUPAC化學品名稱，每個項目必須是單一化學品名稱，不包含任何描述、備註、括號說明或其他文字。嚴禁包含如'(dobpdc)'、'(representative...)'、'(trifluoromethyl-substituted...)'等括號內容。每個化學品名稱必須是標準的IUPAC命名，例如：magnesium nitrate hexahydrate, 4,4'-dioxidobiphenyl-3,3'-dicarboxylic acid, 2-(2,2,2-trifluoroethylamino)ethan-1-amine, N,N-dimethylacetamide",
                "minItems": 1
            }
        }
    }

# 動態生成 JSON Schema
RESEARCH_PROPOSAL_SCHEMA = create_research_proposal_schema()
EXPERIMENTAL_DETAIL_SCHEMA = create_experimental_detail_schema()
REVISION_EXPLAIN_SCHEMA = create_revision_explain_schema()
REVISION_PROPOSAL_SCHEMA = create_revision_proposal_schema()

# Embedding model configuration

# ==================== 向量數據庫管理 ====================

def load_paper_vectorstore():
    """
    載入文獻向量數據庫
    
    功能：
    1. 獲取或創建文獻向量數據庫實例
    2. 使用緩存避免重複創建
    
    返回：
        Chroma: 文獻向量數據庫對象
    
    技術細節：
    - 使用緩存的 Chroma 實例
    - 持久化存儲在paper_vector目錄
    - 集合名稱為"paper"
    """
    return get_chroma_instance("paper")


def load_experiment_vectorstore():
    """
    載入實驗數據向量數據庫
    
    功能：
    1. 獲取或創建實驗數據向量數據庫實例
    2. 使用緩存避免重複創建
    
    返回：
        Chroma: 實驗數據向量數據庫對象
    
    技術細節：
    - 使用緩存的 Chroma 實例
    - 持久化存儲在experiment_vector目錄
    - 集合名稱為"experiment"
    """
    return get_chroma_instance("experiment")


# ==================== 文檔檢索功能 ====================

def retrieve_chunks_multi_query(
    vectorstore, query_list: List[str], k: int = 10, fetch_k: int = 20, score_threshold: float = 0.35
    ) -> List[Document]:
    """
    多查詢文檔檢索功能
    
    功能：
    1. 對多個查詢進行並行檢索
    2. 去重和排序檢索結果
    3. 提供詳細的檢索統計信息
    
    參數：
        vectorstore: 向量數據庫對象
        query_list (List[str]): 查詢列表
        k (int): 返回的文檔數量
        fetch_k (int): 初始檢索的文檔數量
        score_threshold (float): 相似度閾值
    
    返回：
        List[Document]: 檢索到的文檔列表
    
    技術細節：
    - 使用MMR（最大邊際相關性）搜索
    - 自動去重避免重複內容
    - 提供詳細的檢索日誌
    """
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": k, "fetch_k": fetch_k, "score_threshold": score_threshold}
    )

    # 使用字典進行去重
    chunk_dict = {}
    print("🔍 查詢列表：", query_list)
    
    # 對每個查詢進行檢索
    for q in query_list:
        docs = retriever.get_relevant_documents(q)
        for doc in docs:
            # 使用唯一標識符進行去重
            key = doc.metadata.get("exp_id") or doc.metadata.get("source") or doc.page_content[:30]
            chunk_dict[key] = doc
    
    # 限制返回結果數量，使用傳入的 k 參數
    result = list(chunk_dict.values())[:k]

    # 檢索結果驗證
    if not result:
        print("⚠️ 沒有檢索到任何文檔，建議檢查檢索器或嵌入格式")
    else:
        print(f"🔍 多查詢檢索共找到 {len(result)} 個文檔：")
        print("🔍 檢索到的文檔預覽：")
        for i, doc in enumerate(result[:5], 1):
            meta = doc.metadata
            filename = meta.get("filename") or meta.get("source", "Unknown")
            page = meta.get("page_number") or meta.get("page", "?")
            preview = doc.page_content[:80].replace("\n", " ")
            print(f"--- 文檔 {i} ---")
            print(f"📄 {filename} | 頁碼 {page}")
            print(f"📝 內容預覽：{preview}")
            print()

    return result


def preview_chunks(chunks: List[Document], title: str, max_preview: int = 5):
    """
    預覽文檔塊內容
    
    功能：
    1. 顯示文檔塊的基本信息
    2. 提供內容預覽
    3. 幫助調試和驗證檢索結果
    
    參數：
        chunks (List[Document]): 文檔塊列表
        title (str): 預覽標題
        max_preview (int): 最大預覽數量
    """
    print(f"\n📦【{title}】共找到 {len(chunks)} 個文檔塊")

    if not chunks:
        print("⚠️ 沒有任何段落可顯示。")
        return

    # 顯示前幾個文檔塊的詳細信息
    for i, doc in enumerate(chunks[:max_preview], 1):
        meta = doc.metadata
        filename = meta.get("filename") or meta.get("source", "Unknown")
        page = meta.get("page_number") or meta.get("page", "?")
        preview = doc.page_content[:100].replace("\n", " ")
        print(f"--- Chunk {i} ---")
        print(f"📄 Filename: {filename} | Page: {page}")
        print(f"📚 Preview: {preview}")


# ==================== 提示詞構建功能 ====================

def build_prompt(chunks: List[Document], question: str) -> Tuple[str, List[Dict]]: #嚴謹回答模式，不允許使用任何外部知識
    # 檢查：chunks 必須是 List[Document]，question 應為 str
    context_text = ""
    citations = []
    citation_map = {}
    
    for i, doc in enumerate(chunks):
        # 檢查：doc 應有 metadata 屬性，且為 dict
        metadata = doc.metadata
        title = metadata.get("title", "Untitled")
        # 檢查：filename 來源於 "filename" 或 "source"，若都無則為 "Unknown"
        filename = metadata.get("filename") or metadata.get("source", "Unknown")
        # 檢查：page 來源於 "page_number" 或 "page"，若都無則為 "?"
        page = metadata.get("page_number") or metadata.get("page", "?")
        # 預覽片段，取前 80 字元，並將換行替換為空格
        snippet = doc.page_content[:80].replace("\n", " ")

        # 檢查：避免重複的 (filename, page) 組合
        citation_key = f"{filename}_p{page}"
        if citation_key not in citation_map:
            label = f"[{len(citations) + 1}]"
            citations.append({
                "label": label,
                "title": title,
                "source": filename,
                "page": page,
                "snippet": snippet
            })
            citation_map[citation_key] = label
        else:
            label = citation_map[citation_key]

        # context_text 累加每個 chunk 的內容，格式為 [n] title | Page n
        context_text += f"{label} {title} | Page {page}\n{doc.page_content}\n\n"

    # system_prompt is the final prompt containing context_text and question
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
    # Check: return system_prompt with trimmed whitespace and citations list
    return system_prompt.strip(), citations


def call_llm(prompt: str) -> str:
    print(f"🔍 調用 LLM，提示詞長度：{len(prompt)} 字符")
    print(f"🔍 DEBUG: prompt 類型: {type(prompt)}")
    print(f"🔍 DEBUG: prompt 前100字符: {prompt[:100]}...")
    
    # 獲取當前使用的模型信息和參數
    try:
        from model_config_bridge import get_current_model, get_model_params
        current_model = get_current_model()
        llm_params = get_model_params()
        print(f"🤖 使用模型：{current_model}")
        print(f"🔧 模型參數：{llm_params}")
        print(f"🔍 DEBUG: current_model 類型: {type(current_model)}")
        print(f"🔍 DEBUG: current_model.startswith('gpt-5'): {current_model.startswith('gpt-5')}")
    except Exception as e:
        print(f"⚠️ 無法獲取模型信息：{e}")
        # 使用fallback配置
        llm_params = {
            "model": "gpt-4-1106-preview",
            "temperature": 0.3,
            "max_tokens": 4000,
            "timeout": 120,
        }
    
    try:
        # 根據模型類型選擇不同的API
        if current_model.startswith('gpt-5'):
            # GPT-5系列使用Responses API
            from openai import OpenAI
            client = OpenAI()
            
            # 準備Responses API的參數
            # 使用設定的max_output_tokens，不自動提高
            max_tokens = llm_params.get('max_output_tokens', 2000)
            print(f"🔧 使用設定的max_output_tokens: {max_tokens}")
            
            responses_params = {
                'model': current_model,
                'input': [{'role': 'user', 'content': prompt}],
                'max_output_tokens': max_tokens
            }
            
            # 添加其他參數（排除model、input和max_output_tokens）
            for key, value in llm_params.items():
                if key not in ['model', 'input', 'max_output_tokens']:
                    responses_params[key] = value
            
            print(f"🔧 使用Responses API，參數：{responses_params}")
            print(f"🔍 DEBUG: 準備調用 client.responses.create")
            

            
            # 處理GPT-5的incomplete狀態
            max_retries = 3
            retry_count = 0
            current_max_tokens = max_tokens
            
            while retry_count < max_retries:
                # 更新token數（每次重試增加1500）
                if retry_count > 0:
                    current_max_tokens += 1500
                    responses_params['max_output_tokens'] = current_max_tokens
                    print(f"🔄 重試 {retry_count}：提高max_output_tokens到 {current_max_tokens}")
                
                response = client.responses.create(**responses_params)
                
                print(f"🔍 DEBUG: API調用完成 (嘗試 {retry_count + 1}/{max_retries})")
                print(f"🔍 DEBUG: response 類型: {type(response)}")
                print(f"🔍 DEBUG: response.status: {getattr(response, 'status', 'N/A')}")
                
                # 檢查整體response狀態
                if hasattr(response, 'status') and response.status == 'incomplete':
                    print(f"⚠️ 檢測到incomplete狀態，等待後重試...")
                    print(f"💡 當前max_output_tokens: {current_max_tokens}")
                    retry_count += 1
                    if retry_count < max_retries:
                        import time
                        time.sleep(2)  # 等待2秒後重試
                        continue
                    else:
                        print(f"❌ 達到最大重試次數，使用incomplete的結果")
                
                # 提取文本內容（優先使用output_text，後備解析output陣列）
                output = ""
                
                # 1) 優先嘗試官方便捷屬性 output_text
                try:
                    if getattr(response, "output_text", None):
                        txt = response.output_text.strip()
                        if txt:
                            print(f"✅ 使用 output_text: {len(txt)} 字符")
                            output = txt
                except Exception as e:
                    print(f"⚠️ output_text 提取失敗: {e}")
                
                # 2) 如果output_text為空，後備解析output陣列
                if not output:
                    if hasattr(response, 'output') and response.output:
                        print(f"🔍 DEBUG: 開始解析 output 陣列，共 {len(response.output)} 個項目")
                        
                        for i, item in enumerate(response.output):
                            item_type = getattr(item, "type", None)
                            item_status = getattr(item, "status", None)
                            print(f"  - [{i}] type={item_type}, status={item_status}")
                            
                            # 最終答案通常在 type="message"
                            if item_type == "message":
                                content = getattr(item, "content", []) or []
                                print(f"    📝 message 有 {len(content)} 個 content 項目")
                                
                                for j, c in enumerate(content):
                                    # content 物件通常有 .text
                                    textval = getattr(c, "text", None)
                                    if textval:
                                        print(f"    ✅ content[{j}] 提取到文本: {len(textval)} 字符")
                                        output += textval
                                    else:
                                        print(f"    ⚠️ content[{j}] 沒有 text 屬性")
                    else:
                        print(f"🔍 DEBUG: response 沒有 output 屬性或 output 為空")

                output = output.strip()
                print(f"🔍 DEBUG: 最終 output 長度: {len(output)}")
                print(f"🔍 DEBUG: 最終 output 內容: {output[:200]}...")

                # 檢查整體response狀態
                response_status = getattr(response, 'status', None)
                if response_status == 'incomplete':
                    print(f"⚠️ 整體響應狀態為 incomplete")
                    if output:
                        print(f"✅ 即使incomplete狀態，仍成功提取文本: {len(output)} 字符")
                        print(f"✅ LLM 調用成功，回應長度：{len(output)} 字符")
                        print(f"📝 LLM 回應預覽：{output[:200]}...")
                        return output
                    else:
                        print(f"❌ incomplete狀態且無法提取文本")
                        retry_count += 1
                        if retry_count < max_retries:
                            import time
                            time.sleep(2)  # 等待2秒後重試
                            continue
                        else:
                            print(f"❌ 達到最大重試次數")
                            print(f"💡 已嘗試提高token數到 {current_max_tokens}")
                            return ""
                else:
                    # 正常狀態
                    if output:
                        print(f"✅ 成功提取文本: {len(output)} 字符")
                        print(f"✅ LLM 調用成功，回應長度：{len(output)} 字符")
                        print(f"📝 LLM 回應預覽：{output[:200]}...")
                        return output
                    else:
                        print(f"❌ 無法提取文本")
                        retry_count += 1
                        if retry_count < max_retries:
                            import time
                            time.sleep(2)
                            continue
                        else:
                            print(f"❌ 達到最大重試次數")
                            print(f"💡 已嘗試提高token數到 {current_max_tokens}")
                            return ""

            print(f"❌ 所有重試都失敗，返回空字符串")
            return ""
            
        else:
            # GPT-4系列使用Chat Completions API (LangChain)
            llm = ChatOpenAI(**llm_params)
            response = llm.invoke(prompt)
            print(f"✅ LLM 調用成功，回應長度：{len(response.content)} 字符")
            print(f"📝 LLM 回應預覽：{response.content[:200]}...")
            return response.content
            
    except Exception as e:
        print(f"❌ LLM 調用失敗：{e}")
        return ""


def call_llm_structured_proposal(system_prompt: str, user_prompt: str) -> Dict[str, Any]:
    """
    使用OpenAI Responses API的JSON structured output生成結構化研究提案
    
    Args:
        system_prompt: 系統提示詞
        user_prompt: 用戶提示詞（包含文獻摘要和研究目標）
    
    Returns:
        Dict[str, Any]: 符合RESEARCH_PROPOSAL_SCHEMA的結構化提案
    """
    print(f"🔍 調用結構化LLM，系統提示詞長度：{len(system_prompt)} 字符")
    print(f"🔍 用戶提示詞長度：{len(user_prompt)} 字符")
    
    # 獲取當前使用的模型信息和參數
    try:
        from model_config_bridge import get_current_model, get_model_params
        current_model = get_current_model()
        llm_params = get_model_params()
        print(f"🤖 使用模型：{current_model}")
        print(f"🔧 模型參數：{llm_params}")
    except Exception as e:
        print(f"⚠️ 無法獲取模型信息：{e}")
        # 使用fallback配置
        current_model = "gpt-4-1106-preview"
        llm_params = {
            "model": "gpt-4-1106-preview",
            "temperature": 0.0,  # 結構化輸出使用0溫度
            "max_tokens": 4000,
            "timeout": 120,
        }
    
    try:
        # 根據模型類型選擇不同的API
        if current_model.startswith('gpt-5'):
            # GPT-5系列使用Responses API with JSON Schema
            from openai import OpenAI
            client = OpenAI()
            
            # 準備Responses API的參數
            max_tokens = llm_params.get('max_output_tokens', 4000)
            
            # 動態獲取最新的 schema
            current_schema = create_research_proposal_schema()
            
            # 使用 Responses API + JSON Schema (適用於所有 GPT-5 系列模型)
            responses_params = {
                'model': current_model,
                'input': [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                'text': {
                    'format': {
                        'type': 'json_schema',
                        'name': 'ResearchProposal',
                        'strict': True,
                        'schema': current_schema,
                    },
                    'verbosity': 'low'  # 使用 low verbosity
                },
                'reasoning': {'effort': 'medium'},  # 使用 medium reasoning
                'max_output_tokens': max_tokens
            }
            
            print(f"🔧 使用Responses API with JSON Schema，參數：{responses_params}")
            
            # 處理GPT-5的incomplete狀態
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                response = client.responses.create(**responses_params)
                
                print(f"🔍 DEBUG: API調用完成 (嘗試 {retry_count + 1}/{max_retries})")
                print(f"🔍 DEBUG: response.status: {getattr(response, 'status', 'N/A')}")
                
                # 檢查整體response狀態
                if hasattr(response, 'status') and response.status == 'incomplete':
                    print(f"⚠️ 檢測到incomplete狀態，等待後重試...")
                    retry_count += 1
                    if retry_count < max_retries:
                        import time
                        time.sleep(2)  # 等待2秒後重試
                        continue
                    else:
                        print(f"❌ 達到最大重試次數")
                        return {}
                
                # 提取JSON內容
                try:
                    # 優先使用 resp.output_text
                    output_text = getattr(response, 'output_text', None)
                    if output_text:
                        print(f"✅ 使用 resp.output_text 提取內容: {len(output_text)} 字符")
                        try:
                            proposal_data = json.loads(output_text)
                            print(f"✅ 成功解析JSON結構化提案")
                            
                            # 本地 JSON Schema 驗證
                            try:
                                from jsonschema import Draft202012Validator
                                from jsonschema.exceptions import ValidationError
                                Draft202012Validator(current_schema).validate(proposal_data)
                                print("✅ 本地 Schema 驗證通過")
                            except ImportError:
                                print("⚠️ jsonschema 未安裝，跳過本地驗證")
                            except ValidationError as e:
                                print(f"⚠️ 本地 Schema 驗證失敗: {e}")
                                # 繼續返回結果，因為 API 端已經驗證過
                            
                            return proposal_data
                        except json.JSONDecodeError as e:
                            print(f"⚠️ JSON解析失敗: {e}")
                            print(f"⚠️ 嘗試的文本: {output_text[:200]}...")
                            return {}
                    
                    # 回退到 resp.output 聚合方式
                    if hasattr(response, 'output') and response.output:
                        parts = []
                        for item in response.output:
                            if hasattr(item, "content"):
                                for content in item.content:
                                    if hasattr(content, "text"):
                                        parts.append(content.text)
                        
                        if parts:
                            text_content = "".join(parts).strip()
                            print(f"✅ 使用 resp.output 聚合提取內容: {len(text_content)} 字符")
                            
                            try:
                                proposal_data = json.loads(text_content)
                                print(f"✅ 成功解析JSON結構化提案")
                                
                                # 本地 JSON Schema 驗證
                                try:
                                    from jsonschema import Draft202012Validator
                                    from jsonschema.exceptions import ValidationError
                                    Draft202012Validator(current_schema).validate(proposal_data)
                                    print("✅ 本地 Schema 驗證通過")
                                except ImportError:
                                    print("⚠️ jsonschema 未安裝，跳過本地驗證")
                                except ValidationError as e:
                                    print(f"⚠️ 本地 Schema 驗證失敗: {e}")
                                    # 繼續返回結果，因為 API 端已經驗證過
                                
                                return proposal_data
                            except json.JSONDecodeError as e:
                                print(f"⚠️ JSON解析失敗: {e}")
                                print(f"⚠️ 嘗試的文本: {text_content[:200]}...")
                                return {}
                    
                    # 如果沒有找到JSON內容
                    print(f"⚠️ 無法從Responses API提取JSON內容")
                    return {}
                    
                except json.JSONDecodeError as e:
                    print(f"❌ JSON解析失敗: {e}")
                    retry_count += 1
                    if retry_count < max_retries:
                        import time
                        time.sleep(2)
                        continue
                    else:
                        print(f"❌ 達到最大重試次數")
                        return {}
                except Exception as e:
                    print(f"❌ 提取JSON內容失敗: {e}")
                    retry_count += 1
                    if retry_count < max_retries:
                        import time
                        time.sleep(2)
                        continue
                    else:
                        print(f"❌ 達到最大重試次數")
                        return {}
            
            print(f"❌ 所有重試都失敗，返回空字典")
            return {}
            
        else:
            # GPT-4系列使用Chat Completions API with function calling
            from openai import OpenAI
            client = OpenAI()
            
            # 動態獲取最新的 schema
            current_schema = create_research_proposal_schema()
            
            # 使用function calling作為fallback
            response = client.chat.completions.create(
                model=current_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0,
                functions=[{
                    "name": "create_research_proposal",
                    "description": "Create a structured research proposal",
                    "parameters": current_schema
                }],
                function_call={"name": "create_research_proposal"},
                max_tokens=llm_params.get('max_tokens', 4000)
            )
            
            # 提取function call結果
            if response.choices[0].message.function_call:
                function_call = response.choices[0].message.function_call
                arguments = json.loads(function_call.arguments)
                print(f"✅ 成功解析function call結構化提案")
                return arguments
            else:
                print(f"❌ 無法從function call提取結果")
                return {}
            
    except Exception as e:
        print(f"❌ 結構化LLM調用失敗：{e}")
        return {}

def call_llm_structured_experimental_detail(chunks: List[Document], proposal: str) -> Dict[str, Any]:
    """
    使用OpenAI Responses API的JSON structured output生成結構化實驗細節
    
    Args:
        chunks: 文獻片段
        proposal: 研究提案
    
    Returns:
        Dict[str, Any]: 符合EXPERIMENTAL_DETAIL_SCHEMA的結構化實驗細節
    """
    print(f"🔍 調用結構化實驗細節LLM，文獻片段數量：{len(chunks)}")
    print(f"🔍 提案長度：{len(proposal)} 字符")
    
    # 獲取當前使用的模型信息和參數
    try:
        from model_config_bridge import get_current_model, get_model_params
        current_model = get_current_model()
        llm_params = get_model_params()
        print(f"🤖 使用模型：{current_model}")
        print(f"🔧 模型參數：{llm_params}")
    except Exception as e:
        print(f"⚠️ 無法獲取模型信息：{e}")
        # 使用fallback配置
        current_model = "gpt-4-1106-preview"
        llm_params = {
            "model": "gpt-4-1106-preview",
            "temperature": 0.0,  # 結構化輸出使用0溫度
            "max_tokens": 4000,
            "timeout": 120,
        }
    
    try:
        # 根據模型類型選擇不同的API
        if current_model.startswith('gpt-5'):
            # GPT-5系列使用Responses API with JSON Schema
            from openai import OpenAI
            client = OpenAI()
            
            # 準備Responses API的參數
            max_tokens = llm_params.get('max_output_tokens', 6000)  # 使用測試報告推薦的 6000
            
            # 構建系統提示詞
            system_prompt = f"""
            You are a professional materials synthesis consultant, skilled at generating detailed experimental procedures based on literature and research proposals.

            Based on the following research proposal and literature information, please generate detailed experimental details:

            --- Research Proposal ---
            {proposal}

            Please generate detailed experimental details including the following four sections:
            1. Synthesis Process: Detailed synthesis steps, conditions, durations, etc.
            2. Materials and Conditions: Materials used, concentrations, temperatures, pressures, and other reaction conditions
            3. Analytical Methods: Characterization techniques such as XRD, SEM, NMR, etc.
            4. Precautions: Experimental notes and safety precautions

            """
            
            # 構建用戶提示詞（包含文獻摘要）
            context_text = ""
            citations = []
            for i, doc in enumerate(chunks):
                meta = doc.metadata
                title = meta.get("title", "Untitled")
                filename = meta.get("filename") or meta.get("source", "Unknown")
                page = meta.get("page_number") or meta.get("page", "?")
                
                context_text += f"[{i+1}] {title} | Page {page}\n{doc.page_content}\n\n"
                citations.append({
                    "label": f"[{i+1}]",
                    "title": title,
                    "source": filename,
                    "page": page
                })
            
            user_prompt = f"""
            基於以下文獻信息生成實驗細節：
            
            --- 文獻摘要 ---
            {context_text}
            
            請生成詳細的實驗細節，確保所有化學品名稱都使用IUPAC命名法。
            """
            
            # 動態獲取最新的 schema
            current_schema = create_experimental_detail_schema()
            
            # 使用測試報告推薦的最佳實踐配置
            responses_params = {
                'model': current_model,
                'input': [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                'text': {
                    'format': {
                        'type': 'json_schema',
                        'name': 'ExperimentalDetail',
                        'strict': True,
                        'schema': current_schema,
                    },
                    'verbosity': 'low'  # 使用 low verbosity 避免過長輸出
                },
                'reasoning': {'effort': 'minimal'},  # 使用 minimal effort 提高速度
                'max_output_tokens': max_tokens
            }
            
            print(f"🔧 使用Responses API，參數：{responses_params}")
            
            # 處理GPT-5的incomplete狀態 - 使用測試報告推薦的配置
            max_retries = 2  # 減少重試次數
            retry_count = 0
            current_max_tokens = max_tokens
            
            while retry_count < max_retries:
                # 更新token數（每次重試增加1000，而不是1500）
                if retry_count > 0:
                    current_max_tokens += 1000
                    responses_params['max_output_tokens'] = current_max_tokens
                    print(f"🔄 重試 {retry_count}：提高max_output_tokens到 {current_max_tokens}")
                
                response = client.responses.create(**responses_params)
                
                print(f"🔍 DEBUG: API調用完成 (嘗試 {retry_count + 1}/{max_retries})")
                print(f"🔍 DEBUG: response 類型: {type(response)}")
                print(f"🔍 DEBUG: response.status: {getattr(response, 'status', 'N/A')}")
                
                # 檢查整體response狀態
                if hasattr(response, 'status') and response.status == 'incomplete':
                    print(f"⚠️ 檢測到incomplete狀態，等待後重試...")
                    print(f"💡 當前max_output_tokens: {current_max_tokens}")
                    retry_count += 1
                    if retry_count < max_retries:
                        import time
                        time.sleep(1)  # 減少等待時間到1秒
                        continue
                    else:
                        print(f"❌ 達到最大重試次數，使用incomplete的結果")
                
                # 提取JSON內容
                try:
                    # 優先使用 resp.output_text
                    output_text = getattr(response, 'output_text', None)
                    if output_text:
                        print(f"✅ 使用 resp.output_text 提取內容: {len(output_text)} 字符")
                        try:
                            experimental_data = json.loads(output_text)
                            print(f"✅ 成功解析JSON結構化實驗細節")
                            
                            # 添加引用信息
                            experimental_data['citations'] = citations
                            
                            return experimental_data
                        except json.JSONDecodeError as e:
                            print(f"⚠️ JSON解析失敗: {e}")
                            print(f"⚠️ 嘗試的文本: {output_text[:200]}...")
                            
                            # 嘗試修復常見的JSON格式問題
                            try:
                                # 嘗試修復未終止的字符串
                                if "Unterminated string" in str(e):
                                    # 找到最後一個完整的引號位置
                                    last_quote = output_text.rfind('"')
                                    if last_quote > 0:
                                        # 截斷到最後一個完整引號並添加結束引號
                                        fixed_text = output_text[:last_quote+1] + '}'
                                        experimental_data = json.loads(fixed_text)
                                        print(f"✅ 修復JSON格式後成功解析")
                                        
                                        # 添加引用信息
                                        experimental_data['citations'] = citations
                                        
                                        return experimental_data
                            except:
                                pass
                            
                            return {}
                    
                    # 回退到 resp.output 聚合方式
                    if hasattr(response, 'output') and response.output:
                        parts = []
                        for item in response.output:
                            if hasattr(item, "content"):
                                for content in item.content:
                                    if hasattr(content, "text"):
                                        parts.append(content.text)
                        
                        if parts:
                            combined_text = "".join(parts)
                            try:
                                experimental_data = json.loads(combined_text)
                                print(f"✅ 成功解析JSON結構化實驗細節（聚合方式）")
                                
                                # 添加引用信息
                                experimental_data['citations'] = citations
                                
                                return experimental_data
                            except json.JSONDecodeError as e:
                                print(f"⚠️ JSON解析失敗（聚合方式）: {e}")
                                return {}
                
                except Exception as e:
                    print(f"⚠️ 內容提取失敗: {e}")
                
                # 如果無法提取內容，重試
                retry_count += 1
                if retry_count < max_retries:
                    import time
                    time.sleep(1)  # 減少等待時間
                    continue
                else:
                    print(f"❌ 達到最大重試次數")
                    print(f"💡 已嘗試提高token數到 {current_max_tokens}")
                    return {}
            
            print(f"❌ 所有重試都失敗，返回空字典")
            return {}
            
        else:
            # GPT-4系列使用Chat Completions API with function calling
            from openai import OpenAI
            client = OpenAI()
            
            # 構建提示詞
            context_text = ""
            citations = []
            for i, doc in enumerate(chunks):
                meta = doc.metadata
                title = meta.get("title", "Untitled")
                filename = meta.get("filename") or meta.get("source", "Unknown")
                page = meta.get("page_number") or meta.get("page", "?")
                
                context_text += f"[{i+1}] {title} | Page {page}\n{doc.page_content}\n\n"
                citations.append({
                    "label": f"[{i+1}]",
                    "title": title,
                    "source": filename,
                    "page": page
                })
            
            system_prompt = f"""
            你是一個專業的材料合成顧問，擅長基於文獻和提案生成詳細的實驗細節。
            
            請基於以下研究提案和文獻信息，生成詳細的實驗細節：
            
            --- 研究提案 ---
            {proposal}
            
            請生成包含以下四個部分的詳細實驗細節：
            1. 合成過程：詳細的合成步驟、條件、時間等
            2. 材料和條件：使用的材料、濃度、溫度、壓力等反應條件
            3. 分析方法：XRD、SEM、NMR等表徵技術
            4. 注意事項：實驗注意事項和安全預防措施
            
            請確保所有化學品名稱都使用IUPAC命名法。
            """
            
            user_prompt = f"""
            基於以下文獻信息生成實驗細節：
            
            --- 文獻摘要 ---
            {context_text}
            
            請生成詳細的實驗細節，確保所有化學品名稱都使用IUPAC命名法。
            """
            
            # 動態獲取最新的 schema
            current_schema = create_experimental_detail_schema()
            
            # 使用function calling作為fallback
            response = client.chat.completions.create(
                model=current_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.0,
                functions=[{
                    "name": "create_experimental_detail",
                    "description": "Create a structured experimental detail",
                    "parameters": current_schema
                }],
                function_call={"name": "create_experimental_detail"},
                max_tokens=llm_params.get('max_tokens', 4000)
            )
            
            # 提取function call結果
            if response.choices[0].message.function_call:
                function_call = response.choices[0].message.function_call
                arguments = json.loads(function_call.arguments)
                print(f"✅ 成功解析function call結構化實驗細節")
                
                # 添加引用信息
                arguments['citations'] = citations
                
                return arguments
            else:
                print(f"❌ 無法從function call提取結果")
                return {}
            
    except Exception as e:
        print(f"❌ 結構化實驗細節LLM調用失敗：{e}")
        return {}

def call_llm_structured_revision_explain(user_feedback: str, proposal: str) -> Dict[str, Any]:
    """
    使用OpenAI Responses API的JSON structured output生成結構化修訂說明
    
    Args:
        user_feedback: 用戶反饋
        proposal: 原始提案
    
    Returns:
        Dict[str, Any]: 符合REVISION_EXPLAIN_SCHEMA的結構化修訂說明
    """
    print(f"🔍 調用結構化修訂說明LLM，用戶反饋長度：{len(user_feedback)}")
    print(f"🔍 提案長度：{len(proposal)} 字符")
    
    # 獲取當前使用的模型信息和參數
    try:
        from model_config_bridge import get_current_model, get_model_params
        current_model = get_current_model()
        llm_params = get_model_params()
        print(f"🤖 使用模型：{current_model}")
        print(f"🔧 模型參數：{llm_params}")
    except Exception as e:
        print(f"⚠️ 無法獲取模型信息：{e}")
        # 使用fallback配置
        current_model = "gpt-4-1106-preview"
        llm_params = {
            "model": "gpt-4-1106-preview",
            "temperature": 0.0,  # 結構化輸出使用0溫度
            "max_tokens": 4000,
            "timeout": 120,
        }
    
    try:
        # 根據模型類型選擇不同的API
        if current_model.startswith('gpt-5'):
            # GPT-5系列使用Responses API with JSON Schema
            from openai import OpenAI
            client = OpenAI()
            
            # 準備Responses API的參數
            max_tokens = llm_params.get('max_output_tokens', 4000)
            
            # 動態獲取最新的 schema
            current_schema = create_revision_explain_schema()
            
            # 構建提示詞
            system_prompt = """
            You are a research proposal revision expert. Your task is to analyze the user's feedback and the original proposal, then provide a detailed explanation of the revision approach.
            
            Please provide a comprehensive explanation that includes:
            1. Analysis of the user's feedback
            2. Identification of key areas for improvement
            3. Specific revision strategies
            4. Expected outcomes and benefits
            5. Technical innovation points
            """
            
            user_prompt = f"""
            --- Original Proposal ---
            {proposal}
            
            --- User Feedback ---
            {user_feedback}
            
            Please provide a detailed revision explanation based on the above information.
            """
            
            # 使用 Responses API + JSON Schema (適用於所有 GPT-5 系列模型)
            responses_params = {
                'model': current_model,
                'input': [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                'text': {
                    'format': {
                        'type': 'json_schema',
                        'name': 'RevisionExplain',
                        'strict': True,
                        'schema': current_schema,
                    },
                    'verbosity': 'low'  # 使用 low verbosity
                },
                'reasoning': {'effort': 'medium'},  # 使用 medium reasoning
                'max_output_tokens': max_tokens
            }
            
            print(f"🔧 使用Responses API with JSON Schema，參數：{responses_params}")
            
            # 處理GPT-5的incomplete狀態
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                response = client.responses.create(**responses_params)
                
                print(f"🔍 DEBUG: API調用完成 (嘗試 {retry_count + 1}/{max_retries})")
                print(f"🔍 DEBUG: response.status: {getattr(response, 'status', 'N/A')}")
                
                # 檢查整體response狀態
                if hasattr(response, 'status') and response.status == 'incomplete':
                    print(f"⚠️ 檢測到incomplete狀態，等待後重試...")
                    retry_count += 1
                    if retry_count < max_retries:
                        import time
                        time.sleep(2)  # 等待2秒後重試
                        continue
                    else:
                        print(f"❌ 達到最大重試次數")
                        return {}
                
                # 提取JSON內容
                try:
                    # 優先使用 resp.output_text
                    output_text = getattr(response, 'output_text', None)
                    if output_text:
                        print(f"✅ 使用 resp.output_text 提取內容: {len(output_text)} 字符")
                        try:
                            revision_data = json.loads(output_text)
                            print(f"✅ 成功解析JSON結構化修訂說明")
                            
                            # 本地驗證 schema
                            try:
                                from jsonschema import validate
                                validate(instance=revision_data, schema=current_schema)
                                print(f"✅ 本地 Schema 驗證通過")
                            except Exception as e:
                                print(f"⚠️ 本地 Schema 驗證失敗: {e}")
                            
                            return revision_data
                        except json.JSONDecodeError as e:
                            print(f"❌ JSON解析失敗: {e}")
                            print(f"🔍 原始輸出: {output_text}")
                            return {}
                    else:
                        print(f"❌ 無法提取 output_text")
                        return {}
                        
                except Exception as e:
                    print(f"❌ 提取JSON內容失敗: {e}")
                    retry_count += 1
                    if retry_count < max_retries:
                        import time
                        time.sleep(2)
                        continue
                    else:
                        print(f"❌ 達到最大重試次數")
                        return {}
            
            print(f"❌ 所有重試都失敗")
            return {}
            
        else:
            # GPT-4系列使用Chat Completions API (LangChain)
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(**llm_params)
            
            # 構建提示詞
            system_prompt = """
            You are a research proposal revision expert. Your task is to analyze the user's feedback and the original proposal, then provide a detailed explanation of the revision approach.
            """
            
            full_prompt = f"{system_prompt}\n\n--- Original Proposal ---\n{proposal}\n\n--- User Feedback ---\n{user_feedback}\n\nPlease provide a detailed revision explanation."
            
            response = llm.invoke(full_prompt)
            print(f"✅ 傳統LLM調用成功，回應長度：{len(response.content)} 字符")
            
            # 返回文本格式
            return {
                'revision_explain': response.content
            }
            
    except Exception as e:
        print(f"❌ 結構化修訂說明LLM調用失敗：{e}")
        return {}

def generate_structured_experimental_detail(chunks: List[Document], proposal: str) -> Dict[str, Any]:
    """
    生成結構化實驗細節的便捷函數
    
    Args:
        chunks: 文獻片段
        proposal: 研究提案
    
    Returns:
        Dict[str, Any]: 結構化實驗細節
    """
    return call_llm_structured_experimental_detail(chunks, proposal)

def generate_structured_revision_explain(user_feedback: str, proposal: str) -> Dict[str, Any]:
    """
    生成結構化修訂說明的便捷函數
    
    Args:
        user_feedback: 用戶反饋
        proposal: 原始提案
    
    Returns:
        Dict[str, Any]: 結構化修訂說明
    """
    return call_llm_structured_revision_explain(user_feedback, proposal)

def structured_experimental_detail_to_text(experimental_data: Dict[str, Any]) -> str:
    """
    將結構化實驗細節轉換為傳統文本格式
    
    Args:
        experimental_data: 結構化實驗細節數據
    
    Returns:
        str: 格式化的文本實驗細節
    """
    if not experimental_data:
        return ""
    
    text_parts = []
    
    
    # Synthesis Process
    if experimental_data.get('synthesis_process'):
        text_parts.append("## Synthesis Process")
        text_parts.append(f"{experimental_data['synthesis_process']}\n")
    
    # Materials and Conditions
    if experimental_data.get('materials_and_conditions'):
        text_parts.append("## Materials and Conditions")
        text_parts.append(f"{experimental_data['materials_and_conditions']}\n")
    
    # Analytical Methods
    if experimental_data.get('analytical_methods'):
        text_parts.append("## Analytical Methods")
        text_parts.append(f"{experimental_data['analytical_methods']}\n")
    
    # Precautions
    if experimental_data.get('precautions'):
        text_parts.append("## Precautions")
        text_parts.append(f"{experimental_data['precautions']}\n")
    
    return "\n".join(text_parts)

def build_inference_prompt(chunks: List[Document], question: str) -> Tuple[str, List[Dict]]:
    context_text = ""
    citations = []
    citation_map = {}
    
    for i, doc in enumerate(chunks):
        meta = doc.metadata
        title = meta.get("title", "Untitled")
        filename = meta.get("filename") or meta.get("source", "Unknown")
        page = meta.get("page_number") or meta.get("page", "?")
        snippet = doc.page_content[:80].replace("\n", " ")
        
        # 檢查：避免重複的 (filename, page) 組合
        citation_key = f"{filename}_p{page}"
        if citation_key not in citation_map:
            label = f"[{len(citations) + 1}]"
            citations.append({
                "label": label,
                "title": title,
                "source": filename,
                "page": page,
                "snippet": snippet
            })
            citation_map[citation_key] = label
        else:
            label = citation_map[citation_key]

        context_text += f"{label} {title} | Page {page}\n{doc.page_content}\n\n"

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
    return system_prompt.strip(), citations

def build_dual_inference_prompt(
    chunks_paper: List[Document],
    question: str,
    experiment_chunks: List[Document]
    ) -> Tuple[str, List[Dict]]:

    paper_context_text = ""
    exp_context_text = ""
    citations = []
    label_index = 1

    # --- Literature Summary ---
    paper_context_text += "--- Literature Summary ---\n"
    for doc in chunks_paper:
        meta = doc.metadata
        title = meta.get("title", "Untitled")
        filename = meta.get("filename") or meta.get("source", "Unknown")
        page = meta.get("page_number") or meta.get("page", "?")
        snippet = doc.page_content[:80].replace("\n", " ")
        label = f"[{label_index}]"

        citations.append({
            "label": label,
            "title": title,
            "source": filename,
            "page": page,
            "snippet": snippet,
            "type": "paper"
        })

        paper_context_text += f"{label} {title} | Page {page}\n{doc.page_content}\n\n"
        label_index += 1

    # --- Experiment Summary ---
    exp_context_text += "--- Similar Experiment Summary ---\n"
    for doc in experiment_chunks:
        meta = doc.metadata
        filename = meta.get("filename") or meta.get("source", "Unknown")
        exp_id = meta.get("exp_id", "unknown_exp")
        snippet = doc.page_content[:80].replace("\n", " ")
        label = f"[{label_index}]"

        citations.append({
            "label": label,
            "title": exp_id,
            "source": filename,
            "page": "-",  # 沒有頁數
            "snippet": snippet,
            "type": "experiment"
        })

        exp_context_text += f"{label} Experiment {exp_id}\n{doc.page_content}\n\n"
        label_index += 1
        
    # --- Prompt Injection ---
    system_prompt = f"""
    You are a materials synthesis consultant who understands and excels at comparing the chemical and physical properties of materials.

    You will see three parts of information. Please conduct comprehensive analysis and provide specific inferences and innovative suggestions for experiments:
    1. Literature summary (with source annotations [1], [2])
    2. Similar experiment summary (from vector database)
    3. Experiment records (tables)

    Please propose new suggestions for the research question, including:
    - Adjusted synthesis pathways and conditions (such as temperature, time, ratios)
    - Factors that may affect synthesis success rate
    - Reasoning behind the causes, citing literature ([1], [2]...) or similar experiment results when necessary
    Important: You can only cite the provided literature excerpts. The current literature excerpt numbers are [1] to [{len(chunks_paper) + len(experiment_chunks)}] (total {len(chunks_paper) + len(experiment_chunks)} excerpts)

    --- Literature Knowledge Sources ---
    {paper_context_text}

    --- Experiment Records ---
    {exp_context_text}

    --- Research Question ---
    {question}
    """
    return system_prompt.strip(), citations



def expand_query(user_prompt: str) -> List[str]:
    """
    Convert user input natural language questions into multiple semantic search query statements.
    The returned English statements can be used for literature vector retrieval.
    """
    # Get dynamic model parameters
    try:
        from model_config_bridge import get_current_model, get_model_params
        current_model = get_current_model()
        llm_params = get_model_params()
    except Exception as e:
        print(f"⚠️ 無法獲取模型參數：{e}")
        current_model = "gpt-4-1106-preview"
        llm_params = {
            "model": "gpt-4-1106-preview",
            "temperature": 0.3,
            "max_tokens": 4000,
            "timeout": 120,
        }

    system_prompt = """You are a scientific assistant helping expand a user's synthesis question into multiple semantic search queries. 
    Each query should be precise, relevant, and useful for retrieving related technical documents. 
    Only return a list of 3 to 6 search queries in English. Do not explain, do not include numbering if not needed."""

    full_prompt = f"{system_prompt}\n\nUser question:\n{user_prompt}"

    try:
        # 根據模型類型選擇不同的API
        if current_model.startswith('gpt-5'):
            # GPT-5系列使用Responses API
            from openai import OpenAI
            client = OpenAI()
            
            # 準備Responses API的參數
            responses_params = {
                'model': current_model,
                'input': [{'role': 'user', 'content': full_prompt}]
            }
            
            # 添加其他參數（排除model和input）
            for key, value in llm_params.items():
                if key not in ['model', 'input']:
                    responses_params[key] = value
            
            # 修復：移除reasoning參數，避免返回ResponseReasoningItem
            if 'reasoning' in responses_params:
                del responses_params['reasoning']
            
            # 確保移除reasoning參數
            if 'reasoning' in responses_params:
                print(f"🔍 DEBUG: 移除 reasoning 參數: {responses_params['reasoning']}")
                del responses_params['reasoning']
                print(f"🔍 DEBUG: 更新後的參數: {responses_params}")
            
            response = client.responses.create(**responses_params)
            
            # 修復：根據GPT-5 cookbook正確處理Responses API的回應格式
            output = ""
            if hasattr(response, 'output') and response.output:
                for item in response.output:
                    # 跳過ResponseReasoningItem對象
                    if hasattr(item, 'type') and item.type == 'reasoning':
                        continue
                    
                    if hasattr(item, "content"):
                        for content in item.content:
                            if hasattr(content, "text"):
                                output += content.text
                    elif hasattr(item, "text"):
                        # 直接文本輸出
                        output += item.text
                    elif hasattr(item, "message"):
                        # message對象
                        if hasattr(item.message, "content"):
                            output += item.message.content
                        else:
                            output += str(item.message)
                    else:
                        # 其他情況，嘗試轉換為字符串，但過濾掉ResponseReasoningItem
                        item_str = str(item)
                        if not item_str.startswith('ResponseReasoningItem'):
                            output += item_str
            
            output = output.strip()
            
        else:
            # GPT-4系列使用Chat Completions API (LangChain)
            llm = ChatOpenAI(**llm_params)
            output = llm.predict(full_prompt).strip()

        # Try to parse into query list
        if output.startswith("[") and output.endswith("]"):
            try:
                return eval(output)
            except Exception:
                pass  # fall back

        queries = [line.strip("-• ").strip() for line in output.split("\n") if line.strip()]
        return [q for q in queries if len(q) > 4]
        
    except Exception as e:
        print(f"❌ 查詢擴展失敗：{e}")
        # 返回原始查詢作為fallback
        return [user_prompt]


def build_proposal_prompt(question: str, chunks: List[Document]) -> Tuple[str, List[Dict]]:
    paper_context_text = ""
    citations = []
    citation_map = {}

    for i, doc in enumerate(chunks):
        
        meta = doc.metadata
        title = meta.get("title", "Untitled")
        filename = meta.get("filename") or meta.get("source", "Unknown")
        page = meta.get("page_number") or meta.get("page", "?")
        snippet = doc.page_content[:80].replace("\n", " ")
        
        # 檢查：避免重複的 (filename, page) 組合
        citation_key = f"{filename}_p{page}"
        if citation_key not in citation_map:
            label = f"[{len(citations) + 1}]"
            citations.append({
                "label": label,
                "title": title,
                "source": filename,
                "page": page,
                "snippet": snippet
            })
            citation_map[citation_key] = label
        else:
            label = citation_map[citation_key]

        paper_context_text += f"{label} {title} | Page {page}\n{doc.page_content}\n\n"

    system_prompt = f"""
    You are a scientific research expert who excels at proposing innovative and feasible research proposals based on literature summaries and research objectives.
    Your expertise covers materials science, chemistry, physics, and engineering, and you are capable of deriving new ideas grounded in experimental evidence and theoretical principles.

    Your task is to generate a structured research proposal based on the provided literature excerpts and research objectives. The proposal should be innovative, scientifically rigorous, and feasible.

    IMPORTANT: You must respond in valid JSON format only. Do not include any text before or after the JSON object.

    The JSON must have the following structure:
    {{
        "proposal_title": "Title of the research proposal",
        "need": "Research need and current limitations",
        "solution": "Proposed design and development strategies",
        "differentiation": "Comparison with existing technologies",
        "benefit": "Expected improvements and benefits",
        "experimental_overview": "Experimental approach and methodology",
        "materials_list": ["material1", "material2", "material3"]
    }}

    Key requirements:
    1. Propose new components, structures, or mechanisms (e.g., new ligands, frameworks, catalysts, processing techniques) based on the literature
    2. Clearly explain structural or functional advantages and potential reactivity/performance
    3. All proposed designs must have a logical basis — avoid inventing unreasonable structures without justification
    4. Maintain scientific rigor, clarity, and avoid vague descriptions
    5. Use only the provided literature labels ([1], [2], etc.) for citations, and do not fabricate sources
    6. Ensure every claim is supported by a cited source or reasonable extension from the literature
    7. For materials_list, include ONLY IUPAC chemical names without any descriptions, notes, or parenthetical explanations. Each item must be a single chemical name only.

    Literature excerpts are provided below with labels from [1] to [{len(chunks)}] (total {len(chunks)} excerpts).
    """
    
    return system_prompt.strip(), citations

def build_detail_experimental_plan_prompt(chunks: List[Document], proposal_text: str) -> Tuple[str, List[Dict]]:
    context_text = ""
    citations = []
    citation_map = {}
    
    for i, doc in enumerate(chunks):
        # 檢查：doc 應有 metadata 屬性，且為 dict
        metadata = doc.metadata
        title = metadata.get("title", "Untitled")
        # 檢查：filename 來源於 "filename" 或 "source"，若都無則為 "Unknown"
        filename = metadata.get("filename") or metadata.get("source", "Unknown")
        # 檢查：page 來源於 "page_number" 或 "page"，若都無則為 "?"
        page = metadata.get("page_number") or metadata.get("page", "?")
        # 預覽片段，取前 80 字元，並將換行替換為空格
        snippet = doc.page_content[:80].replace("\n", " ")

        # 檢查：避免重複的 (filename, page) 組合
        citation_key = f"{filename}_p{page}"
        if citation_key not in citation_map:
            label = f"[{len(citations) + 1}]"
            citations.append({
                "label": label,
                "title": title,
                "source": filename,
                "page": page,
                "snippet": snippet
            })
            citation_map[citation_key] = label
        else:
            label = citation_map[citation_key]

        # context_text 累加每個 chunk 的內容，格式為 [n] title | Page n
        context_text += f"{label} {title} | Page {page}\n{doc.page_content}\n\n"

    system_prompt = f"""
    You are an experienced consultant in materials experiment design. Based on the following research proposal and related literature excerpts, please provide the researcher with a detailed set of recommended experimental procedures.

    IMPORTANT: Please provide your response in plain text format only. Do NOT use any markdown formatting, bold text, or special formatting. Use simple text with clear section headers and bullet points.

    Please include the following sections:

    SYNTHESIS PROCESS:
    Provide a step-by-step description of each experimental operation, including sequence, logic, and purpose.
    Guidelines for synthesis process:
    - Suggest specific ranges of experimental conditions (temperature, time, pressure, etc.)
    - For each reaction condition and step mentioned in the literature, cite the source ([1], [2], etc.)
    - For suggested conditions not based on literature, explain your logic clearly

    MATERIALS AND CONDITIONS:
    List the required raw materials for each step (including proportions) and the reaction conditions (temperature, time, containers).

    ANALYTICAL METHODS:
    Suggest characterization tools (such as XRD, BET, TGA) and explain the purpose of each.

    PRECAUTIONS:
    Highlight key points or parameter limitations mentioned in the literature.

    Format your response with clear section headers in CAPITAL LETTERS, followed by detailed explanations. Use simple bullet points (-) for lists.
    Use [1], [2], etc. to cite the literature sources in your response. Only cite the provided literature excerpts, numbered [1] to [{len(chunks)}] (total {len(chunks)} excerpts).

    --- literature chunks ---
    {context_text}

    --- User's Proposal ---
    {proposal_text}
    """
    return system_prompt.strip(), citations



def build_iterative_proposal_prompt(
        question: str,
        new_chunks: List[Document],
        old_chunks: List[Document],
        past_proposal: str
    ) -> Tuple[str, List[Dict]]:
    """
    Build a new research proposal prompt that combines user feedback, newly retrieved literature, old literature, and the original proposal.
    Also returns citation list.
    """
    citations = []

    def format_chunks(chunks: List[Document], label_offset=0) -> Tuple[str, List[Dict]]:
        text = ""
        local_citations = []
        for i, doc in enumerate(chunks):
            meta = doc.metadata
            title = meta.get("title", "Untitled")
            filename = meta.get("filename") or meta.get("source", "Unknown")
            page = meta.get("page_number") or meta.get("page", "?")
            snippet = doc.page_content[:80].replace("\n", " ")
            label = f"[{label_offset + i + 1}]"

            local_citations.append({
                "label": label,
                "title": title,
                "source": filename,
                "page": page,
                "snippet": snippet
            })

            text += f"{label} {title} | Page {page}\n{doc.page_content}\n\n"

        return text, local_citations

    old_text, old_citations = format_chunks(old_chunks)
    new_text, new_citations = format_chunks(new_chunks, label_offset=len(old_citations))
    citations.extend(old_citations + new_citations)

    system_prompt = f"""
    You are an experienced materials experiment design consultant. Please help modify parts of the research proposal based on user feedback, original proposal, and literature content.

    Your task is to generate a modified research proposal based on user feedback, original proposal, and literature content. The proposal should be innovative, scientifically rigorous, and feasible.

    IMPORTANT: You must respond in valid JSON format only. Do not include any text before or after the JSON object.

    The JSON must have the following structure:
    {{
        "proposal_title": "Title of the research proposal",
        "need": "Research need and current limitations",
        "solution": "Proposed design and development strategies",
        "differentiation": "Comparison with existing technologies",
        "benefit": "Expected improvements and benefits",
        "experimental_overview": "Experimental approach and methodology",
        "materials_list": ["material1", "material2", "material3"]
    }}

    Key requirements:
    1. Prioritize the areas that the user wants to modify and look for possible improvement directions from the literature
    2. Except for the areas that the user is dissatisfied with, other parts should maintain the original proposal content without changes
    3. Maintain scientific rigor, clarity, and avoid vague descriptions
    4. Use only the provided literature labels ([1], [2], etc.) for citations, and do not fabricate sources
    5. Ensure every claim is supported by a cited source or reasonable extension from the literature
    6. For materials_list, include ONLY IUPAC chemical names without any descriptions, notes, or parenthetical explanations. Each item must be a single chemical name only.

    Literature excerpts are provided below with labels from [1] to [{len(old_chunks) + len(new_chunks)}] (total {len(old_chunks) + len(new_chunks)} excerpts).
    """
    
    user_prompt = f"""
    --- User Feedback ---
    {question}

    --- Original Proposal Content ---
    {past_proposal}

    --- Literature Excerpts Based on Original Proposal ---
    {old_text}

    --- New Retrieved Excerpts Based on Feedback ---
    {new_text}
    """
    
    return system_prompt.strip(), user_prompt, citations


def generate_structured_proposal(chunks: List[Document], question: str) -> Dict[str, Any]:
    """
    生成結構化研究提案
    
    Args:
        chunks: 檢索到的文獻片段
        question: 用戶的研究問題
    
    Returns:
        Dict[str, Any]: 結構化的研究提案
    """
    # 添加調試日誌
    print(f"🔍 DEBUG: generate_structured_proposal 開始")
    print(f"🔍 DEBUG: chunks 長度: {len(chunks) if chunks else 0}")
    print(f"🔍 DEBUG: question: {question}")
    
    system_prompt, citations = build_proposal_prompt(question, chunks)
    
    # 構建用戶提示詞（包含文獻摘要）
    paper_context_text = ""
    for i, doc in enumerate(chunks):
        metadata = doc.metadata
        title = metadata.get("title", "Untitled")
        filename = metadata.get("filename") or metadata.get("source", "Unknown")
        page = metadata.get("page_number") or metadata.get("page", "?")
        
        paper_context_text += f"[{i+1}] {title} | Page {page}\n{doc.page_content}\n\n"
    
    user_prompt = f"""
    --- Literature Excerpts ---
    {paper_context_text}

    --- Research Objectives ---
    {question}
    """
    
    # 調用結構化LLM
    proposal_data = call_llm_structured_proposal(system_prompt, user_prompt)
    
    # 添加引用信息到返回結果
    if proposal_data:
        proposal_data['citations'] = citations
    
    return proposal_data


def generate_iterative_structured_proposal(
        question: str,
        new_chunks: List[Document],
        old_chunks: List[Document],
        past_proposal: str
    ) -> Dict[str, Any]:
    """
    生成迭代式結構化研究提案
    
    Args:
        question: 用戶反饋
        new_chunks: 新檢索到的文獻片段
        old_chunks: 原有的文獻片段
        past_proposal: 之前的提案內容
    
    Returns:
        Dict[str, Any]: 修改後的結構化研究提案
    """
    system_prompt, user_prompt, citations = build_iterative_proposal_prompt(
        question, new_chunks, old_chunks, past_proposal
    )
    
    # 調用結構化LLM
    proposal_data = call_llm_structured_proposal(system_prompt, user_prompt)
    
    # 添加引用信息到返回結果
    if proposal_data:
        proposal_data['citations'] = citations
    
    return proposal_data


def structured_proposal_to_text(proposal_data: Dict[str, Any]) -> str:
    """
    將結構化提案轉換為傳統文本格式
    
    Args:
        proposal_data: 結構化提案數據
    
    Returns:
        str: 格式化的文本提案
    """
    if not proposal_data:
        return ""
    
    text_parts = []
    
    # 標題
    if proposal_data.get('proposal_title'):
        text_parts.append(f"Proposal: {proposal_data['proposal_title']}\n")
    
    # Need
    if proposal_data.get('need'):
        text_parts.append("Need:\n")
        text_parts.append(f"{proposal_data['need']}\n")
    
    # Solution
    if proposal_data.get('solution'):
        text_parts.append("Solution:\n")
        text_parts.append(f"{proposal_data['solution']}\n")
    
    # Differentiation
    if proposal_data.get('differentiation'):
        text_parts.append("Differentiation:\n")
        text_parts.append(f"{proposal_data['differentiation']}\n")
    
    # Benefit
    if proposal_data.get('benefit'):
        text_parts.append("Benefit:\n")
        text_parts.append(f"{proposal_data['benefit']}\n")
    

    
    # Experimental overview
    if proposal_data.get('experimental_overview'):
        text_parts.append("Experimental overview:\n")
        text_parts.append(f"{proposal_data['experimental_overview']}\n")
    
    # Materials list
    if proposal_data.get('materials_list'):
        materials_json = json.dumps(proposal_data['materials_list'], ensure_ascii=False, indent=2)
        text_parts.append(f"```json\n{materials_json}\n```\n")
    
    return "\n".join(text_parts)


def generate_proposal_with_fallback(chunks: List[Document], question: str) -> Tuple[str, Dict[str, Any]]:
    """
    生成研究提案，優先使用結構化輸出，失敗時回退到傳統文本格式
    
    Args:
        chunks: 檢索到的文獻片段
        question: 用戶的研究問題
    
    Returns:
        Tuple[str, Dict[str, Any]]: (文本格式提案, 結構化提案數據)
    """
    # 添加詳細的調試日誌
    print(f"🔍 DEBUG: generate_proposal_with_fallback 開始")
    print(f"🔍 DEBUG: chunks 類型: {type(chunks)}")
    print(f"🔍 DEBUG: chunks 長度: {len(chunks) if chunks else 0}")
    print(f"🔍 DEBUG: question: {question}")
    
    # 驗證 chunks 的格式
    if chunks:
        print(f"🔍 DEBUG: 第一個 chunk 類型: {type(chunks[0])}")
        if hasattr(chunks[0], 'metadata'):
            print(f"🔍 DEBUG: 第一個 chunk 有 metadata 屬性")
            print(f"🔍 DEBUG: 第一個 chunk metadata: {chunks[0].metadata}")
        else:
            print(f"🔍 DEBUG: 第一個 chunk 沒有 metadata 屬性")
            print(f"🔍 DEBUG: 第一個 chunk 內容: {chunks[0]}")
    
    # 首先嘗試結構化輸出
    try:
        print("🔧 嘗試使用結構化輸出生成提案...")
        print(f"🔍 DEBUG: 調用 generate_structured_proposal 前，chunks 長度: {len(chunks)}")
        structured_proposal = generate_structured_proposal(chunks, question)
        print(f"🔍 DEBUG: generate_structured_proposal 返回: {type(structured_proposal)}")
        print(f"🔍 DEBUG: structured_proposal 內容: {structured_proposal}")
        
        if structured_proposal and all(key in structured_proposal for key in ['proposal_title', 'need', 'solution']):
            print("✅ 結構化提案生成成功")
            text_proposal = structured_proposal_to_text(structured_proposal)
            print(f"🔍 DEBUG: 生成的文本提案長度: {len(text_proposal)}")
            return text_proposal, structured_proposal
        else:
            print("⚠️ 結構化提案生成失敗或格式不完整，回退到傳統格式")
            if structured_proposal:
                print(f"🔍 DEBUG: 缺少的鍵: {[key for key in ['proposal_title', 'need', 'solution'] if key not in structured_proposal]}")
    except Exception as e:
        print(f"❌ 結構化提案生成失敗: {e}，回退到傳統格式")
        import traceback
        traceback.print_exc()
    
    # 回退到傳統文本格式
    try:
        print("🔧 使用傳統文本格式生成提案...")
        # 修復參數順序：應該是 (question, chunks) 而不是 (chunks, question)
        system_prompt, citations = build_proposal_prompt(question, chunks)
        
        # 構建完整的提示詞
        paper_context_text = ""
        for i, doc in enumerate(chunks):
            # 添加額外的類型檢查
            if not hasattr(doc, 'metadata'):
                print(f"❌ DEBUG: chunk {i} 沒有 metadata 屬性，類型: {type(doc)}")
                continue
                
            metadata = doc.metadata
            title = metadata.get("title", "Untitled")
            filename = metadata.get("filename") or metadata.get("source", "Unknown")
            page = metadata.get("page_number") or metadata.get("page", "?")
            
            paper_context_text += f"[{i+1}] {title} | Page {page}\n{doc.page_content}\n\n"
        
        full_prompt = f"{system_prompt}\n\n--- Literature Excerpts ---\n{paper_context_text}\n--- Research Objectives ---\n{question}"
        
        # 調用傳統LLM
        text_proposal = call_llm(full_prompt)
        
        # 創建一個基本的結構化數據（用於向後兼容）
        basic_structured = {
            'proposal_title': 'Generated from text format',
            'need': '',
            'solution': '',
            'differentiation': '',
            'benefit': '',
            'experimental_overview': '',
            'materials_list': [],
            'citations': citations,
            'text_format': text_proposal
        }
        
        print("✅ 傳統文本提案生成成功")
        return text_proposal, basic_structured
        
    except Exception as e:
        print(f"❌ 傳統提案生成也失敗: {e}")
        import traceback
        print(f"🔍 DEBUG: 詳細錯誤信息:")
        traceback.print_exc()
        return "", {}

def call_llm_structured_revision_proposal(question: str, new_chunks: List[Document], old_chunks: List[Document], proposal: str) -> Dict[str, Any]:
    """
    使用OpenAI Responses API的JSON structured output生成結構化修訂提案 (包含修訂說明)
    
    Args:
        question: 用戶反饋/問題
        new_chunks: 新檢索的文檔塊
        old_chunks: 原始文檔塊
        proposal: 原始提案
    
    Returns:
        Dict[str, Any]: 符合REVISION_PROPOSAL_SCHEMA的結構化修訂提案
    """
    print(f"🔍 調用結構化修訂提案LLM，用戶反饋長度：{len(question)}")
    print(f"🔍 新文檔塊數量：{len(new_chunks)}")
    print(f"🔍 原文檔塊數量：{len(old_chunks)}")
    print(f"🔍 原始提案長度：{len(proposal)} 字符")
    
    # 獲取當前使用的模型信息和參數
    try:
        from model_config_bridge import get_current_model, get_model_params
        current_model = get_current_model()
        llm_params = get_model_params()
        print(f"🤖 使用模型：{current_model}")
        print(f"🔧 模型參數：{llm_params}")
    except Exception as e:
        print(f"⚠️ 無法獲取模型信息：{e}")
        # 使用fallback配置
        current_model = "gpt-4-1106-preview"
        llm_params = {
            "model": "gpt-4-1106-preview",
            "temperature": 0.0,  # 結構化輸出使用0溫度
            "max_tokens": 4000,
            "timeout": 120,
        }
    
    try:
        # 根據模型類型選擇不同的API
        if current_model.startswith('gpt-5'):
            # GPT-5系列使用Responses API with JSON Schema
            from openai import OpenAI
            client = OpenAI()
            
            # 準備Responses API的參數
            max_tokens = llm_params.get('max_output_tokens', 4000)
            
            # 動態獲取最新的 schema
            current_schema = create_revision_proposal_schema()
            
            # 構建提示詞
            system_prompt = """
            You are an experienced materials experiment design consultant. Please help modify parts of the research proposal based on user feedback, original proposal, and literature content.

            Your task is to generate a modified research proposal based on user feedback, original proposal, and literature content. The proposal should be innovative, scientifically rigorous, and feasible.

            IMPORTANT: You must respond in valid JSON format only. Do not include any text before or after the JSON object.

            The JSON must have the following structure:
            {
                "revision_explanation": "Brief explanation of revision logic and key improvements based on user feedback",
                "proposal_title": "Title of the research proposal",
                "need": "Research need and current limitations",
                "solution": "Proposed design and development strategies",
                "differentiation": "Comparison with existing technologies",
                "benefit": "Expected improvements and benefits",
                "experimental_overview": "Experimental approach and methodology",
                "materials_list": ["material1", "material2", "material3"]
            }

            Key requirements:
            1. Prioritize the areas that the user wants to modify and look for possible improvement directions from the literature
            2. Except for the areas that the user is dissatisfied with, other parts should maintain the original proposal content without changes
            3. Maintain scientific rigor, clarity, and avoid vague descriptions
            4. Use only the provided literature labels ([1], [2], etc.) for citations, and do not fabricate sources
            5. Ensure every claim is supported by a cited source or reasonable extension from the literature
            6. For materials_list, include ONLY IUPAC chemical names without any descriptions, notes, or parenthetical explanations. Each item must be a single chemical name only.
            7. The revision_explanation should briefly explain the logic of changes and key improvements based on user feedback
            """
            
            # 構建文檔內容
            old_text = ""
            for i, doc in enumerate(old_chunks):
                metadata = doc.metadata
                title = metadata.get("title", "Untitled")
                filename = metadata.get("filename") or metadata.get("source", "Unknown")
                page = metadata.get("page_number") or metadata.get("page", "?")
                snippet = doc.page_content[:80].replace("\n", " ")
                old_text += f"    [{i+1}] {title} | Page {page}\n{snippet}\n\n"
            
            new_text = ""
            for i, doc in enumerate(new_chunks):
                metadata = doc.metadata
                title = metadata.get("title", "Untitled")
                filename = metadata.get("filename") or metadata.get("source", "Unknown")
                page = metadata.get("page_number") or metadata.get("page", "?")
                snippet = doc.page_content[:80].replace("\n", " ")
                new_text += f"    [{i+1}] {title} | Page {page}\n{snippet}\n\n"
            
            user_prompt = f"""
            --- User Feedback ---
            {question}

            --- Original Proposal Content ---
            {proposal}

            --- Literature Excerpts Based on Original Proposal ---
            {old_text}

            --- New Retrieved Excerpts Based on Feedback ---
            {new_text}
            """
            
            # 使用 Responses API + JSON Schema (適用於所有 GPT-5 系列模型)
            responses_params = {
                'model': current_model,
                'input': [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                'text': {
                    'format': {
                        'type': 'json_schema',
                        'name': 'RevisionProposal',
                        'strict': True,
                        'schema': current_schema,
                    },
                    'verbosity': 'low'  # 使用 low verbosity
                },
                'reasoning': {'effort': 'medium'},  # 使用 medium reasoning
                'max_output_tokens': max_tokens
            }
            
            print(f"🔧 使用Responses API with JSON Schema，參數：{responses_params}")
            
            # 處理GPT-5的incomplete狀態
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                response = client.responses.create(**responses_params)
                
                print(f"🔍 DEBUG: API調用完成 (嘗試 {retry_count + 1}/{max_retries})")
                print(f"🔍 DEBUG: response.status: {getattr(response, 'status', 'N/A')}")
                
                # 檢查整體response狀態
                if hasattr(response, 'status') and response.status == 'incomplete':
                    print(f"⚠️ 檢測到incomplete狀態，等待後重試...")
                    retry_count += 1
                    if retry_count < max_retries:
                        import time
                        time.sleep(2)  # 等待2秒後重試
                        continue
                    else:
                        print(f"❌ 達到最大重試次數")
                        return {}
                
                # 提取JSON內容
                try:
                    # 優先使用 resp.output_text
                    output_text = getattr(response, 'output_text', None)
                    if output_text:
                        print(f"✅ 使用 resp.output_text 提取內容: {len(output_text)} 字符")
                        try:
                            revision_data = json.loads(output_text)
                            print(f"✅ 成功解析JSON結構化修訂提案")
                            
                            # 本地驗證 schema
                            try:
                                from jsonschema import validate
                                validate(instance=revision_data, schema=current_schema)
                                print(f"✅ 本地 Schema 驗證通過")
                            except Exception as e:
                                print(f"⚠️ 本地 Schema 驗證失敗: {e}")
                            
                            return revision_data
                        except json.JSONDecodeError as e:
                            print(f"❌ JSON解析失敗: {e}")
                            print(f"❌ 原始輸出: {output_text[:500]}...")
                            retry_count += 1
                            if retry_count < max_retries:
                                continue
                            else:
                                return {}
                    
                    # 如果沒有 output_text，嘗試其他方式
                    print(f"⚠️ 沒有找到 output_text，嘗試其他方式...")
                    retry_count += 1
                    if retry_count < max_retries:
                        continue
                    else:
                        return {}
                        
                except Exception as e:
                    print(f"❌ 處理響應時發生錯誤: {e}")
                    retry_count += 1
                    if retry_count < max_retries:
                        continue
                    else:
                        return {}
            
            print(f"❌ 所有重試都失敗")
            return {}
            
        else:
            # GPT-4系列使用Chat Completions API (LangChain)
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(**llm_params)
            
            # 構建提示詞
            system_prompt = """
            You are an experienced materials experiment design consultant. Please help modify parts of the research proposal based on user feedback, original proposal, and literature content.
            """
            
            # 構建文檔內容
            old_text = ""
            for i, doc in enumerate(old_chunks):
                metadata = doc.metadata
                title = metadata.get("title", "Untitled")
                filename = metadata.get("filename") or metadata.get("source", "Unknown")
                page = metadata.get("page_number") or metadata.get("page", "?")
                snippet = doc.page_content[:80].replace("\n", " ")
                old_text += f"    [{i+1}] {title} | Page {page}\n{snippet}\n\n"
            
            new_text = ""
            for i, doc in enumerate(new_chunks):
                metadata = doc.metadata
                title = metadata.get("title", "Untitled")
                filename = metadata.get("filename") or metadata.get("source", "Unknown")
                page = metadata.get("page_number") or metadata.get("page", "?")
                snippet = doc.page_content[:80].replace("\n", " ")
                new_text += f"    [{i+1}] {title} | Page {page}\n{snippet}\n\n"
            
            full_prompt = f"{system_prompt}\n\n--- User Feedback ---\n{question}\n\n--- Original Proposal Content ---\n{proposal}\n\n--- Literature Excerpts Based on Original Proposal ---\n{old_text}\n\n--- New Retrieved Excerpts Based on Feedback ---\n{new_text}\n\nPlease provide a modified research proposal with revision explanation."
            
            response = llm.invoke(full_prompt)
            print(f"✅ 傳統LLM調用成功，回應長度：{len(response.content)} 字符")
            
            # 返回文本格式
            return {
                'revision_explanation': 'Revision based on user feedback',
                'proposal_title': 'Modified Research Proposal',
                'need': response.content,
                'solution': response.content,
                'differentiation': response.content,
                'benefit': response.content,
                'experimental_overview': response.content,
                'materials_list': ['sample_material']
            }
            
    except Exception as e:
        print(f"❌ 結構化修訂提案LLM調用失敗：{e}")
        return {}

def generate_structured_revision_explain(user_feedback: str, proposal: str) -> Dict[str, Any]:
    """
    生成結構化修訂說明的便捷函數
    
    Args:
        user_feedback: 用戶反饋
        proposal: 原始提案
    
    Returns:
        Dict[str, Any]: 結構化修訂說明
    """
    return call_llm_structured_revision_explain(user_feedback, proposal)

def generate_structured_revision_proposal(question: str, new_chunks: List[Document], old_chunks: List[Document], proposal: str) -> Dict[str, Any]:
    """
    生成結構化修訂提案的便捷函數 (包含修訂說明)
    
    Args:
        question: 用戶反饋/問題
        new_chunks: 新檢索的文檔塊
        old_chunks: 原始文檔塊
        proposal: 原始提案
    
    Returns:
        Dict[str, Any]: 結構化修訂提案 (包含修訂說明)
    """
    return call_llm_structured_revision_proposal(question, new_chunks, old_chunks, proposal)

def structured_revision_proposal_to_text(revision_data: Dict[str, Any]) -> str:
    """
    將結構化修訂提案轉換為傳統文本格式
    
    Args:
        revision_data: 結構化修訂提案數據 (包含修訂說明)
    
    Returns:
        str: 格式化的文本提案
    """
    if not revision_data:
        return ""
    
    text_parts = []
    
    # 修訂說明
    if revision_data.get('revision_explanation'):
        text_parts.append("Revision Explanation:")
        text_parts.append(f"{revision_data['revision_explanation']}\n")
    
    # 標題
    if revision_data.get('proposal_title'):
        text_parts.append(f"Proposal: {revision_data['proposal_title']}\n")
    
    # Need
    if revision_data.get('need'):
        text_parts.append("Need:\n")
        text_parts.append(f"{revision_data['need']}\n")
    
    # Solution
    if revision_data.get('solution'):
        text_parts.append("Solution:\n")
        text_parts.append(f"{revision_data['solution']}\n")
    
    # Differentiation
    if revision_data.get('differentiation'):
        text_parts.append("Differentiation:\n")
        text_parts.append(f"{revision_data['differentiation']}\n")
    
    # Benefit
    if revision_data.get('benefit'):
        text_parts.append("Benefit:\n")
        text_parts.append(f"{revision_data['benefit']}\n")
    
    # Experimental Overview
    if revision_data.get('experimental_overview'):
        text_parts.append("Experimental Overview:\n")
        text_parts.append(f"{revision_data['experimental_overview']}\n")
    
    # Materials list
    if revision_data.get('materials_list'):
        materials_json = json.dumps(revision_data['materials_list'], ensure_ascii=False, indent=2)
        text_parts.append(f"```json\n{materials_json}\n```\n")
    
    return "\n".join(text_parts)

