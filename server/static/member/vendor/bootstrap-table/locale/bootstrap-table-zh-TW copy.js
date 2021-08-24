/**
 * Bootstrap Table Chinese translation
 * Author: Zhixin Wen<wenzhixin2010@gmail.com>
 */
(function ($) {
    'use strict';

    $.fn.bootstrapTable.locales['zh-TW'] = {
        formatLoadingMessage: function formatLoadingMessage() {
            return '正在努力地載入資料，請稍候……';
        },
        formatRecordsPerPage: function formatRecordsPerPage(pageNumber) {
            return "每頁顯示 ".concat(pageNumber, " 項記錄");
        },
        formatShowingRows: function formatShowingRows(pageFrom, pageTo, totalRows, totalNotFiltered) {
        if (totalNotFiltered !== undefined && totalNotFiltered > 0 && totalNotFiltered > totalRows) {
            return "\u986F\u793A\u7B2C ".concat(pageFrom, " \u5230\u7B2C ").concat(pageTo, " \u9805\u8A18\u9304，\u7E3D\u5171 ").concat(totalRows, " \u9805\u8A18\u9304(filtered from ").concat(totalNotFiltered, " \u6240\u6709\u8A18\u9304)");
        }
    
            return "\u986F\u793A\u7B2C ".concat(pageFrom, " \u5230\u7B2C ").concat(pageTo, " \u9805\u8A18\u9304，\u7E3D\u5171 ").concat(totalRows, " \u9805\u8A18\u9304");
        },
        formatSRPaginationPreText: function formatSRPaginationPreText() {
            return '上一頁';
        },
        formatSRPaginationPageText: function formatSRPaginationPageText(page) {
            return "\u8DF3\u81F3 ".concat(page, " \u9801");
        },
        formatSRPaginationNextText: function formatSRPaginationNextText() {
            return '下一頁';
        },
        formatDetailPagination: function formatDetailPagination(totalRows) {
            return "\u986F\u793A ".concat(totalRows, " \u884C");
        },
        formatClearSearch: function formatClearSearch() {
            return '清除過濾條件';
        },
        formatSearch: function formatSearch() {
            return '搜尋';
        },
        formatNoMatches: function formatNoMatches() {
            return '沒有找到符合的結果';
        },
        formatPaginationSwitch: function formatPaginationSwitch() {
            return '隱藏/顯示分頁';
        },
        formatPaginationSwitchDown: function formatPaginationSwitchDown() {
            return '顯示分頁';
        },
        formatPaginationSwitchUp: function formatPaginationSwitchUp() {
            return '隐藏分頁';
        },
        formatRefresh: function formatRefresh() {
            return '重新整理';
        },
        formatToggle: function formatToggle() {
            return '切換';
        },
        formatToggleOn: function formatToggleOn() {
            return '顯示詳細資料';
        },
        formatToggleOff: function formatToggleOff() {
            return '隱藏詳細資料';
        },
        formatColumns: function formatColumns() {
            return '列';
        },
        formatColumnsToggleAll: function formatColumnsToggleAll() {
            return '切換所有';
        },
        formatFullscreen: function formatFullscreen() {
            return '全螢幕';
        },
        formatAllRows: function formatAllRows() {
            return '所有';
        },
        formatAutoRefresh: function formatAutoRefresh() {
            return '自動更新';
        },
        formatExport: function formatExport() {
            return '导出数据';
        },
        formatJumpTo: function formatJumpTo() {
            return '跳至';
        },
        formatAdvancedSearch: function formatAdvancedSearch() {
            return '高級搜尋';
        },
        formatAdvancedCloseButton: function formatAdvancedCloseButton() {
            return '關閉';
        },
        formatFilterControlSwitch: function formatFilterControlSwitch() {
            return '隱藏/顯示過濾選項';
        },
        formatFilterControlSwitchHide: function formatFilterControlSwitchHide() {
            return '隱藏過濾選項';
        },
        formatFilterControlSwitchShow: function formatFilterControlSwitchShow() {
            return '顯示過濾選項';
        },
        formatClearFilters: function formatClearFilters() {
            return '清除過濾條件';
        },
        pageGo: function pageGo() {
            return '跳到';
        }

    };

    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['zh-TW']);

})(jQuery);
