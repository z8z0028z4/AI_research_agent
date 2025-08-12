"""
AI 研究助理 - RAG核心模塊
========================

這個模塊是整個系統的RAG（檢索增強生成）核心，負責：
1. 向量數據庫管理
2. 文檔檢索和相似度搜索
3. 提示詞構建和優化
4. LLM調用和回答生成

架構說明：
- 使用Chroma作為向量數據庫
- 支持多查詢檢索
- 提供多種提示詞模板
- 集成OpenAI GPT模型

⚠️ 注意：此模塊是系統的核心組件，所有知識處理都依賴於此模塊
"""

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain.chat_models import ChatOpenAI
from config import VECTOR_INDEX_DIR, EMBEDDING_MODEL_NAME, LLM_MODEL_NAME
import pandas as pd
from typing import List, Tuple, Dict
import os
from collections import defaultdict

# Embedding model configuration

# ==================== 向量數據庫管理 ====================

def load_paper_vectorstore():
    """
    載入文獻向量數據庫
    
    功能：
    1. 初始化嵌入模型
    2. 連接文獻向量存儲
    3. 返回可用的向量數據庫對象
    
    返回：
        Chroma: 文獻向量數據庫對象
    
    技術細節：
    - 使用HuggingFace嵌入模型
    - 持久化存儲在paper_vector目錄
    - 集合名稱為"paper"
    """
    # Load Nomic embedding model
    try:
        print(f"🔧 Loading Nomic embedding model: {EMBEDDING_MODEL_NAME}")
        embedding_model = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            model_kwargs={"trust_remote_code": True},
            encode_kwargs={"normalize_embeddings": True}
        )
        print("✅ Nomic embedding model loaded successfully")
    except Exception as e:
        print(f"❌ Nomic embedding failed: {e}")
        raise e
    
    paper_vector_dir = os.path.join(VECTOR_INDEX_DIR, "paper_vector")
    vectorstore = Chroma(
        persist_directory=paper_vector_dir,
        embedding_function=embedding_model, 
        collection_name="paper"
        )
    return vectorstore


def load_experiment_vectorstore():
    """
    載入實驗數據向量數據庫
    
    功能：
    1. 初始化嵌入模型
    2. 連接實驗數據向量存儲
    3. 返回可用的向量數據庫對象
    
    返回：
        Chroma: 實驗數據向量數據庫對象
    
    技術細節：
    - 使用相同的嵌入模型確保一致性
    - 持久化存儲在experiment_vector目錄
    - 集合名稱為"experiment"
    """
    # Load Nomic embedding model
    try:
        print(f"🔧 Loading Nomic embedding model: {EMBEDDING_MODEL_NAME}")
        embedding_model = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            model_kwargs={"trust_remote_code": True},
            encode_kwargs={"normalize_embeddings": True}
        )
        print("✅ Nomic embedding model loaded successfully")
    except Exception as e:
        print(f"❌ Nomic embedding failed: {e}")
        raise e
    experiment_vector_dir = os.path.join(VECTOR_INDEX_DIR, "experiment_vector")
    vectorstore = Chroma(
        persist_directory=experiment_vector_dir, 
        embedding_function=embedding_model, 
        collection_name="experiment"
        )
    return vectorstore


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
    chunk_dict = defaultdict(float)
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

def build_prompt(chunks: List[Document], question: str) -> Tuple[str, List[Dict]]:
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
            # 對於複雜的proposal prompt，使用更高的token限制
            base_max_tokens = llm_params.get('max_output_tokens', 2000)
            if len(prompt) > 1000:  # 複雜prompt
                max_tokens = max(base_max_tokens, 8000)  # 大幅提高到8000 tokens
                print(f"🔧 檢測到複雜prompt，大幅提高max_output_tokens到: {max_tokens}")
            else:
                max_tokens = base_max_tokens
            
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
            
            while retry_count < max_retries:
                response = client.responses.create(**responses_params)
                
                print(f"🔍 DEBUG: API調用完成 (嘗試 {retry_count + 1}/{max_retries})")
                print(f"🔍 DEBUG: response 類型: {type(response)}")
                print(f"🔍 DEBUG: response.status: {getattr(response, 'status', 'N/A')}")
                
                # 檢查整體response狀態
                if hasattr(response, 'status') and response.status == 'incomplete':
                    print(f"⚠️ 檢測到incomplete狀態，等待後重試...")
                    print(f"💡 提示：如果持續遇到incomplete狀態，建議在設置頁面提高max_output_tokens參數")
                    print(f"💡 當前max_output_tokens: {max_tokens}，建議提高到8000-12000")
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
                            print(f"💡 建議：請在設置頁面將max_output_tokens提高到8000-12000，或降低verbosity設置")
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
                            print(f"💡 建議：請在設置頁面將max_output_tokens提高到8000-12000，或降低verbosity設置")
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


def build_proposal_prompt(chunks: List[Document], question: str) -> Tuple[str, List[Dict]]:
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

If possible, propose new components, structures, or mechanisms (e.g., new ligands, frameworks, catalysts, processing techniques) based on the literature, and clearly explain their structural or functional advantages and potential reactivity/performance.

Write a structured proposal based on the provided literature excerpts and research objectives in the following format (complete each section):

Proposal: (Automatically generate a proposal title summarizing research objectives and innovation points)

Need:

Briefly describe the research objectives and current limitations in existing solutions

Clearly identify the pain points or technical bottlenecks that need to be addressed at industry, academic, or global level

Solution:

Propose specific design and development strategies

Suggest new structures, compositions, or methods, clearly naming the proposed elements (e.g., chemical names, material systems, fabrication methods)

Explain the logic behind the proposed design (e.g., structure-property relationship, mechanism of action, processing advantages)

Differentiation:

Compare with existing literature or technologies

Emphasize breakthroughs in structure, performance, or implementation

Benefit:

Expected improvements in performance or application scope

Provide quantitative estimates if possible (e.g., % improvement, target metrics)

Based Literature:

Use paragraph labels to cite sources, with labels from [1] to [{len(chunks)}] (total {len(chunks)} excerpts)

Ensure every claim is supported by a cited source or reasonable extension from the literature

Experimental overview:

Starting materials/components and conditions (e.g., temperature, duration, environment)

Instruments/equipment description and list

Step-by-step description of the procedure (highlighting key logic and rationale)

Finally, list all materials/chemicals used in this proposal (including metals, ligands, solvents, or other relevant reagents) in JSON format at the end of your answer. Use IUPAC names where applicable.
Example:

```json
["formic acid", "N,N-dimethylformamide", "copper;dinitrate;trihydrate"]
Notes:

All proposed designs must have a logical basis — avoid inventing unreasonable structures without justification

Maintain scientific rigor, clarity, and avoid vague descriptions

Use only the provided literature labels ([1], [2], etc.) for citations, and do not fabricate sources

    --- Literature Excerpts ---
    {paper_context_text}

    --- Research Objectives ---
    {question}"""
    
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

    Please follow these guidelines:
    1. Prioritize the areas that the user wants to modify and look for possible improvement directions from the literature.
    2. Except for the areas that the user is dissatisfied with, other parts (NSDB) should maintain the original proposal content without changes, output directly.
    3. Maintain the proposal format consistent with the original proposal content, and please briefly explain the direction of changes in the first paragraph, including the following sections:
    - revision explanation: Briefly explain the differences between this proposal and the previous proposal
    - Need
    - Solution
    - Differentiation
    - Benefit
    - Based Literature
    - Experimental overview
    Important: You can only cite the provided literature excerpts. The current literature excerpt numbers are [1] to [{len(old_chunks) + len(new_chunks)}] (total {len(old_chunks) + len(new_chunks)} excerpts)

    Finally, please list all chemicals used in this proposal (including metal salts, organic ligands, solvents, etc.) in JSON format at the end of your answer. Answer with IUPAC names, format and example as follows:

    ```json
    ["formic acid", "N,N-dimethylformamide", "copper;dinitrate;trihydrate"]
    --- User Feedback ---
    {question}

    --- Original Proposal Content ---
    {past_proposal}

    --- Literature Excerpts Based on Original Proposal ---
    {old_text}

    --- New Retrieved Excerpts Based on Feedback ---
    {new_text}
    """
    return system_prompt.strip(), citations

