#!/usr/bin/env python3
"""
GitHub发布器 - README更新
使用Git命令更新repository的README
"""

import os
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class GitHubPoster:
    def __init__(self, repo_path: str = None):
        """
        repo_path: 本地Git仓库路径（如果不提供，会在临时目录创建）
        """
        self.repo_path = repo_path
        self.repo_name = "hiremeai-content"  # 默认仓库名

    def create_post(self, content: dict) -> bool:
        """
        创建GitHub README帖子

        content格式:
        {
            'content': 'README.md内容（Markdown格式）',
            'files': {
                'README.md': '内容...',
                'docs/GUIDE.md': '内容...'
            },
            'repo_topics': ['ai', 'interview', 'automation']
        }
        """
        try:
            readme_content = content.get('content', '')
            files = content.get('files', {'README.md': readme_content})

            logger.info(f"📦 准备GitHub内容发布...")

            # 方案1: 如果有本地仓库路径，直接更新
            if self.repo_path and os.path.exists(self.repo_path):
                logger.info(f"   📂 使用现有仓库: {self.repo_path}")

                os.chdir(self.repo_path)

                # 更新文件
                for file_path, file_content in files.items():
                    full_path = os.path.join(self.repo_path, file_path)

                    # 创建目录
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)

                    # 写入文件
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(file_content)

                    logger.info(f"      ✅ 已更新: {file_path}")

                # Git提交
                try:
                    subprocess.run(['git', 'add', '.'], check=True)
                    subprocess.run(
                        ['git', 'commit', '-m', 'Update content from MarketingMind AI'],
                        check=True
                    )
                    subprocess.run(['git', 'push'], check=True)
                    logger.info(f"   ✅ GitHub内容已推送")
                    return True
                except subprocess.CalledProcessError as e:
                    logger.error(f"   ❌ Git操作失败: {str(e)}")
                    return False

            # 方案2: 没有仓库路径，输出内容供手动创建
            else:
                logger.warning("   ⚠️  未提供仓库路径")
                logger.info("   💡 请手动创建GitHub仓库并上传以下内容：")
                logger.info("")

                for file_path, file_content in files.items():
                    logger.info(f"   📄 {file_path}:")
                    logger.info("   " + "-"*50)
                    logger.info(file_content[:500] + "..." if len(file_content) > 500 else file_content)
                    logger.info("")

                # 保存到临时文件
                temp_dir = "github_content_temp"
                os.makedirs(temp_dir, exist_ok=True)

                for file_path, file_content in files.items():
                    temp_file = os.path.join(temp_dir, file_path)
                    os.makedirs(os.path.dirname(temp_file), exist_ok=True)

                    with open(temp_file, 'w', encoding='utf-8') as f:
                        f.write(file_content)

                logger.info(f"   💾 内容已保存到: {temp_dir}/")
                logger.info(f"   📋 下一步：")
                logger.info(f"      1. 在GitHub创建新仓库")
                logger.info(f"      2. 上传 {temp_dir}/ 中的文件")
                logger.info(f"      3. 或提供repo_path参数实现自动化")

                return True

        except Exception as e:
            logger.error(f"   ❌ GitHub发布失败: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False

if __name__ == "__main__":
    # 测试
    import sys

    logging.basicConfig(level=logging.INFO)

    test_content = {
        'content': '''# HireMeAI Interview Preparation

🚀 AI-powered interview preparation platform

## Overview

HireMeAI transforms how job seekers prepare for interviews using advanced AI technology.

## Features

- ✅ Personalized practice questions
- ✅ Real-time feedback
- ✅ Industry-specific scenarios
- ✅ Confidence building

## Quick Start

Visit [HireMeAI.app](https://hiremeai.app) to get started.

## Contributing

Contributions welcome! Please read CONTRIBUTING.md first.

## License

MIT License - see LICENSE file for details.
''',
        'files': {
            'README.md': '# HireMeAI\n\nAI-powered interview prep...',
        },
        'repo_topics': ['ai', 'interview', 'automation', 'career']
    }

    # 测试1: 没有仓库路径（输出内容）
    poster = GitHubPoster()
    poster.create_post(test_content)

    # 测试2: 有仓库路径（实际推送）
    # poster = GitHubPoster(repo_path='/path/to/your/repo')
    # poster.create_post(test_content)
