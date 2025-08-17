"""
RAG核心模組 - 簡化版本
========

基於檢索增強生成的AI研究助手核心功能
只支援 GPT-5 和結構化輸出
"""

import os
import json
import time
from typing import List, Dict, Any, Tuple
from pathlib import Path

# 導入必要的模組
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from chunk_embedding import get_chroma_instance
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import openai

# 導入配置和橋接模組
try:
    from .config import (
        OPENAI_API_KEY, 
        VECTOR_INDEX_DIR, 
        EMBEDDING_MODEL_NAME,
        MAX_TOKENS,
        CHUNK_SIZE,
        CHUNK_OVERLAP
    )
    from .model_config_bridge import get_model_params, get_current_model
except ImportError:
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
    """
    try:
        import sys
        backend_path = os.path.join(os.path.dirname(__file__), "..", "backend")
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)
        
        try:
            from backend.core.settings_manager import settings_manager
        except ImportError:
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

def create_experimental_detail_schema():
    """
    動態創建實驗細節的 JSON Schema
    """
    schema_params = get_dynamic_schema_params()
    
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
            },
            "materials_and_conditions": {
                "type": "string",
                "description": "使用的材料和反應條件，包括濃度、溫度、壓力等",
                "minLength": 10
            },
            "analytical_methods": {
                "type": "string",
                "description": "分析方法和表徵技術，如XRD、SEM、NMR等",
                "minLength": 10
            },
            "precautions": {
                "type": "string",
                "description": "實驗注意事項和安全預防措施",
                "minLength": 10
            }
        }
    }

def create_revision_explain_schema():
    """
    動態創建修訂說明的 JSON Schema
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
            }
        }
    }

def create_revision_proposal_schema():
    """
    動態創建修訂提案的 JSON Schema (包含修訂說明)
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

# ==================== 向量數據庫管理 ====================

def load_paper_vectorstore():
    """
    載入文獻向量數據庫
    """
    return get_chroma_instance("paper")

def load_experiment_vectorstore():
    """
    載入實驗數據向量數據庫
    """
    return get_chroma_instance("experiment")

# ==================== 文檔檢索功能 ====================

def retrieve_chunks_multi_query(
    vectorstore, query_list: List[str], k: int = 10, fetch_k: int = 20, score_threshold: float = 0.35
    ) -> List[Document]:
    """
    多查詢文檔檢索功能
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

# ==================== LLM 調用功能 ====================

def call_llm(prompt: str) -> str:
    """
    調用 LLM 生成文本 - 只支援 GPT-5
    """
    print(f"🔍 調用 LLM，提示詞長度：{len(prompt)} 字符")
    
    # 獲取當前使用的模型信息和參數
    try:
        from model_config_bridge import get_current_model, get_model_params
        current_model = get_current_model()
        llm_params = get_model_params()
        print(f"🤖 使用模型：{current_model}")
        print(f"🔧 模型參數：{llm_params}")
    except Exception as e:
        print(f"❌ 無法獲取模型信息：{e}")
        raise Exception(f"無法獲取模型信息：{str(e)}")
    
    try:
        # 只支援 GPT-5 系列使用 Responses API
        if not current_model.startswith('gpt-5'):
            raise Exception(f"不支援的模型：{current_model}，只支援 GPT-5 系列")
            
        from openai import OpenAI
        client = OpenAI()
        
        # 準備Responses API的參數
        max_tokens = llm_params.get('max_output_tokens', llm_params.get('max_tokens', 2000))
        print(f"🔧 使用設定的max_output_tokens: {max_tokens}")
        
        responses_params = {
            'model': current_model,
            'input': [{'role': 'user', 'content': prompt}],
            'max_output_tokens': max_tokens
        }
        
        # 添加其他參數
        for key, value in llm_params.items():
            if key not in ['model', 'input', 'max_output_tokens', 'max_tokens', 'verbosity', 'reasoning_effort']:
                responses_params[key] = value
        
        # 特殊處理verbosity和reasoning_effort
        if 'text' in llm_params:
            responses_params['text'] = llm_params['text']
        if 'reasoning' in llm_params:
            responses_params['reasoning'] = llm_params['reasoning']
        
        print(f"🔧 使用Responses API，參數：{responses_params}")
        
        # 處理GPT-5的incomplete狀態
        max_retries = 3
        retry_count = 0
        current_max_tokens = max_tokens
        
        while retry_count < max_retries:
            if retry_count > 0:
                current_max_tokens += 1500
                responses_params['max_output_tokens'] = current_max_tokens
                print(f"🔄 重試 {retry_count}：提高max_output_tokens到 {current_max_tokens}")
            
            response = client.responses.create(**responses_params)
            
            # 檢查整體response狀態
            if hasattr(response, 'status') and response.status == 'incomplete':
                print(f"⚠️ 檢測到incomplete狀態，等待後重試...")
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(2)
                    continue
                else:
                    print(f"❌ 達到最大重試次數")
            
            # 提取文本內容（只使用 output_text）
            if getattr(response, "output_text", None):
                txt = response.output_text.strip()
                if txt:
                    print(f"✅ 使用 output_text: {len(txt)} 字符")
                    print(f"✅ LLM 調用成功，回應長度：{len(txt)} 字符")
                    return txt
                else:
                    print(f"❌ output_text 為空")
                    retry_count += 1
                    if retry_count < max_retries:
                        continue
                    else:
                        print(f"❌ 達到最大重試次數")
                        return ""
            else:
                print(f"❌ 無法提取 output_text")
                retry_count += 1
                if retry_count < max_retries:
                    continue
                else:
                    print(f"❌ 達到最大重試次數")
                    return ""
        
        print(f"❌ 所有重試都失敗，返回空字符串")
        return ""
        
    except Exception as e:
        print(f"❌ LLM 調用失敗：{e}")
        raise Exception(f"LLM 調用失敗：{str(e)}")

def call_llm_structured_proposal(system_prompt: str, user_prompt: str) -> Dict[str, Any]:
    """
    使用OpenAI Responses API的JSON structured output生成結構化研究提案
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
        print(f"❌ 無法獲取模型信息：{e}")
        raise Exception(f"無法獲取模型信息：{str(e)}")
    
    try:
        # 只支援 GPT-5 系列使用 Responses API
        if not current_model.startswith('gpt-5'):
            raise Exception(f"不支援的模型：{current_model}，只支援 GPT-5 系列")
            
        from openai import OpenAI
        client = OpenAI()
        
        # 準備Responses API的參數
        max_tokens = llm_params.get('max_output_tokens', llm_params.get('max_tokens', 4000))
        
        # 動態獲取最新的 schema
        current_schema = create_research_proposal_schema()
        
        # 使用 Responses API + JSON Schema
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
                'verbosity': 'low'
            },
            'reasoning': {'effort': 'medium'},
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
                    time.sleep(2)
                    continue
                else:
                    print(f"❌ 達到最大重試次數")
                    return {}
            
            # 提取JSON內容
            try:
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
                        
                        return proposal_data
                    except json.JSONDecodeError as e:
                        print(f"⚠️ JSON解析失敗: {e}")
                        print(f"⚠️ 嘗試的文本: {output_text[:200]}...")
                        return {}
                
                # 如果沒有找到JSON內容
                print(f"⚠️ 無法從Responses API提取JSON內容")
                return {}
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析失敗: {e}")
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(2)
                    continue
                else:
                    print(f"❌ 達到最大重試次數")
                    return {}
            except Exception as e:
                print(f"❌ 提取JSON內容失敗: {e}")
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(2)
                    continue
                else:
                    print(f"❌ 達到最大重試次數")
                    return {}
        
        print(f"❌ 所有重試都失敗，返回空字典")
        return {}
        
    except Exception as e:
        print(f"❌ 結構化LLM調用失敗：{e}")
        raise Exception(f"結構化LLM調用失敗：{str(e)}")

# ==================== 提示詞構建功能 ====================

def build_prompt(chunks: List[Document], question: str) -> Tuple[str, List[Dict]]:
    """
    構建提示詞
    """
    context_text = ""
    citations = []
    citation_map = {}
    
    for i, doc in enumerate(chunks):
        metadata = doc.metadata
        title = metadata.get("title", "Untitled")
        filename = metadata.get("filename") or metadata.get("source", "Unknown")
        page = metadata.get("page_number") or metadata.get("page", "?")
        snippet = doc.page_content[:80].replace("\n", " ")

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
    You are a research literature search assistant. Please answer questions based only on the provided literature excerpts.
    Please use [1], [2], etc. to cite paragraph sources in your answers, and do not repeat the sources at the end.
    If the paragraphs mention specific experimental conditions (temperature, time, etc.), please be sure to include them in your answer.
    Important: You can only cite the provided literature excerpts. The current literature excerpt numbers are [1] to [{len(chunks)}] (total {len(chunks)} excerpts)

    --- Literature Summary ---
    {context_text}

    --- Question ---
    {question}
    """
    return system_prompt.strip(), citations

def expand_query(user_prompt: str) -> List[str]:
    """
    將用戶輸入的自然語言問題轉換為多個語義搜索查詢語句
    """
    try:
        from model_config_bridge import get_current_model, get_model_params
        current_model = get_current_model()
        llm_params = get_model_params()
    except Exception as e:
        print(f"❌ 無法獲取模型參數：{e}")
        raise Exception(f"無法獲取模型參數：{str(e)}")

    system_prompt = """You are a scientific assistant helping expand a user's synthesis question into multiple semantic search queries. 
    Each query should be precise, relevant, and useful for retrieving related technical documents. 
    Only return a list of 3 to 6 search queries in English. Do not explain, do not include numbering if not needed."""

    full_prompt = f"{system_prompt}\n\nUser question:\n{user_prompt}"

    try:
        # 只支援 GPT-5 系列使用 Responses API
        if not current_model.startswith('gpt-5'):
            raise Exception(f"不支援的模型：{current_model}，只支援 GPT-5 系列")
            
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
        
        # 移除reasoning參數，避免返回ResponseReasoningItem
        if 'reasoning' in responses_params:
            del responses_params['reasoning']
        
        response = client.responses.create(**responses_params)
        
        # 提取輸出
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
                    output += item.text
                elif hasattr(item, "message"):
                    if hasattr(item.message, "content"):
                        output += item.message.content
                    else:
                        output += str(item.message)
                else:
                    item_str = str(item)
                    if not item_str.startswith('ResponseReasoningItem'):
                        output += item_str
        
        output = output.strip()
        
        # 嘗試解析為查詢列表
        if output.startswith("[") and output.endswith("]"):
            try:
                import ast
                return ast.literal_eval(output)
            except Exception:
                pass

        queries = [line.strip("-• ").strip() for line in output.split("\n") if line.strip()]
        return [q for q in queries if len(q) > 4]
        
    except Exception as e:
        print(f"❌ 查詢擴展失敗：{e}")
        raise Exception(f"查詢擴展失敗：{str(e)}")

def build_proposal_prompt(question: str, chunks: List[Document]) -> Tuple[str, List[Dict]]:
    """
    構建提案生成提示詞
    """
    paper_context_text = ""
    citations = []
    citation_map = {}

    for i, doc in enumerate(chunks):
        meta = doc.metadata
        title = meta.get("title", "Untitled")
        filename = meta.get("filename") or meta.get("source", "Unknown")
        page = meta.get("page_number") or meta.get("page", "?")
        snippet = doc.page_content[:80].replace("\n", " ")
        
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

# ==================== 提案生成功能 ====================

def generate_structured_proposal(chunks: List[Document], question: str) -> Dict[str, Any]:
    """
    生成結構化研究提案
    """
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

def structured_proposal_to_text(proposal_data: Dict[str, Any]) -> str:
    """
    將結構化提案轉換為傳統文本格式
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

# ==================== 主要接口函數 ====================

def generate_proposal(chunks: List[Document], question: str) -> Tuple[str, Dict[str, Any]]:
    """
    生成研究提案 - 只支援結構化輸出
    """
    print(f"🔍 DEBUG: generate_proposal 開始")
    print(f"🔍 DEBUG: chunks 長度: {len(chunks) if chunks else 0}")
    print(f"🔍 DEBUG: question: {question}")
    
    try:
        print("🔧 使用結構化輸出生成提案...")
        structured_proposal = generate_structured_proposal(chunks, question)
        print(f"🔍 DEBUG: generate_structured_proposal 返回: {type(structured_proposal)}")
        
        if structured_proposal and all(key in structured_proposal for key in ['proposal_title', 'need', 'solution']):
            print("✅ 結構化提案生成成功")
            text_proposal = structured_proposal_to_text(structured_proposal)
            print(f"🔍 DEBUG: 生成的文本提案長度: {len(text_proposal)}")
            return text_proposal, structured_proposal
        else:
            print("❌ 結構化提案生成失敗或格式不完整")
            if structured_proposal:
                print(f"🔍 DEBUG: 缺少的鍵: {[key for key in ['proposal_title', 'need', 'solution'] if key not in structured_proposal]}")
            raise Exception("結構化提案生成失敗")
            
    except Exception as e:
        print(f"❌ 提案生成失敗: {e}")
        raise Exception(f"提案生成失敗: {str(e)}")

# ==================== 其他功能函數 ====================

def build_inference_prompt(chunks: List[Document], question: str) -> Tuple[str, List[Dict]]:
    """
    構建推理提示詞
    """
    context_text = ""
    citations = []
    citation_map = {}
    
    for i, doc in enumerate(chunks):
        meta = doc.metadata
        title = meta.get("title", "Untitled")
        filename = meta.get("filename") or meta.get("source", "Unknown")
        page = meta.get("page_number") or meta.get("page", "?")
        snippet = doc.page_content[:80].replace("\n", " ")
        
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
    """
    構建雙重推理提示詞
    """
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
            "page": "-",
            "snippet": snippet,
            "type": "experiment"
        })

        exp_context_text += f"{label} Experiment {exp_id}\n{doc.page_content}\n\n"
        label_index += 1
        
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
