/**
 * 文字反白功能 E2E 測試
 * ===================
 * 
 * 使用 Playwright 測試文字反白互動功能的完整用戶流程
 */

import { test, expect } from '@playwright/test';

// 測試配置
const BASE_URL = 'http://localhost:3000'; // 前端開發服務器
const API_BASE_URL = 'http://localhost:8000'; // 後端 API 服務器

test.describe('Text Highlight Workflows', () => {
  test.beforeEach(async ({ page }) => {
    // 每個測試前導航到主頁
    await page.goto(BASE_URL);
    
    // 等待頁面加載完成
    await page.waitForSelector('[data-testid="proposal-page"]', { timeout: 10000 });
  });

  test.describe('Explain Workflow', () => {
    test('should complete explain workflow for proposal text', async ({ page }) => {
      // 1. 導航到提案頁面
      await page.click('[data-testid="nav-proposal"]');
      await page.waitForSelector('[data-testid="proposal-content"]');

      // 2. 選擇文字
      const proposalText = await page.locator('[data-testid="proposal-content"]').first();
      await proposalText.selectText('metal organic framework');

      // 3. 等待彈窗出現
      await page.waitForSelector('[data-testid="highlight-popup"]', { timeout: 5000 });

      // 4. 點擊解釋按鈕
      await page.click('[data-testid="explain-button"]');

      // 5. 等待輸入框出現
      await page.waitForSelector('[data-testid="user-input"]');

      // 6. 輸入問題
      await page.fill('[data-testid="user-input"]', 'What is a metal organic framework?');

      // 7. 提交
      await page.click('[data-testid="submit-button"]');

      // 8. 等待響應
      await page.waitForSelector('[data-testid="interaction-response"]', { timeout: 30000 });

      // 9. 驗證響應內容
      const responseContent = await page.locator('[data-testid="response-content"]');
      await expect(responseContent).toBeVisible();
      
      const responseText = await responseContent.textContent();
      expect(responseText).toContain('metal organic framework');
    });

    test('should complete explain workflow for experiment detail text', async ({ page }) => {
      // 1. 導航到提案頁面
      await page.click('[data-testid="nav-proposal"]');
      await page.waitForSelector('[data-testid="experiment-detail-content"]');

      // 2. 選擇實驗細節文字
      const experimentText = await page.locator('[data-testid="experiment-detail-content"]').first();
      await experimentText.selectText('synthesis process');

      // 3. 等待彈窗出現
      await page.waitForSelector('[data-testid="highlight-popup"]', { timeout: 5000 });

      // 4. 點擊解釋按鈕
      await page.click('[data-testid="explain-button"]');

      // 5. 等待輸入框出現
      await page.waitForSelector('[data-testid="user-input"]');

      // 6. 輸入問題
      await page.fill('[data-testid="user-input"]', 'Explain the synthesis process');

      // 7. 提交
      await page.click('[data-testid="submit-button"]');

      // 8. 等待響應
      await page.waitForSelector('[data-testid="interaction-response"]', { timeout: 30000 });

      // 9. 驗證響應內容
      const responseContent = await page.locator('[data-testid="response-content"]');
      await expect(responseContent).toBeVisible();
      
      const responseText = await responseContent.textContent();
      expect(responseText).toContain('synthesis');
    });
  });

  test.describe('Revise Proposal Workflow', () => {
    test('should complete revise proposal workflow', async ({ page }) => {
      // 1. 導航到提案頁面
      await page.click('[data-testid="nav-proposal"]');
      await page.waitForSelector('[data-testid="proposal-content"]');

      // 2. 選擇提案文字
      const proposalText = await page.locator('[data-testid="proposal-content"]').first();
      await proposalText.selectText('research proposal');

      // 3. 等待彈窗出現
      await page.waitForSelector('[data-testid="highlight-popup"]', { timeout: 5000 });

      // 4. 點擊修改按鈕
      await page.click('[data-testid="revise-button"]');

      // 5. 等待輸入框出現
      await page.waitForSelector('[data-testid="user-input"]');

      // 6. 輸入修改請求
      await page.fill('[data-testid="user-input"]', 'Please improve the clarity of this section');

      // 7. 提交
      await page.click('[data-testid="submit-button"]');

      // 8. 等待修改完成（彈窗應該自動關閉）
      await page.waitForTimeout(30000);

      // 9. 驗證提案內容已更新
      const updatedProposal = await page.locator('[data-testid="proposal-content"]');
      await expect(updatedProposal).toBeVisible();

      // 10. 驗證修訂說明卡片出現
      const revisionCard = await page.locator('[data-testid="revision-explanation-card"]');
      await expect(revisionCard).toBeVisible();
    });
  });

  test.describe('Revise Experiment Detail Workflow', () => {
    test('should complete revise experiment detail workflow', async ({ page }) => {
      // 1. 導航到提案頁面
      await page.click('[data-testid="nav-proposal"]');
      await page.waitForSelector('[data-testid="experiment-detail-content"]');

      // 2. 選擇實驗細節文字
      const experimentText = await page.locator('[data-testid="experiment-detail-content"]').first();
      await experimentText.selectText('experimental procedure');

      // 3. 等待彈窗出現
      await page.waitForSelector('[data-testid="highlight-popup"]', { timeout: 5000 });

      // 4. 點擊修改按鈕
      await page.click('[data-testid="revise-button"]');

      // 5. 等待輸入框出現
      await page.waitForSelector('[data-testid="user-input"]');

      // 6. 輸入修改請求
      await page.fill('[data-testid="user-input"]', 'Please add more detail to this experimental step');

      // 7. 提交
      await page.click('[data-testid="submit-button"]');

      // 8. 等待修改完成（彈窗應該自動關閉）
      await page.waitForTimeout(30000);

      // 9. 驗證實驗細節內容已更新
      const updatedExperiment = await page.locator('[data-testid="experiment-detail-content"]');
      await expect(updatedExperiment).toBeVisible();

      // 10. 驗證修訂說明卡片出現
      const revisionCard = await page.locator('[data-testid="experiment-revision-explanation-card"]');
      await expect(revisionCard).toBeVisible();
    });
  });

  test.describe('Error Handling', () => {
    test('should handle empty highlighted text', async ({ page }) => {
      // 1. 導航到提案頁面
      await page.click('[data-testid="nav-proposal"]');
      await page.waitForSelector('[data-testid="proposal-content"]');

      // 2. 嘗試選擇空文字（這應該不會觸發彈窗）
      const proposalText = await page.locator('[data-testid="proposal-content"]').first();
      
      // 3. 驗證彈窗不會出現
      await page.waitForTimeout(2000);
      const popup = await page.locator('[data-testid="highlight-popup"]');
      await expect(popup).not.toBeVisible();
    });

    test('should handle API errors gracefully', async ({ page }) => {
      // 1. 模擬 API 錯誤
      await page.route(`${API_BASE_URL}/api/v1/text-interaction`, route => {
        route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'Internal server error' })
        });
      });

      // 2. 導航到提案頁面
      await page.click('[data-testid="nav-proposal"]');
      await page.waitForSelector('[data-testid="proposal-content"]');

      // 3. 選擇文字
      const proposalText = await page.locator('[data-testid="proposal-content"]').first();
      await proposalText.selectText('test text');

      // 4. 等待彈窗出現
      await page.waitForSelector('[data-testid="highlight-popup"]', { timeout: 5000 });

      // 5. 點擊解釋按鈕
      await page.click('[data-testid="explain-button"]');

      // 6. 等待輸入框出現
      await page.waitForSelector('[data-testid="user-input"]');

      // 7. 輸入問題
      await page.fill('[data-testid="user-input"]', 'test question');

      // 8. 提交
      await page.click('[data-testid="submit-button"]');

      // 9. 驗證錯誤處理
      await page.waitForSelector('[data-testid="error-message"]', { timeout: 10000 });
      const errorMessage = await page.locator('[data-testid="error-message"]');
      await expect(errorMessage).toBeVisible();
    });
  });

  test.describe('UI/UX Features', () => {
    test('should show correct popup position', async ({ page }) => {
      // 1. 導航到提案頁面
      await page.click('[data-testid="nav-proposal"]');
      await page.waitForSelector('[data-testid="proposal-content"]');

      // 2. 選擇文字
      const proposalText = await page.locator('[data-testid="proposal-content"]').first();
      await proposalText.selectText('test text');

      // 3. 等待彈窗出現
      await page.waitForSelector('[data-testid="highlight-popup"]', { timeout: 5000 });

      // 4. 驗證彈窗位置
      const popup = await page.locator('[data-testid="highlight-popup"]');
      await expect(popup).toBeVisible();

      // 5. 驗證彈窗包含正確的內容
      const highlightedText = await page.locator('[data-testid="highlighted-text"]');
      await expect(highlightedText).toContainText('test text');
    });

    test('should close popup when clicking outside', async ({ page }) => {
      // 1. 導航到提案頁面
      await page.click('[data-testid="nav-proposal"]');
      await page.waitForSelector('[data-testid="proposal-content"]');

      // 2. 選擇文字
      const proposalText = await page.locator('[data-testid="proposal-content"]').first();
      await proposalText.selectText('test text');

      // 3. 等待彈窗出現
      await page.waitForSelector('[data-testid="highlight-popup"]', { timeout: 5000 });

      // 4. 點擊彈窗外部
      await page.click('[data-testid="proposal-page"]');

      // 5. 驗證彈窗已關閉
      await page.waitForTimeout(1000);
      const popup = await page.locator('[data-testid="highlight-popup"]');
      await expect(popup).not.toBeVisible();
    });

    test('should show loading state during API calls', async ({ page }) => {
      // 1. 導航到提案頁面
      await page.click('[data-testid="nav-proposal"]');
      await page.waitForSelector('[data-testid="proposal-content"]');

      // 2. 選擇文字
      const proposalText = await page.locator('[data-testid="proposal-content"]').first();
      await proposalText.selectText('test text');

      // 3. 等待彈窗出現
      await page.waitForSelector('[data-testid="highlight-popup"]', { timeout: 5000 });

      // 4. 點擊解釋按鈕
      await page.click('[data-testid="explain-button"]');

      // 5. 等待輸入框出現
      await page.waitForSelector('[data-testid="user-input"]');

      // 6. 輸入問題
      await page.fill('[data-testid="user-input"]', 'test question');

      // 7. 提交
      await page.click('[data-testid="submit-button"]');

      // 8. 驗證加載狀態
      await page.waitForSelector('[data-testid="loading-spinner"]', { timeout: 5000 });
      const loadingSpinner = await page.locator('[data-testid="loading-spinner"]');
      await expect(loadingSpinner).toBeVisible();
    });
  });

  test.describe('Accessibility', () => {
    test('should have proper ARIA labels', async ({ page }) => {
      // 1. 導航到提案頁面
      await page.click('[data-testid="nav-proposal"]');
      await page.waitForSelector('[data-testid="proposal-content"]');

      // 2. 選擇文字
      const proposalText = await page.locator('[data-testid="proposal-content"]').first();
      await proposalText.selectText('test text');

      // 3. 等待彈窗出現
      await page.waitForSelector('[data-testid="highlight-popup"]', { timeout: 5000 });

      // 4. 驗證 ARIA 標籤
      const explainButton = await page.locator('[data-testid="explain-button"]');
      await expect(explainButton).toHaveAttribute('aria-label');

      const reviseButton = await page.locator('[data-testid="revise-button"]');
      await expect(reviseButton).toHaveAttribute('aria-label');

      const closeButton = await page.locator('[data-testid="close-button"]');
      await expect(closeButton).toHaveAttribute('aria-label');
    });

    test('should support keyboard navigation', async ({ page }) => {
      // 1. 導航到提案頁面
      await page.click('[data-testid="nav-proposal"]');
      await page.waitForSelector('[data-testid="proposal-content"]');

      // 2. 選擇文字
      const proposalText = await page.locator('[data-testid="proposal-content"]').first();
      await proposalText.selectText('test text');

      // 3. 等待彈窗出現
      await page.waitForSelector('[data-testid="highlight-popup"]', { timeout: 5000 });

      // 4. 使用鍵盤導航
      await page.keyboard.press('Tab');
      await page.keyboard.press('Enter'); // 激活解釋按鈕

      // 5. 等待輸入框出現
      await page.waitForSelector('[data-testid="user-input"]');

      // 6. 使用鍵盤輸入
      await page.keyboard.type('test question');
      await page.keyboard.press('Enter'); // 提交

      // 7. 驗證響應
      await page.waitForSelector('[data-testid="interaction-response"]', { timeout: 30000 });
      const response = await page.locator('[data-testid="interaction-response"]');
      await expect(response).toBeVisible();
    });
  });
});

// API E2E 測試
test.describe('API E2E Tests', () => {
  test('should handle explain API request', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/api/v1/text-interaction`, {
      data: {
        highlighted_text: 'metal organic framework',
        context_paragraph: 'This is a test context about metal organic frameworks.',
        user_input: 'What is a metal organic framework?',
        interaction_type: 'explain',
        highlighted_area: 'proposal',
        proposal: '',
        old_chunks: [],
        mode: 'proposal'
      }
    });

    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(data.interaction_type).toBe('explain');
    expect(data.answer).toBeTruthy();
    expect(data.request_id).toBeTruthy();
  });

  test('should handle revise proposal API request', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/api/v1/text-interaction`, {
      data: {
        highlighted_text: 'research proposal',
        context_paragraph: 'This is a test context about research proposals.',
        user_input: 'Please improve this section',
        interaction_type: 'revise',
        highlighted_area: 'proposal',
        proposal: 'This is the original proposal content.',
        old_chunks: [],
        mode: 'proposal'
      }
    });

    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(data.interaction_type).toBe('revise');
    expect(data.structured_proposal).toBeTruthy();
    expect(data.request_id).toBeTruthy();
  });

  test('should handle revise experiment detail API request', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/api/v1/text-interaction`, {
      data: {
        highlighted_text: 'experimental procedure',
        context_paragraph: 'This is a test context about experimental procedures.',
        user_input: 'Please add more detail to this step',
        interaction_type: 'revise',
        highlighted_area: 'experiment',
        proposal: 'This is the original proposal content.',
        old_chunks: [],
        mode: 'proposal'
      }
    });

    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(data.interaction_type).toBe('revise');
    expect(data.structured_experiment).toBeTruthy();
    expect(data.request_id).toBeTruthy();
  });

  test('should handle invalid API request', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/api/v1/text-interaction`, {
      data: {
        highlighted_text: '', // 空的反白文字
        context_paragraph: 'test context',
        user_input: 'test input',
        interaction_type: 'explain',
        highlighted_area: 'proposal',
        proposal: '',
        old_chunks: [],
        mode: 'proposal'
      }
    });

    expect(response.status()).toBe(400);
    const data = await response.json();
    expect(data.detail).toContain('反白文字不能為空');
  });
}); 