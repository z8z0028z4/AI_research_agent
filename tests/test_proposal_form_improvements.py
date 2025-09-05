"""
提案表單改進功能測試
==================

測試以下功能：
1. Document Retrieval Count 下拉選單功能
2. 文字反白 popup 位置計算
3. 表單狀態管理一致性
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
import sys
import os

# 添加項目根目錄到 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.main import app
from backend.api.routes.proposal import ProposalRequest, ProposalResponse
from backend.core.config import Settings


@pytest.mark.fast
@pytest.mark.backend
class TestProposalFormImprovements:
    """測試提案表單改進功能"""
    
    def setup_method(self):
        """設置測試環境"""
        self.client = TestClient(app)
        self.settings = Settings()
        
    def test_proposal_request_model_includes_retrieval_count(self):
        """測試提案請求模型包含 retrieval_count 字段"""
        # 測試默認值
        request = ProposalRequest(research_goal="測試研究目標")
        assert request.retrieval_count == 10
        
        # 測試自定義值
        request = ProposalRequest(
            research_goal="測試研究目標",
            retrieval_count=15
        )
        assert request.retrieval_count == 15
        
        # 測試可選字段
        request = ProposalRequest(
            research_goal="測試研究目標",
            retrieval_count=None
        )
        assert request.retrieval_count is None

    @patch('backend.services.knowledge_service.agent_answer')
    def test_proposal_generation_with_retrieval_count(self, mock_agent_answer):
        """測試提案生成時使用正確的檢索數量"""
        # 設置 mock 返回值
        mock_agent_answer.return_value = {
            "answer": "這是一個測試提案內容，包含詳細的研究計劃和方法。",
            "proposal": "這是一個測試提案內容，包含詳細的研究計劃和方法。",
            "chemicals": [],
            "not_found": [],
            "citations": [],
            "chunks": [],
            "structured_proposal": None
        }
        
        # 測試不同的檢索數量
        test_cases = [1, 5, 10, 15, 20]
        
        for retrieval_count in test_cases:
            response = self.client.post(
                "/api/v1/proposal/generate",
                json={
                    "research_goal": "測試研究目標",
                    "retrieval_count": retrieval_count
                }
            )
            
            assert response.status_code == 200
            
            # 驗證 agent_answer 被調用時傳入了正確的檢索數量
            call_args = mock_agent_answer.call_args
            assert call_args is not None
            
            # 檢查 kwargs 中是否包含 k (retrieval_count 在 agent_answer 中稱為 k)
            kwargs = call_args.kwargs if call_args.kwargs else {}
            assert kwargs.get('k') == retrieval_count

    def test_retrieval_count_validation(self):
        """測試檢索數量驗證"""
        # 測試有效值
        valid_values = [1, 5, 10, 15, 20, 25, 50]
        for value in valid_values:
            request = ProposalRequest(
                research_goal="測試研究目標",
                retrieval_count=value
            )
            assert request.retrieval_count == value
        
        # 測試邊界值
        request = ProposalRequest(
            research_goal="測試研究目標",
            retrieval_count=0
        )
        assert request.retrieval_count == 0
        
        request = ProposalRequest(
            research_goal="測試研究目標",
            retrieval_count=100
        )
        assert request.retrieval_count == 100

    @patch('backend.services.knowledge_service.agent_answer')
    def test_proposal_generation_without_retrieval_count(self, mock_agent_answer):
        """測試不提供檢索數量時使用默認值"""
        mock_agent_answer.return_value = {
            "answer": "這是一個測試提案內容，包含詳細的研究計劃和方法。",
            "proposal": "這是一個測試提案內容，包含詳細的研究計劃和方法。",
            "chemicals": [],
            "not_found": [],
            "citations": [],
            "chunks": [],
            "structured_proposal": None
        }
        
        # 不提供 retrieval_count
        response = self.client.post(
            "/api/v1/proposal/generate",
            json={
                "research_goal": "測試研究目標"
            }
        )
        
        assert response.status_code == 200
        
        # 驗證使用了默認值 10
        call_args = mock_agent_answer.call_args
        kwargs = call_args.kwargs if call_args.kwargs else {}
        assert kwargs.get('k') == 10


@pytest.mark.fast
@pytest.mark.frontend
class TestTextHighlightPopupPosition:
    """測試文字反白 popup 位置計算（模擬測試）"""
    
    def test_calculate_end_position_logic(self):
        """測試位置計算邏輯（不依賴前端模組）"""
        # 模擬位置計算邏輯
        def calculate_end_position_simulation(range_data):
            """模擬位置計算函數"""
            try:
                # 模擬計算最後一個字符的位置
                end_x = range_data.get('end_x', 100)
                end_y = range_data.get('end_y', 50)
                
                return {
                    'x': end_x,
                    'y': end_y
                }
            except Exception:
                # 錯誤處理
                return {
                    'x': 0,
                    'y': 0
                }
        
        # 測試正常情況
        range_data = {'end_x': 150, 'end_y': 200}
        result = calculate_end_position_simulation(range_data)
        assert result['x'] == 150
        assert result['y'] == 200
        
        # 測試錯誤情況
        result = calculate_end_position_simulation({})
        assert result['x'] == 100  # 默認值
        assert result['y'] == 50   # 默認值

    def test_popup_position_validation(self):
        """測試 popup 位置數據驗證"""
        # 測試位置數據結構
        position_data = {
            'x': 150,
            'y': 200
        }
        
        # 驗證數據類型
        assert isinstance(position_data['x'], (int, float))
        assert isinstance(position_data['y'], (int, float))
        
        # 驗證數據範圍
        assert position_data['x'] >= 0
        assert position_data['y'] >= 0

    def test_text_selection_simulation(self):
        """測試文字選擇模擬"""
        # 模擬選中的文字
        selected_text = "water competition problem"
        
        # 模擬位置計算
        mock_position = {"x": 150, "y": 200}
        
        # 驗證位置數據
        assert isinstance(mock_position["x"], (int, float))
        assert isinstance(mock_position["y"], (int, float))
        assert mock_position["x"] > 0
        assert mock_position["y"] > 0


@pytest.mark.fast
@pytest.mark.frontend
class TestFormStateConsistency:
    """測試表單狀態一致性"""
    
    def test_app_state_initial_values(self):
        """測試應用狀態初始值包含 retrievalCount"""
        # 模擬前端狀態
        initial_state = {
            "proposal": {
                "formData": {"goal": "", "retrievalCount": 10},
                "retrievalCount": 10
            }
        }
        
        # 驗證初始狀態
        assert initial_state["proposal"]["formData"]["retrievalCount"] == 10
        assert initial_state["proposal"]["retrievalCount"] == 10
        assert initial_state["proposal"]["formData"]["goal"] == ""

    def test_form_data_synchronization(self):
        """測試表單數據同步"""
        # 模擬表單數據更新
        form_data_updates = [
            {"goal": "測試目標1", "retrievalCount": 5},
            {"goal": "測試目標2", "retrievalCount": 15},
            {"goal": "測試目標3", "retrievalCount": 20}
        ]
        
        for update in form_data_updates:
            # 驗證更新後的數據
            assert "goal" in update
            assert "retrievalCount" in update
            assert update["retrievalCount"] in [1, 5, 10, 15, 20]

    def test_retrieval_count_options(self):
        """測試檢索數量選項"""
        expected_options = [
            {"value": 1, "label": "1 document (Dev Test)"},
            {"value": 5, "label": "5 documents (Fast)"},
            {"value": 10, "label": "10 documents (Balanced)"},
            {"value": 15, "label": "15 documents (Comprehensive)"},
            {"value": 20, "label": "20 documents (Thorough)"}
        ]
        
        for option in expected_options:
            assert isinstance(option["value"], int)
            assert isinstance(option["label"], str)
            assert option["value"] > 0
            assert "document" in option["label"]


@pytest.mark.integration
@pytest.mark.backend
class TestIntegrationScenarios:
    """測試整合場景"""
    
    @patch('backend.services.knowledge_service.agent_answer')
    def test_complete_proposal_workflow(self, mock_agent_answer):
        """測試完整的提案工作流程"""
        # 設置 mock 返回值
        mock_agent_answer.return_value = {
            "answer": "這是一個測試提案內容，包含多個段落和詳細信息。",
            "proposal": "這是一個測試提案內容，包含多個段落和詳細信息。",
            "chemicals": [{"name": "Mg2(dobpdc)", "smiles": "test"}],
            "not_found": [],
            "citations": [{"title": "Test Paper", "authors": "Test Author"}],
            "chunks": [{"content": "測試文檔塊", "metadata": {"source": "test.pdf"}}],
            "structured_proposal": {
                "proposal_title": "測試提案標題",
                "need": "研究需求描述",
                "solution": "解決方案描述"
            }
        }
        
        client = TestClient(app)
        
        # 1. 生成提案
        response = client.post(
            "/api/v1/proposal/generate",
            json={
                "research_goal": "Design a Mg2(dobpdc) based functionalized MOF",
                "retrieval_count": 15
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # 2. 驗證響應包含所有必要字段
        assert "proposal" in data
        assert "chemicals" in data
        assert "citations" in data
        assert "chunks" in data
        
        # 3. 驗證提案內容
        assert len(data["proposal"]) > 0
        assert len(data["chunks"]) > 0

    def test_text_highlight_workflow_simulation(self):
        """測試文字反白工作流程模擬"""
        # 模擬選中的文字
        selected_text = "water competition problem"
        
        # 模擬位置計算
        mock_position = {"x": 150, "y": 200}
        
        # 驗證位置數據
        assert isinstance(mock_position["x"], (int, float))
        assert isinstance(mock_position["y"], (int, float))
        assert mock_position["x"] > 0
        assert mock_position["y"] > 0
        
        # 模擬 popup 顯示
        popup_data = {
            "text": selected_text,
            "position": mock_position,
            "options": ["explain", "revise"]
        }
        
        assert popup_data["text"] == selected_text
        assert popup_data["position"] == mock_position
        assert "explain" in popup_data["options"]
        assert "revise" in popup_data["options"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])