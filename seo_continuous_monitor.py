#!/usr/bin/env python3
"""
SEO持续监控系统
- 自动检测内容质量问题
- 自动修复并重新运行
- 持续优化和更新内容
"""

import os
import sys
import time
import json
import subprocess
import re
from datetime import datetime
from pathlib import Path

# 工作目录
WORK_DIR = "/Users/l.u.c/my-app/MarketingMind AI"
os.chdir(WORK_DIR)

# 监控配置
CHECK_INTERVAL = 300  # 每5分钟检查一次
CONTENT_DIR = "seo_data/content"
PUBLISHED_CONTENT_FILE = "seo_data/published_content.json"
WORKFLOW_STATE_FILE = "seo_data/workflow_state.json"

class SEOMonitor:
    def __init__(self):
        self.run_count = 0
        self.fix_count = 0
        self.last_check = None

    def log(self, message, level="INFO"):
        """日志输出"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            "INFO": "ℹ️ ",
            "SUCCESS": "✅",
            "WARNING": "⚠️ ",
            "ERROR": "❌",
            "FIX": "🔧"
        }.get(level, "")
        print(f"[{timestamp}] {prefix} {message}")
        sys.stdout.flush()

    def check_html_quality(self, filepath):
        """检查HTML文件质量"""
        issues = []

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # 检查1: Markdown artifacts
            if '```markdown' in content or '```\n' in content[:1000]:
                issues.append({
                    'type': 'markdown_artifacts',
                    'severity': 'high',
                    'description': 'Found markdown code block markers in HTML'
                })

            # 检查2: HireMeAI品牌提及
            hiremeai_count = content.lower().count('hiremeai') + content.lower().count('即答侠')
            if hiremeai_count < 3:
                issues.append({
                    'type': 'weak_branding',
                    'severity': 'medium',
                    'description': f'HireMeAI mentioned only {hiremeai_count} times (expected ≥3)'
                })

            # 检查3: CTA链接
            cta_count = content.count('https://interviewasssistant.com')
            if cta_count < 2:
                issues.append({
                    'type': 'missing_cta',
                    'severity': 'high',
                    'description': f'Only {cta_count} CTAs found (expected ≥2)'
                })

            # 检查4: Schema markup
            if '"@context": "https://schema.org"' not in content:
                issues.append({
                    'type': 'missing_schema',
                    'severity': 'medium',
                    'description': 'Missing Schema.org markup'
                })

            # 检查5: Meta描述
            if 'meta name="description"' not in content:
                issues.append({
                    'type': 'missing_meta',
                    'severity': 'high',
                    'description': 'Missing meta description'
                })

            # 检查6: HTML结构问题
            # 简单检查：</p>应该在<p>之后
            p_open = content.count('<p>')
            p_close = content.count('</p>')
            if abs(p_open - p_close) > 2:
                issues.append({
                    'type': 'html_structure',
                    'severity': 'medium',
                    'description': f'Unbalanced <p> tags: {p_open} open, {p_close} close'
                })

        except Exception as e:
            issues.append({
                'type': 'read_error',
                'severity': 'critical',
                'description': f'Cannot read file: {str(e)}'
            })

        return issues

    def check_all_content(self):
        """检查所有发布的内容"""
        self.log("🔍 Scanning all published content...")

        if not os.path.exists(CONTENT_DIR):
            self.log("Content directory not found!", "ERROR")
            return []

        html_files = list(Path(CONTENT_DIR).glob("*.html"))
        self.log(f"   Found {len(html_files)} HTML files")

        all_issues = []
        for filepath in html_files:
            issues = self.check_html_quality(filepath)
            if issues:
                all_issues.append({
                    'file': filepath.name,
                    'path': str(filepath),
                    'issues': issues
                })

        return all_issues

    def auto_fix_content(self):
        """自动修复内容质量问题"""
        self.log("🔧 Running content quality fix...", "FIX")

        try:
            result = subprocess.run(
                ['python3', 'fix_seo_content.py'],
                cwd=WORK_DIR,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                self.log("   ✅ Content fix completed successfully", "SUCCESS")
                self.fix_count += 1
                return True
            else:
                self.log(f"   ❌ Fix script failed: {result.stderr}", "ERROR")
                return False

        except subprocess.TimeoutExpired:
            self.log("   ❌ Fix script timeout", "ERROR")
            return False
        except Exception as e:
            self.log(f"   ❌ Fix error: {str(e)}", "ERROR")
            return False

    def run_seo_workflow(self):
        """运行完整SEO工作流"""
        self.log("🚀 Starting SEO workflow run...", "INFO")

        try:
            # 使用unbuffered模式运行
            process = subprocess.Popen(
                ['python3', '-u', 'run_seo_workflow.py', '--auto'],
                cwd=WORK_DIR,
                env={**os.environ, 'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY', '')},
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            # 实时输出
            for line in process.stdout:
                print(line, end='')
                sys.stdout.flush()

            process.wait(timeout=1800)  # 30分钟超时

            if process.returncode == 0:
                self.log("   ✅ Workflow completed successfully", "SUCCESS")
                self.run_count += 1
                return True
            else:
                self.log(f"   ❌ Workflow failed with code {process.returncode}", "ERROR")
                return False

        except subprocess.TimeoutExpired:
            self.log("   ❌ Workflow timeout (30min)", "ERROR")
            process.kill()
            return False
        except Exception as e:
            self.log(f"   ❌ Workflow error: {str(e)}", "ERROR")
            return False

    def monitor_cycle(self):
        """单次监控循环"""
        self.log("="*80)
        self.log(f"📊 Monitoring Cycle #{self.run_count + 1}")
        self.log(f"   Total runs: {self.run_count} | Total fixes: {self.fix_count}")
        self.log("="*80)

        # 步骤1: 检查内容质量
        issues_found = self.check_all_content()

        if issues_found:
            self.log(f"⚠️  Found quality issues in {len(issues_found)} files:", "WARNING")
            for item in issues_found:
                self.log(f"   📄 {item['file']}:")
                for issue in item['issues']:
                    self.log(f"      • [{issue['severity']}] {issue['description']}")

            # 步骤2: 自动修复
            self.log("\n🔧 Attempting auto-fix...")
            fix_success = self.auto_fix_content()

            if fix_success:
                # 重新检查
                self.log("\n🔍 Re-checking after fix...")
                time.sleep(2)
                issues_after_fix = self.check_all_content()

                if not issues_after_fix:
                    self.log("   ✅ All issues resolved!", "SUCCESS")
                else:
                    self.log(f"   ⚠️  {len(issues_after_fix)} files still have issues", "WARNING")

        else:
            self.log("✅ No quality issues detected - content is healthy!", "SUCCESS")

        # 步骤3: 检查是否需要生成新内容
        try:
            if os.path.exists(PUBLISHED_CONTENT_FILE):
                with open(PUBLISHED_CONTENT_FILE, 'r') as f:
                    published = json.load(f)
                    published_count = len(published)

                self.log(f"\n📊 Current content inventory: {published_count} articles")

                # 如果内容少于10篇，运行新一轮生成
                if published_count < 10:
                    self.log(f"   ℹ️  Content count below target (10), running workflow to generate more...")
                    workflow_success = self.run_seo_workflow()

                    if workflow_success:
                        # 工作流成功后，再次修复确保质量
                        self.log("\n🔧 Applying quality fix to new content...")
                        self.auto_fix_content()
                    else:
                        self.log("   ⚠️  Workflow failed, will retry next cycle", "WARNING")
                else:
                    self.log(f"   ✅ Content inventory is healthy ({published_count}/10 target)")

        except Exception as e:
            self.log(f"   ⚠️  Cannot check content inventory: {e}", "WARNING")

        self.last_check = datetime.now()

    def run_continuous(self):
        """持续监控主循环"""
        self.log("🚀 SEO Continuous Monitoring System Started")
        self.log("="*80)
        self.log("📋 Configuration:")
        self.log(f"   Check interval: {CHECK_INTERVAL}s ({CHECK_INTERVAL/60:.1f} minutes)")
        self.log(f"   Content directory: {CONTENT_DIR}")
        self.log(f"   OpenAI API Key: {'✅ Set' if os.environ.get('OPENAI_API_KEY') else '❌ Not set'}")
        self.log("="*80)
        self.log("\n⚠️  Press Ctrl+C to stop monitoring\n")

        # 立即执行第一次检查
        try:
            self.monitor_cycle()
        except Exception as e:
            self.log(f"❌ Cycle error: {str(e)}", "ERROR")

        # 持续循环
        while True:
            try:
                # 等待下一次检查
                next_check = self.last_check.timestamp() + CHECK_INTERVAL if self.last_check else time.time()
                wait_seconds = max(0, next_check - time.time())

                if wait_seconds > 0:
                    next_time = datetime.fromtimestamp(next_check).strftime("%H:%M:%S")
                    self.log(f"\n💤 Sleeping for {wait_seconds:.0f}s... Next check at {next_time}")
                    time.sleep(wait_seconds)

                # 执行监控循环
                self.monitor_cycle()

            except KeyboardInterrupt:
                self.log("\n\n🛑 Monitoring stopped by user", "WARNING")
                self.log(f"📊 Final stats: {self.run_count} runs, {self.fix_count} fixes")
                break
            except Exception as e:
                self.log(f"❌ Unexpected error: {str(e)}", "ERROR")
                self.log("   Will retry in 60 seconds...")
                time.sleep(60)

if __name__ == "__main__":
    monitor = SEOMonitor()
    monitor.run_continuous()
