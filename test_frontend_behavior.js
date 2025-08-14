// 模擬前端行為測試
const API_BASE = '/api/v1';

// 模擬 citation 數據
const citation = {
    label: "[3]",
    title: "Welding Metallophthalocyanines into Bimetallic Molecular Meshes for Ultrasensitive, Low-Power Chemiresistive Detection of Gases",
    source: "107_Welding_Metallophthalocyanines_into_Bimetallic_Molecular_Meshes_for_Ultrasensiti_SI.pdf",
    page: "2",
    snippet: "141-78-6) were purchased from BDH Chemicals. Compounds 4,5-dimethoxyphthalodinit"
};

// 模擬前端 URL 構建邏輯
function buildCitationUrl(citation) {
    return `${API_BASE}/documents/${encodeURIComponent(citation.source)}`;
}

// 測試不同的 URL 構建方法
console.log("🔍 前端 URL 構建測試");
console.log("=" * 50);

console.log("📋 Citation 數據:");
console.log(`   source: ${citation.source}`);

console.log("\n🔗 URL 構建結果:");
const url1 = buildCitationUrl(citation);
console.log(`   方法 1 (encodeURIComponent): ${url1}`);

const url2 = `/api/v1/documents/${citation.source}`;
console.log(`   方法 2 (無編碼): ${url2}`);

const url3 = `/api/v1/documents/${encodeURIComponent(citation.source)}`;
console.log(`   方法 3 (手動編碼): ${url3}`);

console.log("\n🔍 編碼對比:");
console.log(`   原始文件名: ${citation.source}`);
console.log(`   encodeURIComponent: ${encodeURIComponent(citation.source)}`);
console.log(`   encodeURI: ${encodeURI(citation.source)}`);

console.log("\n💡 測試建議:");
console.log("1. 在瀏覽器中打開 http://localhost:3000");
console.log("2. 打開開發者工具 (F12)");
console.log("3. 點擊 citation 連結");
console.log("4. 觀察 Network 標籤中的請求");
console.log("5. 檢查 Response Headers 中的 Content-Disposition");

// 導出測試函數供其他腳本使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        buildCitationUrl,
        citation
    };
} 