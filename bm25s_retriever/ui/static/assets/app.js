/**
 * BM25S Retriever UI JavaScript
 */

// Global state
let currentDocuments = [];
let currentSettings = {};

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    initTabs();
    initSearchTab();
    initDocumentsTab();
    initSettingsTab();
    initStatusTab();
    loadInitialData();
});

// Tab functionality
function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabPanels = document.querySelectorAll('[data-tab-panel]');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.dataset.tabTarget;
            
            // Update button states
            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            // Update panel visibility
            tabPanels.forEach(panel => {
                if (panel.dataset.tabPanel === targetTab) {
                    panel.classList.remove('panel-hidden');
                } else {
                    panel.classList.add('panel-hidden');
                }
            });
        });
    });
}

// Search tab functionality
function initSearchTab() {
    const searchBtn = document.getElementById('search-btn');
    const clearBtn = document.getElementById('search-clear');
    
    searchBtn?.addEventListener('click', performSearch);
    clearBtn?.addEventListener('click', clearSearch);
    
    // Add enter key support for search query
    document.getElementById('search-query')?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            performSearch();
        }
    });
}

async function performSearch() {
    const query = document.getElementById('search-query').value.trim();
    if (!query) {
        showMessage('search-results', 'Please enter a search query', 'error');
        return;
    }
    
    const temperature = parseFloat(document.getElementById('search-temperature').value);
    const cutoff = parseFloat(document.getElementById('search-cutoff').value);
    const ignoreZero = document.getElementById('search-ignore-zero').checked;
    
    try {
        showMessage('search-results', 'Searching...', 'info');
        
        const response = await fetch('/retrieve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query,
                temperature,
                llm_tools_cutoff: cutoff,
                ignore_zero: ignoreZero
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || data.message || 'Search failed');
        }
        
        displaySearchResults(data);
        
    } catch (error) {
        showMessage('search-results', `Error: ${error.message}`, 'error');
    }
}

function displaySearchResults(data) {
    const resultsDiv = document.getElementById('search-results');
    
    if (!data.documents || data.documents.length === 0) {
        showMessage('search-results', 'No documents found matching your query', 'warning');
        return;
    }
    
    let html = `
        <div class="muted" style="margin-bottom: 12px;">
            Found ${data.documents.length} documents (from ${data.total_retrieved} total)
        </div>
    `;
    
    data.documents.forEach(doc => {
        const scorePercent = (doc.softmax_score * 100).toFixed(2);
        const bm25Score = doc.bm25_score.toFixed(3);
        
        html += `
            <div class="card" style="margin-bottom: 12px; padding: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                    <h4 style="margin: 0;">${escapeHtml(doc.title)}</h4>
                    <div style="text-align: right;">
                        <div style="font-size: 0.9em; color: #666;">Relevance: ${scorePercent}%</div>
                        <div style="font-size: 0.8em; color: #999;">BM25: ${bm25Score}</div>
                    </div>
                </div>
                <div style="margin-bottom: 8px;">
                    ${escapeHtml(doc.content.substring(0, 200))}${doc.content.length > 200 ? '...' : ''}
                </div>
                ${doc.keywords && doc.keywords.length > 0 ? `
                    <div style="font-size: 0.8em; color: #666;">
                        Keywords: ${doc.keywords.map(kw => `<span style="background: #f0f0f0; padding: 2px 6px; border-radius: 3px; margin-right: 4px;">${escapeHtml(kw)}</span>`).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    });
    
    resultsDiv.innerHTML = html;
}

function clearSearch() {
    document.getElementById('search-query').value = '';
    document.getElementById('search-results').innerHTML = '<div class="muted">Enter a query to search documents.</div>';
}

// Documents tab functionality
function initDocumentsTab() {
    const addBtn = document.getElementById('add-document-btn');
    const reloadBtn = document.getElementById('reload-index-btn');
    const saveBtn = document.getElementById('save-document-btn');
    
    addBtn?.addEventListener('click', () => {
        document.getElementById('add-document-modal').style.display = 'block';
    });
    
    reloadBtn?.addEventListener('click', reloadIndex);
    saveBtn?.addEventListener('click', saveDocument);
    
    // Modal can only be closed by X button (no outside-click closing)
}

function closeModal() {
    document.getElementById('add-document-modal').style.display = 'none';
    clearDocumentForm();
}

function clearDocumentForm() {
    document.getElementById('doc-id').value = '';
    document.getElementById('doc-title').value = '';
    document.getElementById('doc-content').value = '';
    document.getElementById('doc-keywords').value = '';
}

async function saveDocument() {
    const id = document.getElementById('doc-id').value.trim();
    const title = document.getElementById('doc-title').value.trim();
    const content = document.getElementById('doc-content').value.trim();
    const keywordsStr = document.getElementById('doc-keywords').value.trim();
    
    if (!id || !title || !content) {
        alert('Please fill in ID, title, and content fields');
        return;
    }
    
    const keywords = keywordsStr ? keywordsStr.split(',').map(k => k.trim()).filter(k => k) : [];
    
    try {
        const response = await fetch('/index', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                documents: [{
                    id,
                    title,
                    content,
                    keywords,
                    metadata: {}
                }],
                rebuild: false
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || data.message || 'Failed to save document');
        }
        
        showMessage('documents-result', 'Document added successfully', 'success');
        closeModal();
        loadDocuments();
        
    } catch (error) {
        showMessage('documents-result', `Error: ${error.message}`, 'error');
    }
}

async function loadDocuments() {
    try {
        const response = await fetch('/status');
        const data = await response.json();
        
        if (response.ok) {
            displayDocuments(data.document_count || 0);
        }
    } catch (error) {
        console.error('Failed to load documents:', error);
    }
}

function displayDocuments(count) {
    const listDiv = document.getElementById('documents-list');
    listDiv.innerHTML = `
        <div class="muted">
            <p>Total indexed documents: ${count}</p>
            <p>Use the "Add Document" button to add new documents.</p>
        </div>
    `;
}

async function reloadIndex() {
    try {
        showMessage('documents-result', 'Reloading index...', 'info');
        
        const response = await fetch('/reload', { method: 'POST' });
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || data.message || 'Failed to reload index');
        }
        
        showMessage('documents-result', 'Index reloaded successfully', 'success');
        loadDocuments();
        
    } catch (error) {
        showMessage('documents-result', `Error: ${error.message}`, 'error');
    }
}

// Settings tab functionality
function initSettingsTab() {
    const saveBtn = document.getElementById('settings-save');
    saveBtn?.addEventListener('click', saveSettings);
}

async function loadSettings() {
    try {
        const response = await fetch('/settings');
        const data = await response.json();
        
        if (response.ok) {
            currentSettings = data;
            updateSettingsUI(data);
        }
    } catch (error) {
        console.error('Failed to load settings:', error);
    }
}

function updateSettingsUI(settings) {
    document.getElementById('settings-temperature').value = settings.bm25s.temperature;
    document.getElementById('settings-ignore-zero').checked = settings.bm25s.ignore_zero;
    document.getElementById('settings-cutoff').value = settings.bm25s.llm_tools_cutoff;
}

async function saveSettings() {
    const temperature = parseFloat(document.getElementById('settings-temperature').value);
    const ignoreZero = document.getElementById('settings-ignore-zero').checked;
    const cutoff = parseFloat(document.getElementById('settings-cutoff').value);
    
    try {
        showMessage('settings-result', 'Saving settings...', 'info');
        
        const response = await fetch('/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                temperature,
                ignore_zero: ignoreZero,
                llm_tools_cutoff: cutoff
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || data.message || 'Failed to save settings');
        }
        
        showMessage('settings-result', 'Settings saved successfully', 'success');
        updateSettingsUI(data);
        
    } catch (error) {
        showMessage('settings-result', `Error: ${error.message}`, 'error');
    }
}

// Status tab functionality
function initStatusTab() {
    const refreshBtn = document.getElementById('status-refresh');
    refreshBtn?.addEventListener('click', loadStatus);
}

async function loadStatus() {
    try {
        const response = await fetch('/status');
        const data = await response.json();
        
        if (response.ok) {
            displayStatus(data);
        }
    } catch (error) {
        document.getElementById('service-status').innerHTML = 
            `<div class="muted" style="color: red;">Error loading status: ${error.message}</div>`;
    }
}

function displayStatus(data) {
    const statusDiv = document.getElementById('service-status');
    const metricsDiv = document.getElementById('performance-metrics');
    
    statusDiv.innerHTML = `
        <div style="display: grid; gap: 8px;">
            <div><strong>Status:</strong> <span style="color: ${data.status === 'healthy' ? 'green' : 'red'};">${data.status}</span></div>
            <div><strong>Document Count:</strong> ${data.document_count}</div>
            <div><strong>Retriever Initialized:</strong> ${data.retriever_initialized ? 'Yes' : 'No'}</div>
            <div><strong>Version:</strong> ${data.version}</div>
        </div>
    `;
    
    metricsDiv.innerHTML = `
        <div class="muted">
            <p>Performance metrics will be available after search operations.</p>
            <p>Monitor search response times and result quality.</p>
        </div>
    `;
}

// Utility functions
function showMessage(elementId, message, type = 'info') {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const colors = {
        info: '#666',
        success: 'green',
        warning: 'orange',
        error: 'red'
    };
    
    element.innerHTML = `<div style="color: ${colors[type]};">${message}</div>`;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function loadInitialData() {
    await Promise.all([
        loadSettings(),
        loadDocuments(),
        loadStatus()
    ]);
}
