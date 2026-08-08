// ---------- 全局变量 ----------
let currentConfig = null;
let currentTree = null;
let selectedPath = null;
let allPingBtn = null;            // 存储“全部测速”按钮引用

// ---------- 初始化 ----------
window.onload = function() {
    loadConfig();
    loadFileTree();
    setupEventListeners();
};

// ---------- 加载配置 ----------
async function loadConfig() {
    currentConfig = await eel.get_config()();
    document.getElementById('repoInput').value = currentConfig.repo || '';
    document.getElementById('branchInput').value = currentConfig.branch || 'master';
    renderDomains(currentConfig.domains || []);
}

function renderDomains(domains) {
    const container = document.getElementById('domainList');
    container.innerHTML = '';
    domains.forEach((d, idx) => {
        const span = document.createElement('span');
        span.className = 'domain-item';
        span.innerHTML = `${d} <span class="del-domain" data-index="${idx}">✕</span>`;
        container.appendChild(span);
    });
    document.querySelectorAll('.del-domain').forEach(el => {
        el.onclick = function(e) {
            const idx = parseInt(this.dataset.index);
            const domains = currentConfig.domains || [];
            domains.splice(idx, 1);
            renderDomains(domains);
            eel.save_domains(domains);
            currentConfig.domains = domains;
        };
    });
}

// ---------- 文件树（可折叠） ----------
async function loadFileTree() {
    const tree = await eel.get_file_tree()();
    currentTree = tree;
    const container = document.getElementById('treeContainer');
    container.innerHTML = '';
    const rootDiv = document.createElement('div');
    rootDiv.className = 'tree-node';
    renderTreeNodes(tree, rootDiv, 0);
    container.appendChild(rootDiv);
}

function renderTreeNodes(nodes, parentElement, level) {
    nodes.forEach(node => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'tree-item';
        itemDiv.style.paddingLeft = (level * 16) + 'px';

        const toggleSpan = document.createElement('span');
        toggleSpan.className = 'toggle-icon';
        if (node.is_dir && node.children && node.children.length > 0) {
            toggleSpan.textContent = '▼';
            toggleSpan.style.display = 'inline-block';
        } else {
            toggleSpan.textContent = '·';
            toggleSpan.style.color = '#b0b8c4';
        }

        const nameSpan = document.createElement('span');
        nameSpan.className = 'name';
        if (node.is_dir) {
            nameSpan.classList.add('folder');
            nameSpan.textContent = node.name;
        } else {
            nameSpan.textContent = node.name;
        }

        itemDiv.appendChild(toggleSpan);
        itemDiv.appendChild(nameSpan);
        parentElement.appendChild(itemDiv);

        if (node.is_dir && node.children && node.children.length > 0) {
            const childContainer = document.createElement('div');
            childContainer.className = 'tree-children';
            childContainer.style.display = 'block';
            renderTreeNodes(node.children, childContainer, level + 1);
            parentElement.appendChild(childContainer);

            itemDiv.onclick = function(e) {
                e.stopPropagation();
                if (childContainer.style.display === 'none') {
                    childContainer.style.display = 'block';
                    toggleSpan.textContent = '▼';
                } else {
                    childContainer.style.display = 'none';
                    toggleSpan.textContent = '▶';
                }
                onItemClick(node);
            };
        } else {
            itemDiv.onclick = function(e) {
                e.stopPropagation();
                onItemClick(node);
            };
        }
    });
}

// ---------- 显示CDN链接（包含全部测速按钮） ----------
async function onItemClick(node) {
    const path = node.path;
    selectedPath = path;
    const rel = await eel.get_relative_path(path)();
    const config = currentConfig;
    if (!config.repo) {
        document.getElementById('detailContent').innerHTML = '<p class="placeholder">⚠️ 请先配置 GitHub 仓库</p>';
        return;
    }
    const urls = await eel.get_cdn_urls(rel, config)();
    if (urls.length === 0) {
        document.getElementById('detailContent').innerHTML = '<p class="placeholder">⚠️ 没有可用的 CDN 域名</p>';
        return;
    }
    const detail = document.getElementById('detailContent');
    // 显示相对路径
    let html = `<p style="margin-bottom:12px; font-size:14px; color:#4a5568;"><strong>相对路径：</strong>${rel}</p>`;
    detail.innerHTML = html;

    // 创建“全部测速”按钮
    const allPingDiv = document.createElement('div');
    allPingDiv.style.marginBottom = '14px';
    allPingBtn = document.createElement('button');
    allPingBtn.className = 'btn ping all-ping';
    allPingBtn.textContent = '📡 全部测速';
    allPingBtn.style.background = '#6c757d';  // 灰色，与普通ping区分
    allPingBtn.onclick = function() {
        // 禁用自身
        this.disabled = true;
        this.textContent = '⏳ 全部测速中...';
        // 获取所有单个ping按钮（排除自身）
        const pingBtns = document.querySelectorAll('.ping:not(.all-ping)');
        if (pingBtns.length === 0) {
            this.disabled = false;
            this.textContent = '📡 全部测速';
            return;
        }
        // 逐个触发点击（仅触发未被禁用的）
        pingBtns.forEach(btn => {
            if (!btn.disabled) {
                btn.click();
            }
        });
        // 检查是否有按钮未禁用？如果没有，则直接启用自身（但正常情况下会有）
        // 启用由 testLatency 中的检查逻辑完成
    };
    allPingDiv.appendChild(allPingBtn);
    detail.appendChild(allPingDiv);

    // 添加每个URL条目
    urls.forEach((url, index) => {
        const div = document.createElement('div');
        div.className = 'url-item';
        div.innerHTML = `
            <span class="url-text">${url}</span>
            <span class="latency" id="latency-${index}">⚪ 未测速</span>
            <button class="btn ping" data-url="${url}" data-index="${index}">📡 Ping</button>
            <button class="btn copy" data-url="${url}">复制</button>
        `;
        detail.appendChild(div);

        // Ping 按钮事件
        div.querySelector('.ping').onclick = function() {
            const url = this.dataset.url;
            const idx = this.dataset.index;
            const latencySpan = document.getElementById(`latency-${idx}`);
            this.disabled = true;
            this.textContent = '⏳ 测试中...';
            testLatency(url, latencySpan, this);
        };

        // 复制按钮事件
        div.querySelector('.copy').onclick = function() {
            eel.copy_to_clipboard(this.dataset.url);
            this.textContent = '已复制';
            setTimeout(() => this.textContent = '复制', 1500);
        };
    });
}

// ---------- 测速函数（改造：测速完成后检查全部按钮状态） ----------
async function testLatency(url, el, btn) {
    const ms = await eel.test_latency(url)();
    if (ms > 0) {
        el.textContent = `${ms} ms`;
        el.style.background = ms < 200 ? '#d4edda' : (ms < 500 ? '#fff3cd' : '#f8d7da');
    } else {
        el.textContent = '❌ 超时';
        el.style.background = '#f8d7da';
    }
    // 恢复单个按钮
    if (btn) {
        btn.disabled = false;
        btn.textContent = '📡 Ping';
    }
    // 检查是否所有单个按钮都已可用，如果是则启用“全部测速”按钮
    if (allPingBtn) {
        const singleBtns = document.querySelectorAll('.ping:not(.all-ping)');
        let allDone = true;
        singleBtns.forEach(b => {
            if (b.disabled) allDone = false;
        });
        if (allDone && singleBtns.length > 0) {
            allPingBtn.disabled = false;
            allPingBtn.textContent = '📡 全部测速';
        } else if (singleBtns.length === 0) {
            // 没有单个按钮时，启用全部按钮（但不可能发生）
            allPingBtn.disabled = false;
            allPingBtn.textContent = '📡 全部测速';
        }
    }
}

// ---------- 事件绑定 ----------
function setupEventListeners() {
    document.getElementById('saveRepoBtn').onclick = async function() {
        const repo = document.getElementById('repoInput').value.trim();
        const branch = document.getElementById('branchInput').value.trim() || 'master';
        if (!repo) { alert('请输入仓库名'); return; }
        await eel.save_repo(repo, branch)();
        currentConfig.repo = repo;
        currentConfig.branch = branch;
        alert('仓库配置已保存');
    };

    document.getElementById('addDomainBtn').onclick = function() {
        const newDomain = prompt('请输入新的 CDN 域名（例如 cdn.jsdelivr.net）：');
        if (newDomain) {
            const domains = currentConfig.domains || [];
            domains.push(newDomain.trim());
            renderDomains(domains);
            eel.save_domains(domains);
            currentConfig.domains = domains;
        }
    };

    document.getElementById('saveDomainsBtn').onclick = function() {
        const items = document.querySelectorAll('.domain-item');
        const domains = [];
        items.forEach(item => {
            const text = item.textContent.replace('✕', '').trim();
            if (text) domains.push(text);
        });
        eel.save_domains(domains);
        currentConfig.domains = domains;
        alert('域名已保存');
    };
}