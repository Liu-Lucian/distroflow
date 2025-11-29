#!/usr/bin/env python3
"""
GitHub 挤牙膏式发布系统
======================

智能地将项目逐步提交到 GitHub，增加 activity 和曝光度。

策略：
- 按模块拆分代码（30+ 个 commits）
- 每天 1-3 个 commits（随机化避免规律）
- 有意义的 commit messages
- 按逻辑顺序发布（基础设施 → 核心功能 → 高级功能）

运行：
    python3 github_gradual_publisher.py --init     # 初始化仓库
    python3 github_gradual_publisher.py --once     # 提交一次
    python3 github_gradual_publisher.py --forever  # 永久运行
"""

import os
import sys
import json
import time
import random
import logging
import subprocess
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('github_publisher.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# ==================== 配置 ====================

CONFIG = {
    # GitHub 仓库配置
    'repo_url': 'https://github.com/q1q1-spefic/interview_assistant.git',
    'repo_name': 'interview_assistant',
    'branch': 'main',

    # 源代码路径
    'source_dir': '/Users/l.u.c/my-app/interview_assistant',

    # 发布频率
    'commits_per_day': {
        'min': 1,
        'max': 3
    },

    # 提交时间窗口（避免半夜提交）
    'commit_time_windows': [
        (9, 12),    # 上午 9:00-11:59
        (14, 18),   # 下午 2:00-17:59
        (20, 24)    # 晚上 8:00-23:59
    ],

    # 检查间隔（小时）
    'check_interval_hours': 6
}

# ==================== 模块定义 ====================

# 按逻辑顺序定义要发布的模块
# 每个模块包含：文件列表、commit 消息、描述
MODULES = [
    # ===== 第 1 阶段：项目基础设施 =====
    {
        'name': 'project-setup',
        'files': ['requirements.txt', 'requirements_minimal.txt', '.env.example', 'setup.sh', 'start.sh'],
        'message': '🎉 Initial commit: Project setup and dependencies',
        'description': 'Core project configuration and setup scripts'
    },
    {
        'name': 'readme',
        'files': ['README.md', 'CLAUDE.md', 'LICENSE'],
        'message': '📚 Add comprehensive documentation',
        'description': 'Project documentation and license'
    },
    {
        'name': 'config',
        'files': ['config.py', 'project.config.json'],
        'message': '⚙️ Add system configuration module',
        'description': 'Centralized configuration management'
    },

    # ===== 第 2 阶段：核心数据库和工具 =====
    {
        'name': 'database-setup',
        'files': ['database_migration.py', 'user_data_migration.py'],
        'message': '🗄️ Add database migration system',
        'description': 'Database schema management and migration tools'
    },
    {
        'name': 'user-auth',
        'files': ['user_auth.py', 'admin_auth.py', 'user_id_helper.py'],
        'message': '🔐 Implement user authentication system',
        'description': 'User login, registration, and session management'
    },
    {
        'name': 'email-service',
        'files': ['email_service.py', 'email_verification.py'],
        'message': '📧 Add email verification system',
        'description': 'Email sending and verification functionality'
    },

    # ===== 第 3 阶段：核心功能 - 简历处理 =====
    {
        'name': 'resume-parser',
        'files': ['enhanced_resume_parser.py', 'advanced_resume_analyzer.py'],
        'message': '📄 Implement advanced resume parsing (GPT-4 powered)',
        'description': 'AI-powered resume parsing and analysis'
    },
    {
        'name': 'resume-optimizer',
        'files': ['resume_optimizer.py', 'resume_version_manager.py'],
        'message': '✨ Add resume optimization and version control',
        'description': 'Resume improvement suggestions and version management'
    },
    {
        'name': 'resume-service',
        'files': ['resume_analysis_service.py', 'version_comparator.py'],
        'message': '🔍 Add resume analysis service layer',
        'description': 'Resume analysis API and version comparison'
    },

    # ===== 第 4 阶段：JD 处理和实体提取 =====
    {
        'name': 'jd-analyzer',
        'files': ['advanced_jd_analyzer.py', 'advanced_entity_extractor.py'],
        'message': '🎯 Implement job description analyzer',
        'description': 'AI-powered JD parsing and entity extraction'
    },
    {
        'name': 'tech-enhancer',
        'files': ['tech_question_enhancer.py', 'interview_template_matcher.py'],
        'message': '💡 Add technical question enhancement',
        'description': 'Technical interview question generation and matching'
    },

    # ===== 第 5 阶段：面试题模板系统 =====
    {
        'name': 'template-database',
        'files': ['template_deduplicator.py', 'intelligent_deduplicator.py'],
        'message': '🧹 Implement template deduplication system',
        'description': 'Smart template deduplication using embeddings'
    },
    {
        'name': 'template-quality',
        'files': ['template_quality_enhancer.py', 'template_operation_logger.py'],
        'message': '⭐ Add template quality enhancement',
        'description': 'Template quality scoring and operation logging'
    },
    {
        'name': 'template-optimization',
        'files': ['enhanced_star_optimizer.py', 'optimized_deduplicator.py'],
        'message': '🚀 Optimize template STAR framework',
        'description': 'STAR/PREP framework optimization for interview answers'
    },

    # ===== 第 6 阶段：语音识别和处理 =====
    {
        'name': 'voice-assistant',
        'files': ['voice_interview_assistant.py', 'streaming_api.py'],
        'message': '🎤 Implement voice interview assistant (Azure Speech)',
        'description': 'Real-time voice transcription and streaming'
    },
    {
        'name': 'speaker-recognition',
        'files': ['eagle_speaker_recognition.py', 'simple_speaker_detection.py'],
        'message': '👤 Add speaker recognition (Picovoice Eagle)',
        'description': 'Speaker diarization for interview recordings'
    },
    {
        'name': 'speaker-enrollment',
        'files': ['speaker_enrollment_manager.py', 'eagle_frame_processor.py'],
        'message': '🔊 Implement speaker enrollment system',
        'description': 'Voice profile creation and management'
    },

    # ===== 第 7 阶段：模拟面试系统 =====
    {
        'name': 'mock-interview-basic',
        'files': ['mock_interview_manager.py'],
        'message': '🎭 Add basic mock interview functionality',
        'description': 'Basic mock interview session management'
    },
    {
        'name': 'mock-interview-advanced',
        'files': ['advanced_mock_interview_manager.py', 'advanced_mock_interview_session.py'],
        'message': '🚀 Implement advanced mock interview system',
        'description': 'Advanced mock interviews with AI feedback'
    },
    {
        'name': 'realtime-mock',
        'files': ['realtime_mock_interview_engine.py', 'realtime_mock_routes.py', 'websocket_interview_handler.py'],
        'message': '⚡ Add real-time mock interview engine',
        'description': 'WebSocket-based real-time mock interviews'
    },

    # ===== 第 8 阶段：记忆和图谱系统 =====
    {
        'name': 'memory-basic',
        'files': ['memory_graph_manager.py', 'memory_tier_manager.py'],
        'message': '🧠 Implement memory graph system',
        'description': 'Graph-based memory management for user context'
    },
    {
        'name': 'memory-advanced',
        'files': ['enhanced_memory_graph_manager.py', 'openai_memory_manager.py'],
        'message': '🔮 Add enhanced memory management (OpenAI powered)',
        'description': 'AI-powered memory conflict resolution'
    },
    {
        'name': 'memory-optimization',
        'files': ['memory_importance_adjuster.py', 'memory_merger.py'],
        'message': '📊 Optimize memory importance and merging',
        'description': 'Memory importance scoring and intelligent merging'
    },

    # ===== 第 9 阶段：向量搜索和优化 =====
    {
        'name': 'vector-search',
        'files': ['vector_similarity_detector.py', 'optimized_graph_engine.py'],
        'message': '🔍 Implement vector similarity search',
        'description': 'ChromaDB-based semantic search for templates'
    },
    {
        'name': 'identity-resolver',
        'files': ['identity_resolver.py', 'integration_guide.py'],
        'message': '🆔 Add identity resolution system',
        'description': 'User identity matching and integration'
    },

    # ===== 第 10 阶段：支付和推荐系统 =====
    {
        'name': 'payment-system',
        'files': ['payment_system.py', 'payment_system_migration.py', 'run_payment_migration.py'],
        'message': '💳 Implement payment system',
        'description': 'Premium feature payment and subscription'
    },
    {
        'name': 'referral-system',
        'files': ['referral_tracker.py', 'referral_codes.py'],
        'message': '🎁 Add referral tracking system',
        'description': 'Referral code generation and reward tracking'
    },
    {
        'name': 'blogger-management',
        'files': ['blogger_management.py', 'smart_display_filter.py'],
        'message': '📢 Implement blogger management',
        'description': 'Content creator management and filtering'
    },

    # ===== 第 11 阶段：分析和安全 =====
    {
        'name': 'user-analytics',
        'files': ['user_analytics.py', 'task_manager.py'],
        'message': '📈 Add user analytics and task management',
        'description': 'User behavior tracking and async task queue'
    },
    {
        'name': 'device-fingerprint',
        'files': ['device_fingerprint.py'],
        'message': '🔒 Implement device fingerprinting',
        'description': 'Fraud prevention and device tracking'
    },
    {
        'name': 'video-analysis',
        'files': ['video_behavior_analyzer.py'],
        'message': '📹 Add video behavior analysis',
        'description': 'Interview video recording and behavior analysis'
    },

    # ===== 第 12 阶段：性能优化 =====
    {
        'name': 'performance',
        'files': ['performance_optimizer.py', 'optimized_fixed.py'],
        'message': '⚡ Add performance optimization modules',
        'description': 'System performance monitoring and optimization'
    },
    {
        'name': 'feedback-handler',
        'files': ['feedback_handler.py', 'global_manager.py'],
        'message': '💬 Implement feedback collection system',
        'description': 'User feedback and global state management'
    },

    # ===== 第 13 阶段：前端模板 =====
    {
        'name': 'templates-core',
        'files': ['templates/index.html', 'templates/login.html', 'templates/register.html', 'templates/base.html'],
        'message': '🎨 Add core frontend templates',
        'description': 'Main UI templates (login, register, home)'
    },
    {
        'name': 'templates-resume',
        'files': ['templates/upload_resume.html', 'templates/resume_analysis.html', 'templates/optimize_resume.html'],
        'message': '📝 Add resume management templates',
        'description': 'Resume upload, analysis, and optimization UI'
    },
    {
        'name': 'templates-interview',
        'files': ['templates/interview_templates.html', 'templates/mock_interview.html', 'templates/realtime_mock.html'],
        'message': '🎭 Add interview templates UI',
        'description': 'Mock interview and template management UI'
    },
    {
        'name': 'templates-advanced',
        'files': ['templates/speaker_enrollment.html', 'templates/payment.html', 'templates/referral.html'],
        'message': '🔧 Add advanced feature templates',
        'description': 'Speaker enrollment, payment, and referral UI'
    },
    {
        'name': 'static-assets',
        'files': ['static/css/style.css', 'static/js/main.js', 'robots.txt'],
        'message': '🎨 Add static assets and styles',
        'description': 'CSS, JavaScript, and static resources'
    },

    # ===== 第 14 阶段：主应用 =====
    {
        'name': 'main-application',
        'files': ['interview_assistant_system.py'],
        'message': '🏗️ Add main Flask application (11k+ lines)',
        'description': 'Core Flask app integrating all modules'
    },

    # ===== 第 15 阶段：测试和文档 =====
    {
        'name': 'tests',
        'files': ['test_eagle.py', 'test_speaker_recognition.py', 'resume_analysis_test.py'],
        'message': '🧪 Add comprehensive test suite',
        'description': 'Unit tests for speaker recognition and resume analysis'
    },
    {
        'name': 'integration-docs',
        'files': ['REALTIME_MOCK_INTERVIEW_INTEGRATION.md', 'MarketingBrief.md'],
        'message': '📖 Add integration and marketing documentation',
        'description': 'Technical integration guides and marketing materials'
    },

    # ===== 第 16 阶段：国际化 =====
    {
        'name': 'i18n',
        'files': ['babel.cfg', 'extract_useful_translations.py'],
        'message': '🌍 Add internationalization support',
        'description': 'Bilingual support (English/Chinese)'
    },
]

# ==================== GitHub 发布器 ====================

class GitHubGradualPublisher:
    """挤牙膏式 GitHub 发布器"""

    def __init__(self):
        self.source_dir = CONFIG['source_dir']
        self.repo_url = CONFIG['repo_url']
        self.repo_name = CONFIG['repo_name']
        self.state_file = 'github_publisher_state.json'
        self.state = self.load_state()

    def load_state(self) -> Dict:
        """加载发布状态"""
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'initialized': False,
                'current_module_index': 0,
                'total_commits': 0,
                'commits_today': 0,
                'last_commit_date': None,
                'completed_modules': []
            }

    def save_state(self):
        """保存发布状态"""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)

    def run_command(self, cmd: str, cwd: str = None) -> tuple:
        """运行命令并返回结果"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=cwd or self.repo_name,
                capture_output=True,
                text=True,
                check=True
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"命令执行失败: {cmd}")
            logger.error(f"错误: {e.stderr}")
            return False, e.stderr

    def init_repository(self):
        """初始化 Git 仓库"""
        logger.info("=" * 80)
        logger.info("📦 初始化 Git 仓库")
        logger.info("=" * 80)

        # 检查源目录
        if not os.path.exists(self.source_dir):
            logger.error(f"源目录不存在: {self.source_dir}")
            return False

        # 创建仓库目录
        if os.path.exists(self.repo_name):
            logger.warning(f"仓库目录已存在: {self.repo_name}")
            choice = input("是否删除并重新初始化？(y/N): ").strip().lower()
            if choice == 'y':
                import shutil
                shutil.rmtree(self.repo_name)
            else:
                return False

        # 初始化 Git
        logger.info("初始化 Git 仓库...")
        os.makedirs(self.repo_name, exist_ok=True)

        success, _ = self.run_command("git init")
        if not success:
            return False

        # 设置默认分支为 main
        logger.info("设置默认分支为 main...")
        self.run_command("git config init.defaultBranch main")

        # 如果当前是 master，重命名为 main
        success, output = self.run_command("git branch --show-current")
        if success and output.strip() == "master":
            logger.info("重命名 master 分支为 main...")
            self.run_command("git branch -m master main")

        # 配置 Git
        self.run_command('git config user.name "q1q1-spefic"')
        self.run_command('git config user.email "your-email@example.com"')

        # 添加远程仓库
        logger.info(f"添加远程仓库: {self.repo_url}")
        self.run_command(f'git remote add origin {self.repo_url}')

        # 创建 .gitignore
        self.create_gitignore()

        # 创建 README.md
        self.create_readme()

        # 标记为已初始化
        self.state['initialized'] = True
        self.save_state()

        logger.info("✅ 仓库初始化完成")
        return True

    def create_gitignore(self):
        """创建 .gitignore"""
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/

# Environment Variables
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Database
*.db
*.sqlite
*.sqlite3

# Logs
*.log
logs/
debug.log

# OS
.DS_Store
Thumbs.db

# User Uploads
uploads/
data/

# Backup files
*.backup
*.bak
backup_*/

# Test files
test_audio.wav
test_*.txt

# Temporary files
temp_*.py
*.tmp

# Campaign tracking
campaign_tracking.db
"""
        with open(f'{self.repo_name}/.gitignore', 'w') as f:
            f.write(gitignore_content)

    def create_readme(self):
        """创建 README.md"""
        readme_content = """# 🎯 AI Interview Assistant (即答侠 / HireMeAI)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange.svg)](https://openai.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> 🚀 **Real-time AI-powered interview preparation system** with voice recognition, mock interviews, and personalized question generation.

---

## ✨ Key Features

### 📄 Resume Intelligence
- **AI Resume Parser** - GPT-4 powered resume analysis (PDF/DOCX/TXT)
- **Smart Optimization** - AI-driven resume improvement suggestions
- **Version Control** - Track and compare resume versions
- **Entity Extraction** - Extract skills, experience, and education

### 🎯 Job Matching
- **JD Analysis** - Automatic job description parsing from URLs or text
- **Skill Gap Detection** - Identify missing skills and experience
- **Match Scoring** - Resume-JD compatibility scoring

### 💡 Interview Preparation
- **Personalized Questions** - AI-generated questions based on your resume and JD
- **STAR Framework** - Behavioral questions with STAR/PREP structure
- **Template Library** - ChromaDB-powered semantic search for 1000+ questions
- **Difficulty Levels** - Questions categorized by difficulty

### 🎤 Voice & Mock Interviews
- **Real-time Mock Interviews** - Practice with AI interviewer
- **Voice Recognition** - Azure Speech Services integration
- **Speaker Diarization** - Picovoice Eagle speaker recognition
- **AI Feedback** - Instant analysis and improvement suggestions
- **WebSocket Streaming** - Low-latency real-time conversations

### 🧠 Memory & Context
- **Graph-based Memory** - Persistent user context across sessions
- **Vector Search** - Semantic similarity for template matching
- **Intelligent Deduplication** - Smart template and question merging

### 💳 Premium Features
- **Payment System** - Subscription and one-time payment support
- **Referral Program** - Reward system for user referrals
- **Device Fingerprinting** - Fraud prevention

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API Key
- Azure Speech Services Key (optional, for voice features)
- Picovoice Access Key (optional, for speaker recognition)

### Installation

```bash
# Clone the repository
git clone https://github.com/q1q1-spefic/interview_assistant.git
cd interview_assistant

# Run setup script
chmod +x setup.sh
./setup.sh

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Running the Application

```bash
# Start the server
python interview_assistant_system.py

# Or use the start script
./start.sh

# Access at http://localhost:5001
```

---

## 🏗️ Architecture

```
interview_assistant/
├── interview_assistant_system.py  # Main Flask application (11k+ lines)
├── config.py                      # System configuration
│
├── Resume Processing
│   ├── enhanced_resume_parser.py
│   ├── resume_optimizer.py
│   └── resume_analysis_service.py
│
├── JD & Entity Extraction
│   ├── advanced_jd_analyzer.py
│   └── advanced_entity_extractor.py
│
├── Interview Templates
│   ├── template_deduplicator.py
│   ├── enhanced_star_optimizer.py
│   └── interview_template_matcher.py
│
├── Voice & Mock Interviews
│   ├── voice_interview_assistant.py
│   ├── eagle_speaker_recognition.py
│   ├── advanced_mock_interview_manager.py
│   └── realtime_mock_interview_engine.py
│
├── Memory & Vector Search
│   ├── memory_graph_manager.py
│   ├── enhanced_memory_graph_manager.py
│   └── vector_similarity_detector.py
│
├── User Management
│   ├── user_auth.py
│   ├── payment_system.py
│   └── referral_tracker.py
│
└── templates/                     # Jinja2 HTML templates
```

---

## 💻 Tech Stack

- **Backend**: Flask, SQLite, ChromaDB
- **AI**: OpenAI GPT-4, GPT-4o-mini
- **Voice**: Azure Speech Services, Picovoice Eagle
- **Vector DB**: ChromaDB (embeddings search)
- **Frontend**: Jinja2, vanilla JavaScript
- **Real-time**: WebSocket, Server-Sent Events (SSE)

---

## 📊 Performance Metrics

- **Resume Parsing**: ~5s (PDF/DOCX → Structured JSON)
- **Question Generation**: ~3s (50 personalized questions)
- **First-byte Latency**: ~1.0s (real-time mock interview)
- **Speaker Recognition**: 95% accuracy (Picovoice Eagle)
- **Template Search**: <100ms (ChromaDB vector similarity)

---

## 🔧 Configuration

Edit `.env` with your API keys:

```bash
OPENAI_API_KEY=your_openai_key
AZURE_SPEECH_KEY=your_azure_key
AZURE_SPEECH_REGION=eastus
PICOVOICE_ACCESS_KEY=your_picovoice_key  # Optional
```

See `config.py` for advanced configuration options.

---

## 📖 Documentation

- [Technical Documentation](CLAUDE.md)
- [Real-time Mock Interview Integration](REALTIME_MOCK_INTERVIEW_INTEGRATION.md)
- [Marketing Brief](MarketingBrief.md)

---

## 🧪 Testing

```bash
# Run tests
python test_speaker_recognition.py
python resume_analysis_test.py
python test_eagle.py
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- OpenAI for GPT-4 API
- Microsoft Azure for Speech Services
- Picovoice for Eagle Speaker Recognition
- ChromaDB for vector similarity search

---

## 📞 Contact

- Website: [interviewasssistant.com](https://interviewasssistant.com)
- GitHub: [@q1q1-spefic](https://github.com/q1q1-spefic)

---

**⭐ Star this repo if you find it helpful!**
"""
        with open(f'{self.repo_name}/README.md', 'w') as f:
            f.write(readme_content)

    def should_commit_now(self) -> bool:
        """判断现在是否应该提交"""

        # 重置每日计数器
        today_str = datetime.now().strftime('%Y-%m-%d')
        last_commit_date = self.state.get('last_commit_date', '')

        # 只有当上次提交日期是不同的一天时才重置
        if last_commit_date and last_commit_date != today_str:
            logger.info(f"📅 新的一天（上次: {last_commit_date}，今天: {today_str}），重置提交计数器")
            self.state['commits_today'] = 0
            self.save_state()

        # 检查是否已达到今日限额
        max_commits = CONFIG['commits_per_day']['max']
        if self.state['commits_today'] >= max_commits:
            logger.info(f"⏸️  今日提交已达上限 ({self.state['commits_today']}/{max_commits})")
            return False

        # 检查是否在提交时间窗口内
        current_hour = datetime.now().hour
        in_time_window = any(
            start <= current_hour < end
            for start, end in CONFIG['commit_time_windows']
        )

        if not in_time_window:
            logger.info(f"⏸️  当前时间 ({current_hour}:00) 不在提交窗口内")
            return False

        # 确保达到最少提交数
        min_commits = CONFIG['commits_per_day']['min']
        if self.state['commits_today'] < min_commits:
            logger.info(f"✅ 今日提交未达最低要求 ({self.state['commits_today']}/{min_commits})")
            return True

        # 随机决定 (40% 概率)
        if random.random() < 0.4:
            logger.info("✅ 随机决定提交")
            return True
        else:
            logger.info("⏸️  随机决定暂不提交")
            return False

    def copy_files(self, module: Dict) -> bool:
        """复制模块文件到仓库"""
        logger.info(f"📂 复制文件: {module['name']}")

        copied_count = 0
        for file_path in module['files']:
            src = os.path.join(self.source_dir, file_path)
            dst = os.path.join(self.repo_name, file_path)

            # 创建目标目录
            os.makedirs(os.path.dirname(dst), exist_ok=True)

            # 复制文件
            if os.path.isfile(src):
                import shutil
                shutil.copy2(src, dst)
                copied_count += 1
                logger.info(f"  ✓ {file_path}")
            elif os.path.isdir(src):
                # 如果是目录，复制整个目录
                import shutil
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
                copied_count += 1
                logger.info(f"  ✓ {file_path}/ (directory)")
            else:
                logger.warning(f"  ⚠️  文件不存在: {file_path}")

        logger.info(f"✅ 复制了 {copied_count} 个文件/目录")
        return copied_count > 0

    def commit_module(self, module: Dict) -> bool:
        """提交一个模块"""
        logger.info("\n" + "=" * 80)
        logger.info(f"📦 提交模块: {module['name']}")
        logger.info(f"   {module['description']}")
        logger.info("=" * 80)

        # 复制文件
        if not self.copy_files(module):
            logger.error("没有文件被复制，跳过提交")
            return False

        # Git add
        logger.info("📝 添加文件到 Git...")
        success, _ = self.run_command('git add .')
        if not success:
            return False

        # Git commit
        logger.info(f"💾 提交: {module['message']}")
        commit_message = f"{module['message']}\n\n{module['description']}"
        success, _ = self.run_command(f'git commit -m "{commit_message}"')
        if not success:
            logger.warning("没有变更需要提交")
            return False

        # 确保分支存在且名称正确
        success, current_branch = self.run_command("git branch --show-current")
        if not success or not current_branch.strip():
            logger.error("无法获取当前分支")
            return False

        current_branch = current_branch.strip()
        target_branch = CONFIG["branch"]

        # 如果当前分支不是目标分支，重命名
        if current_branch != target_branch:
            logger.info(f"重命名分支 {current_branch} -> {target_branch}")
            self.run_command(f"git branch -m {current_branch} {target_branch}")
            current_branch = target_branch

        # Git push
        logger.info(f"🚀 推送到 GitHub (分支: {current_branch})...")

        # 首次推送使用 -u 设置上游
        success, output = self.run_command(f'git push -u origin {current_branch}')

        if not success:
            logger.error("推送失败，请检查远程仓库权限")
            logger.error(f"详细错误: {output}")
            return False

        # 更新状态
        self.state['current_module_index'] += 1
        self.state['total_commits'] += 1
        self.state['commits_today'] += 1
        self.state['last_commit_date'] = datetime.now().isoformat()
        self.state['completed_modules'].append(module['name'])
        self.save_state()

        logger.info(f"✅ 提交成功！总计: {self.state['total_commits']} commits")
        return True

    def setup_git_auth(self):
        """设置 Git 认证"""

        # 检查是否有环境变量中的 token
        github_token = os.getenv('GITHUB_TOKEN')

        if github_token:
            logger.info("🔐 使用环境变量 GITHUB_TOKEN 配置认证...")

            # 更新远程 URL 包含 token
            success, _ = self.run_command(f'git remote set-url origin https://{github_token}@github.com/q1q1-spefic/interview_assistant.git')

            if success:
                logger.info("✅ 认证配置成功")
                return True
            else:
                logger.error("❌ 认证配置失败")
                return False

        # 检查当前的远程 URL
        success, output = self.run_command("git remote get-url origin")

        if success:
            url = output.strip()

            # 如果是 HTTPS 且包含 token，说明已配置
            if 'https://' in url and '@github.com' in url:
                logger.info("✅ 远程 URL 已包含认证信息")
                return True

            # 如果是 SSH，检查 SSH 密钥
            if 'git@github.com' in url:
                logger.info("🔑 使用 SSH 认证")
                # 测试 SSH 连接
                success, _ = self.run_command("ssh -T git@github.com 2>&1", cwd=".")
                # SSH 测试总是会"失败"（返回 1），但如果认证成功会有 "successfully authenticated" 消息
                # 这里我们假设 SSH 已配置好
                return True

        return False

    def check_and_push_unpushed_commits(self) -> bool:
        """检查并推送未推送的 commits"""

        # 检查是否有未推送的 commits
        success, output = self.run_command("git log origin/main..HEAD --oneline 2>/dev/null || git log --oneline")

        if not success:
            return False

        unpushed_commits = output.strip().split('\n') if output.strip() else []

        if not unpushed_commits or (len(unpushed_commits) == 1 and not unpushed_commits[0]):
            logger.info("📭 没有未推送的 commits")
            return False

        logger.info(f"📦 发现 {len(unpushed_commits)} 个未推送的 commits")
        for commit in unpushed_commits[:5]:  # 只显示前5个
            logger.info(f"   {commit}")

        # 尝试设置认证
        self.setup_git_auth()

        # 尝试推送
        logger.info("🚀 尝试推送未推送的 commits...")

        # 获取当前分支
        success, current_branch = self.run_command("git branch --show-current")
        if not success:
            logger.error("无法获取当前分支")
            return False

        current_branch = current_branch.strip()

        # 推送
        success, output = self.run_command(f'git push -u origin {current_branch}')

        if success:
            logger.info("✅ 未推送的 commits 已成功推送")

            # 更新状态 - 每个未推送的 commit 对应一个模块
            commits_pushed = len(unpushed_commits)
            self.state['current_module_index'] = min(
                self.state['current_module_index'] + commits_pushed,
                len(MODULES)
            )
            self.state['total_commits'] += commits_pushed
            self.save_state()

            return True
        else:
            logger.error("❌ 推送失败")
            logger.error(f"错误: {output}")

            # 如果是认证问题，给出提示
            if "Permission denied" in output or "could not read Username" in output:
                logger.error("\n" + "=" * 80)
                logger.error("🔐 推送失败：需要配置 GitHub 认证")
                logger.error("=" * 80)
                logger.error("\n快速解决方案（选择一种）：")
                logger.error("\n方法 1: 使用环境变量（推荐）")
                logger.error("  1. 编辑文件: GITHUB_TOKEN.env")
                logger.error("  2. 填写你的 GitHub token")
                logger.error("  3. 运行: source GITHUB_TOKEN.env")
                logger.error("  4. 重启此脚本")
                logger.error("\n方法 2: 直接配置 Git URL")
                logger.error("  cd interview_assistant")
                logger.error("  git remote set-url origin https://<TOKEN>@github.com/q1q1-spefic/interview_assistant.git")
                logger.error("\n方法 3: 运行快速认证脚本")
                logger.error("  ./quick_auth.sh")
                logger.error("\n详细文档:")
                logger.error("  - GITHUB_AUTH_QUICKFIX.md")
                logger.error("  - ./setup_github_auth.sh")
                logger.error("\n" + "=" * 80)
                logger.error("\n⏳ 系统将在下次检查时自动重试推送...")
                logger.error("=" * 80 + "\n")

            return False

    def execute_once(self) -> bool:
        """执行一次提交"""

        # 检查是否初始化
        if not self.state['initialized']:
            logger.error("❌ 仓库未初始化，请先运行 --init")
            return False

        # 首先检查是否有未推送的 commits
        if self.check_and_push_unpushed_commits():
            logger.info("✅ 已处理未推送的 commits")
            # 成功推送后，继续下一个模块

        # 检查是否应该提交
        if not self.should_commit_now():
            return False

        # 检查是否还有未提交的模块
        if self.state['current_module_index'] >= len(MODULES):
            logger.info("🎉 所有模块已提交完成！")
            return False

        # 获取下一个模块
        module = MODULES[self.state['current_module_index']]

        # 提交
        return self.commit_module(module)

    def run_forever(self):
        """永久运行"""
        logger.info("\n" + "=" * 80)
        logger.info("🤖 GitHub 挤牙膏式发布系统 - 永久运行模式")
        logger.info("=" * 80)
        logger.info(f"仓库: {CONFIG['repo_url']}")
        logger.info(f"检查间隔: {CONFIG['check_interval_hours']} 小时")
        logger.info(f"每日提交: {CONFIG['commits_per_day']['min']}-{CONFIG['commits_per_day']['max']} 次")
        logger.info("=" * 80)

        try:
            while True:
                # 检查是否完成
                if self.state['current_module_index'] >= len(MODULES):
                    logger.info("\n🎉 所有模块已提交完成！系统退出。")
                    break

                # 执行一次
                self.execute_once()

                # 等待下次检查
                wait_hours = CONFIG['check_interval_hours']
                wait_minutes = wait_hours * 60 + random.randint(-30, 30)

                next_check = datetime.now() + timedelta(minutes=wait_minutes)
                logger.info(f"\n⏰ 下次检查时间: {next_check.strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"   (等待 {wait_minutes} 分钟)\n")

                time.sleep(wait_minutes * 60)

        except KeyboardInterrupt:
            logger.info("\n\n⚠️  用户中断，正在关闭...")
        finally:
            logger.info("✅ 系统已关闭")

    def print_status(self):
        """打印当前状态"""
        logger.info("\n" + "=" * 80)
        logger.info("📊 发布状态")
        logger.info("=" * 80)
        logger.info(f"仓库: {CONFIG['repo_url']}")
        logger.info(f"初始化: {'✅' if self.state['initialized'] else '❌'}")
        logger.info(f"总模块数: {len(MODULES)}")
        logger.info(f"已完成: {self.state['current_module_index']}/{len(MODULES)}")
        logger.info(f"总提交数: {self.state['total_commits']}")
        logger.info(f"今日提交: {self.state['commits_today']}/{CONFIG['commits_per_day']['max']}")

        if self.state.get('last_commit_date'):
            logger.info(f"上次提交: {self.state['last_commit_date']}")

        if self.state['current_module_index'] < len(MODULES):
            next_module = MODULES[self.state['current_module_index']]
            logger.info(f"\n下一个模块: {next_module['name']}")
            logger.info(f"  {next_module['description']}")
            logger.info(f"  文件数: {len(next_module['files'])}")

        logger.info("\n已完成模块:")
        for module_name in self.state['completed_modules'][-5:]:
            logger.info(f"  ✅ {module_name}")

        logger.info("=" * 80 + "\n")

# ==================== CLI ====================

def main():
    parser = argparse.ArgumentParser(
        description='GitHub 挤牙膏式发布系统',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--init', action='store_true', help='初始化 Git 仓库')
    parser.add_argument('--once', action='store_true', help='执行一次提交')
    parser.add_argument('--forever', action='store_true', help='永久运行')
    parser.add_argument('--status', action='store_true', help='查看状态')

    args = parser.parse_args()

    publisher = GitHubGradualPublisher()

    # 初始化
    if args.init:
        publisher.init_repository()
        return 0

    # 查看状态
    if args.status:
        publisher.print_status()
        return 0

    # 默认单次运行
    if not args.once and not args.forever:
        args.once = True

    # 执行
    if args.once:
        publisher.execute_once()
    elif args.forever:
        publisher.run_forever()

    return 0

if __name__ == "__main__":
    exit(main())
