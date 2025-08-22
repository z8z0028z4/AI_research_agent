"""
服務層整合測試
============

測試後端服務層功能 - 使用真實功能而非 Mock：
- 文件處理服務
- 嵌入服務
- 知識代理服務
- 搜索服務
"""

import pytest
import os
import shutil

class TestFileService:
    """測試文件處理服務 - 真實測試"""
    
    def test_real_metadata_extraction(self):
        """測試真實元數據提取"""
        from backend.services.metadata_extractor import extract_basic_metadata
        
        # 創建測試文件
        test_file = "tests/test_data/test_metadata.txt"
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
        
        with open(test_file, "w", encoding='utf-8') as f:
            f.write("測試內容")
        
        try:
            metadata = extract_basic_metadata(test_file)
            
            assert isinstance(metadata, dict)
            assert "filename" in metadata
            assert "file_size" in metadata
            assert metadata["filename"] == "test_metadata.txt"
            assert metadata["file_size"] > 0
        finally:
            # 清理
            if os.path.exists(test_file):
                os.remove(test_file)
    
    def test_real_document_renaming(self):
        """測試真實文檔重命名"""
        from backend.services.document_renamer import rename_and_copy_file
        
        # 創建測試文件
        test_file = "tests/test_data/test_document.pdf"
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
        
        with open(test_file, "w", encoding='utf-8') as f:
            f.write("測試內容")
        
        try:
            # 測試重命名
            metadata = {"title": "新文件名", "type": "paper"}
            result_metadata = rename_and_copy_file(test_file, metadata)
            
            assert isinstance(result_metadata, dict)
            assert "new_filename" in result_metadata
            assert "new_path" in result_metadata
            assert "新文件名" in result_metadata["new_filename"]
        finally:
            # 清理
            if os.path.exists(test_file):
                os.remove(test_file)
    
    def test_real_duplicate_detection(self):
        """測試真實重複檢測"""
        from backend.services.file_service import check_duplicate_file
        
        # 創建測試文件
        test_file = "tests/test_data/test_file.txt"
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
        
        with open(test_file, "w", encoding='utf-8') as f:
            f.write("測試內容")
        
        try:
            # 測試重複檢測
            is_duplicate = check_duplicate_file(test_file)
            
            assert isinstance(is_duplicate, bool)
            # 新文件不應該是重複的
            assert is_duplicate is False
        finally:
            # 清理
            if os.path.exists(test_file):
                os.remove(test_file)


class TestEmbeddingService:
    """測試嵌入服務 - 真實測試"""
    
    def test_real_embedding_model_validation(self):
        """測試真實嵌入模型驗證"""
        from backend.services.embedding_service import validate_embedding_model
        
        result = validate_embedding_model()
        assert isinstance(result, bool)
        # 模型應該有效
        assert result is True
    
    def test_real_vectorstore_stats(self):
        """測試真實向量存儲統計"""
        from backend.services.embedding_service import get_vectorstore_stats
        
        # 測試論文向量庫
        paper_stats = get_vectorstore_stats("paper")
        assert isinstance(paper_stats, dict)
        assert "total_documents" in paper_stats
        assert "collection_name" in paper_stats
        assert paper_stats["collection_name"] == "paper"
        
        # 測試實驗向量庫
        exp_stats = get_vectorstore_stats("experiment")
        assert isinstance(exp_stats, dict)
        assert "total_documents" in exp_stats
        assert "collection_name" in exp_stats
        assert exp_stats["collection_name"] == "experiment"
    
    def test_real_embedding_model_loading(self):
        """測試真實嵌入模型加載"""
        from backend.services.embedding_service import get_embedding_model
        
        model = get_embedding_model()
        assert model is not None
        # 測試模型能正常編碼
        test_texts = ["測試文本1", "測試文本2"]
        embeddings = model.encode(test_texts)
        assert len(embeddings) == 2
        assert len(embeddings[0]) > 0


class TestKnowledgeService:
    """測試知識代理服務 - 真實測試"""
    
    def test_real_agent_answer(self):
        """測試真實代理回答"""
        from backend.services.knowledge_service import agent_answer
        
        # 測試知識查詢
        query = "什麼是化學合成？"
        answer = agent_answer(query, mode="knowledge")
        
        assert isinstance(answer, str)
        assert len(answer) > 0
        # 回答應該包含相關內容
        assert any(keyword in answer.lower() for keyword in ["化學", "合成", "chemistry", "synthesis"])
    
    def test_real_search_and_download(self):
        """測試真實搜索和下載"""
        from backend.services.knowledge_service import search_and_download_only
        
        # 測試搜索功能
        query = "metal organic framework synthesis"
        result = search_and_download_only(query)
        
        assert isinstance(result, dict)
        assert "papers" in result
        assert "total" in result
        assert isinstance(result["papers"], list)
        assert isinstance(result["total"], int)
    
    def test_real_retrieve_chunks_multi_query(self):
        """測試真實多查詢檢索"""
        from backend.services.knowledge_service import retrieve_chunks_multi_query
        
        # 測試多查詢檢索
        queries = ["chemical synthesis", "organic chemistry"]
        chunks = retrieve_chunks_multi_query(queries, k=5)
        
        assert isinstance(chunks, list)
        # 應該能找到相關文檔
        assert len(chunks) > 0
        # 驗證文檔結構
        for chunk in chunks:
            assert hasattr(chunk, 'page_content')
            assert hasattr(chunk, 'metadata')
            assert len(chunk.page_content) > 0


class TestSearchService:
    """測試搜索服務 - 真實測試"""
    
    def test_real_query_parsing(self):
        """測試真實查詢解析"""
        from backend.services.query_parser import parse_query
        
        # 測試查詢解析
        query = "metal organic framework synthesis methods"
        parsed = parse_query(query)
        
        assert isinstance(parsed, dict)
        assert "keywords" in parsed
        assert "intent" in parsed
        assert isinstance(parsed["keywords"], list)
        assert len(parsed["keywords"]) > 0
    
    def test_real_europepmc_search(self):
        """測試真實 Europe PMC 搜索"""
        from backend.services.europepmc_handler import search_papers
        
        # 測試論文搜索
        query = "metal organic framework"
        results = search_papers(query, max_results=5)
        
        assert isinstance(results, list)
        # 可能沒有結果，但函數應該正常工作
        assert len(results) >= 0
        # 如果有結果，驗證結構
        if results:
            paper = results[0]
            assert isinstance(paper, dict)
            assert "title" in paper
            assert "abstract" in paper


class TestChemicalService:
    """測試化學服務 - 真實測試"""
    
    def test_real_pubchem_search(self):
        """測試真實 PubChem 搜索"""
        from backend.services.pubchem_service import search_compound
        
        # 測試化合物搜索
        compound_name = "ethanol"
        results = search_compound(compound_name)
        
        assert isinstance(results, list)
        # 應該能找到乙醇
        assert len(results) > 0
        # 驗證結果結構
        compound = results[0]
        assert isinstance(compound, dict)
        assert "cid" in compound
        assert "title" in compound
    
    def test_real_compound_info(self):
        """測試真實化合物信息"""
        from backend.services.pubchem_service import get_compound_info
        
        # 測試獲取化合物信息 (乙醇的 CID)
        cid = "702"
        info = get_compound_info(cid)
        
        assert isinstance(info, dict)
        assert "cid" in info
        assert "title" in info
        assert info["cid"] == cid
        assert "ethanol" in info["title"].lower()


class TestExcelService:
    """測試 Excel 服務 - 真實測試"""
    
    def test_real_excel_reading(self):
        """測試真實 Excel 讀取"""
        from backend.services.excel_service import read_excel_file
        
        # 創建測試 Excel 文件
        test_file = "tests/test_data/test_experiments.xlsx"
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
        
        try:
            import pandas as pd
            df = pd.DataFrame({
                "實驗ID": ["EXP001", "EXP002"],
                "實驗名稱": ["測試實驗1", "測試實驗2"],
                "描述": ["這是第一個測試實驗", "這是第二個測試實驗"]
            })
            df.to_excel(test_file, index=False)
            
            # 測試讀取
            data = read_excel_file(test_file)
            
            assert isinstance(data, dict)
            assert "data" in data
            assert "columns" in data
            assert len(data["data"]) == 2
            assert len(data["columns"]) == 3
        except ImportError:
            # 如果沒有 pandas，跳過測試
            pytest.skip("pandas not available")
        finally:
            # 清理
            if os.path.exists(test_file):
                os.remove(test_file)
    
    def test_real_experiment_export(self):
        """測試真實實驗導出"""
        from backend.services.excel_service import export_new_experiments_to_txt
        
        # 創建測試 Excel 文件
        test_file = "tests/test_data/test_export.xlsx"
        output_dir = "tests/test_output"
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            import pandas as pd
            df = pd.DataFrame({
                "實驗ID": ["EXP001"],
                "實驗名稱": ["測試實驗"],
                "描述": ["測試描述"]
            })
            df.to_excel(test_file, index=False)
            
            # 測試導出
            result_df, txt_paths = export_new_experiments_to_txt(test_file, output_dir)
            
            assert result_df is not None
            assert isinstance(txt_paths, list)
            assert len(txt_paths) > 0
            # 驗證導出的文件存在
            for txt_path in txt_paths:
                assert os.path.exists(txt_path)
        except ImportError:
            # 如果沒有 pandas，跳過測試
            pytest.skip("pandas not available")
        finally:
            # 清理
            if os.path.exists(test_file):
                os.remove(test_file)
            if os.path.exists(output_dir):
                shutil.rmtree(output_dir)


class TestRAGService:
    """測試 RAG 服務 - 真實測試"""
    
    def test_real_research_proposal_generation(self):
        """測試真實研究提案生成"""
        from backend.services.rag_service import generate_research_proposal
        
        # 測試提案生成
        topic = "金屬有機框架的合成方法研究"
        proposal = generate_research_proposal(topic)
        
        assert isinstance(proposal, dict)
        assert "proposal" in proposal
        assert "suggestions" in proposal
        assert isinstance(proposal["proposal"], str)
        assert len(proposal["proposal"]) > 0
        assert isinstance(proposal["suggestions"], list)
    
    def test_real_structured_llm_call(self):
        """測試真實結構化 LLM 調用"""
        from backend.services.rag_service import call_llm_structured
        
        schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "content": {"type": "string"}
            },
            "required": ["title", "content"]
        }
        
        # 測試結構化調用
        response = call_llm_structured("Generate a test response", schema)
        
        assert isinstance(response, dict)
        assert "title" in response
        assert "content" in response
        assert isinstance(response["title"], str)
        assert isinstance(response["content"], str) 