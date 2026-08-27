import eel
import os
import json
import time
import requests
import pyperclip
from pathlib import Path

# 初始化 Eel（指定 web 文件夹）
eel.init('web')

# 配置文件路径
CONFIG_FILE = 'config.json'

# 默认配置
DEFAULT_CONFIG = {
    "repo": "sairatecn/files",  # GitHub 仓库，格式 "用户名/仓库名"
    "branch": "master",  # 分支名，默认 master
    "domains": [
        "cdn.jsdelivr.net",
        "fastly.jsdelivr.net",
        "gcore.jsdelivr.net",
        "cdn.jsdmirror.com",
        "jsd.cdn.zzko.cn"
    ]
}


def load_config():
    """加载配置文件，若不存在则创建默认"""
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        return DEFAULT_CONFIG
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_config(config):
    """保存配置到文件"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)


# ---------- 新增：生成 filepath.txt ----------
def generate_filepath_txt():
    """在 files 目录下生成 filepath.txt，列出所有文件的相对路径"""
    files_dir = os.path.join(os.getcwd(), 'files')
    # 确保 files 目录存在
    if not os.path.exists(files_dir):
        os.makedirs(files_dir)

    output_path = os.path.join(files_dir, 'filepath.txt')

    with open(output_path, 'w', encoding='utf-8') as f:
        for root, dirs, files in os.walk(files_dir):
            for file in files:
                # 跳过 filepath.txt 自身
                if file == 'filepath.txt':
                    continue
                # 计算相对于 files_dir 的路径
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, files_dir)
                f.write(rel_path + '\n')


# ----------------------------------------------

# ---------- Eel 暴露的 API ----------

@eel.expose
def get_config():
    """获取当前配置"""
    return load_config()


@eel.expose
def save_repo(repo, branch):
    """保存仓库信息"""
    config = load_config()
    config['repo'] = repo
    config['branch'] = branch
    save_config(config)
    return True


@eel.expose
def save_domains(domains):
    """保存域名列表"""
    config = load_config()
    config['domains'] = domains
    save_config(config)
    return True


@eel.expose
def get_file_tree(root_path=None):
    """获取文件树结构（递归），默认根目录为 ./files"""
    if root_path is None:
        root_path = os.path.join(os.getcwd(), 'files')
    if not os.path.exists(root_path):
        return []  # 如果目录不存在，返回空树
    tree = []
    try:
        items = os.listdir(root_path)
        for name in sorted(items):
            full = os.path.join(root_path, name)
            is_dir = os.path.isdir(full)
            tree.append({
                'name': name,
                'path': full,
                'is_dir': is_dir,
                'children': [] if is_dir else None
            })
            if is_dir:
                try:
                    tree[-1]['children'] = get_file_tree(full)
                except PermissionError:
                    pass
    except PermissionError:
        pass
    return tree


@eel.expose
def get_cdn_urls(relative_path, config):
    """根据相对路径和配置生成多个 CDN URL"""
    repo = config.get('repo', '').strip('/')
    branch = config.get('branch', 'master')
    domains = config.get('domains', [])
    if not repo:
        return []
    # 相对路径使用正斜杠
    rel = relative_path.replace('\\', '/').lstrip('/')
    urls = []
    for domain in domains:
        url = f"https://{domain}/gh/{repo}@{branch}/{rel}"
        urls.append(url)
    return urls


@eel.expose
def get_relative_path(file_path):
    """获取相对于当前工作目录的路径"""
    cwd = os.getcwd()
    try:
        rel = os.path.relpath(file_path, cwd)
        return rel
    except ValueError:
        return file_path


@eel.expose
def test_latency(url):
    """测试 URL 的延迟（HEAD 请求耗时 ms）"""
    try:
        start = time.time()
        r = requests.head(url, timeout=3)
        elapsed = (time.time() - start) * 1000
        return round(elapsed, 1) if r.status_code < 400 else -1
    except:
        return -1


@eel.expose
def copy_to_clipboard(text):
    """复制文本到剪贴板"""
    pyperclip.copy(text)
    return True


# ---------- 启动程序 ----------
if __name__ == '__main__':
    # --- 新增：启动前生成 filepath.txt ---
    generate_filepath_txt()
    # -----------------------------------

    # 以当前目录为根，打开浏览器窗口（默认使用 Chrome 或系统浏览器）
    eel.start('index.html', size=(1200, 700), port=8000)