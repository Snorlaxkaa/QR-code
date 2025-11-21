/* ==================== 
   搜尋和匯出頁面 - JavaScript
   ==================== */

/**
 * 初始化搜尋和匯出功能
 */
document.addEventListener('DOMContentLoaded', function() {
    initializeExportButton();
    initializeAutoScroll();
});

/**
 * 初始化匯出按鈕
 * - 取得搜尋參數
 * - 檢查是否有搜尋結果
 * - 綁定點擊事件
 */
function initializeExportButton() {
    var exportBtn = document.getElementById('exportBtn');
    var nidValue = document.querySelector('input[name="nid"]').value;
    var dateStart = document.querySelector('input[name="date_start"]').value;
    var dateEnd = document.querySelector('input[name="date_end"]').value;
    
    var hasSearch = nidValue || dateStart || dateEnd;
    var hasResults = document.querySelector('table') !== null;

    if (hasSearch && hasResults) {
        exportBtn.style.display = 'inline-block';
        exportBtn.addEventListener('click', handleExportClick);
    }
}

/**
 * 處理匯出按鈕點擊事件
 * @param {Event} e - 點擊事件
 */
function handleExportClick(e) {
    e.preventDefault();
    
    var nidValue = document.querySelector('input[name="nid"]').value;
    var dateStart = document.querySelector('input[name="date_start"]').value;
    var dateEnd = document.querySelector('input[name="date_end"]').value;

    var exportForm = createExportForm(nidValue, dateStart, dateEnd);
    
    document.body.appendChild(exportForm);
    exportForm.submit();
    document.body.removeChild(exportForm);
}

/**
 * 建立匯出表單
 * @param {string} nid - 身分證號碼
 * @param {string} dateStart - 開始日期
 * @param {string} dateEnd - 結束日期
 * @returns {HTMLFormElement} 表單元素
 */
function createExportForm(nid, dateStart, dateEnd) {
    var form = document.createElement('form');
    form.method = 'POST';
    form.action = document.querySelector('input[name="nid"]').closest('form').action.replace('/search_page', '/export_xlsx');

    var nidInput = createHiddenInput('nid', nid);
    var dateStartInput = createHiddenInput('date_start', dateStart);
    var dateEndInput = createHiddenInput('date_end', dateEnd);

    form.appendChild(nidInput);
    form.appendChild(dateStartInput);
    form.appendChild(dateEndInput);

    return form;
}

/**
 * 建立隱藏輸入欄位
 * @param {string} name - 欄位名稱
 * @param {string} value - 欄位值
 * @returns {HTMLInputElement} 隱藏輸入元素
 */
function createHiddenInput(name, value) {
    var input = document.createElement('input');
    input.type = 'hidden';
    input.name = name;
    input.value = value;
    return input;
}

/**
 * 初始化自動滾動功能
 * - 檢查是否有搜尋條件
 * - 如果有結果，自動滾動到結果區塊
 */
function initializeAutoScroll() {
    var nidValue = document.querySelector('input[name="nid"]').value;
    var dateStart = document.querySelector('input[name="date_start"]').value;
    var dateEnd = document.querySelector('input[name="date_end"]').value;
    
    var hasSearch = nidValue || dateStart || dateEnd;

    if (hasSearch) {
        setTimeout(function() {
            var resultSection = document.querySelector('.results-section');
            if (resultSection) {
                resultSection.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        }, 100);
    }
}