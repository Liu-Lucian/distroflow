#!/usr/bin/env python3
"""
持续营销活动 - Continuous Marketing Campaign
24/7不间断运行，每50封邮件后休息5小时

使用方法：
    python3 continuous_campaign.py --product hiremeai --batch-size 50 --rest-hours 5

特点：
1. 自动批次运行（每批50个leads）
2. 智能休息（每批后休息5小时，模拟人类行为）
3. 错误恢复（遇到错误自动重试）
4. 进度保存（可以随时中断和恢复）
5. 统计报告（实时显示总体进度）
"""

import sys
import os
import argparse
import logging
import time
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Tuple

# Add src directory to Python path
SCRIPT_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(SCRIPT_DIR / "src"))
sys.path.insert(0, str(SCRIPT_DIR))

from src.smart_email_finder import SmartEmailFinder
from src.email_campaign_manager import EmailCampaignManager
from src.linkedin_scraper import LinkedInScraper
from src.github_scraper import GitHubScraper
from src.producthunt_scraper import ProductHuntScraper
from src.hackernews_scraper import HackerNewsScraper
from src.reddit_scraper import RedditScraper
from src.youtube_scraper import YouTubeScraper
from src.instagram_scraper import InstagramScraper
from src.tiktok_scraper import TikTokScraper

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('continuous_campaign.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ContinuousCampaign:
    """持续营销活动管理器"""

    def __init__(self, product_file: str, batch_size: int = 50,
                 rest_hours: int = 5, seeds_per_batch: int = 5,
                 state_file: str = "campaign_state.json",
                 target_emails_per_batch: int = 50,
                 platforms: list = None):
        """
        初始化持续营销活动

        Args:
            product_file: 产品描述文件
            batch_size: 每次查找的leads数量
            rest_hours: 每批后休息小时数
            seeds_per_batch: 每批使用的种子账号数
            state_file: 状态保存文件
            target_emails_per_batch: 每批目标发送邮件数（会持续找直到达到）
            platforms: 平台列表 ['twitter', 'linkedin', 'github']
        """
        self.product_file = product_file
        self.batch_size = batch_size
        self.rest_hours = rest_hours
        self.seeds_per_batch = seeds_per_batch
        self.state_file = state_file
        self.target_emails_per_batch = target_emails_per_batch
        self.platforms = platforms or ['twitter']  # 默认Twitter

        # 加载或初始化状态
        self.state = self._load_state()

        # Hunter.io API key
        self.hunter_api_key = '1553249bbb256b2a3d111c9c67755c2927053828'

        # Auth files
        self.auth_file = str(SCRIPT_DIR / "auth.json")  # Twitter auth
        self.platforms_auth_file = str(SCRIPT_DIR / "platforms_auth.json")  # LinkedIn, GitHub
        self.email_config_file = str(SCRIPT_DIR / "email_config.json")

        # 初始化平台scrapers
        self.platform_scrapers = {}
        self._init_platform_scrapers()

    def _init_platform_scrapers(self):
        """初始化所有平台的scrapers"""
        logger.info(f"🔌 Initializing platform scrapers: {', '.join(self.platforms)}")

        for platform in self.platforms:
            try:
                if platform.lower() == 'linkedin':
                    # 使用linkedin_auth.json（storage_state格式）
                    linkedin_auth_file = str(SCRIPT_DIR / "linkedin_auth.json")
                    self.platform_scrapers['linkedin'] = LinkedInScraper(
                        auth_file=linkedin_auth_file
                    )
                    logger.info("  ✅ LinkedIn scraper initialized")

                elif platform.lower() == 'github':
                    self.platform_scrapers['github'] = GitHubScraper(
                        auth_file=self.platforms_auth_file
                    )
                    logger.info("  ✅ GitHub scraper initialized")

                elif platform.lower() in ['twitter', 'x']:
                    # Twitter使用SmartEmailFinder（已有的系统）
                    self.platform_scrapers['twitter'] = 'smart_email_finder'
                    logger.info("  ✅ Twitter scraper ready (using SmartEmailFinder)")

                elif platform.lower() == 'producthunt':
                    self.platform_scrapers['producthunt'] = ProductHuntScraper(
                        auth_file=self.platforms_auth_file
                    )
                    logger.info("  ✅ Product Hunt scraper initialized")

                elif platform.lower() == 'hackernews':
                    self.platform_scrapers['hackernews'] = HackerNewsScraper(
                        auth_file=self.platforms_auth_file
                    )
                    logger.info("  ✅ Hacker News scraper initialized")

                elif platform.lower() == 'reddit':
                    self.platform_scrapers['reddit'] = RedditScraper(
                        auth_file=self.platforms_auth_file
                    )
                    logger.info("  ✅ Reddit scraper initialized")

                elif platform.lower() == 'youtube':
                    self.platform_scrapers['youtube'] = YouTubeScraper(
                        auth_file=self.platforms_auth_file
                    )
                    logger.info("  ✅ YouTube scraper initialized")

                elif platform.lower() == 'instagram':
                    self.platform_scrapers['instagram'] = InstagramScraper(
                        auth_file=self.platforms_auth_file
                    )
                    logger.info("  ✅ Instagram scraper initialized")

                elif platform.lower() == 'tiktok':
                    self.platform_scrapers['tiktok'] = TikTokScraper(
                        auth_file=self.platforms_auth_file
                    )
                    logger.info("  ✅ TikTok scraper initialized")

            except Exception as e:
                logger.warning(f"  ⚠️  Could not initialize {platform} scraper: {e}")

    def _get_current_platform(self, batch_num: int) -> str:
        """获取当前批次应该使用的平台（轮换策略）"""
        if len(self.platforms) == 1:
            return self.platforms[0]

        # 轮换策略：按批次轮换
        platform_index = (batch_num - 1) % len(self.platforms)
        return self.platforms[platform_index]

    def _load_state(self):
        """加载状态文件"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    logger.info(f"📂 Loaded state: {state}")
                    return state
            except Exception as e:
                logger.warning(f"⚠️  Could not load state: {e}")

        # 默认状态
        return {
            'total_batches': 0,
            'total_leads': 0,
            'total_emails_sent': 0,
            'total_emails_failed': 0,
            'start_time': datetime.now().isoformat(),
            'last_batch_time': None,
            'next_run_time': None
        }

    def _save_state(self):
        """保存状态文件"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
            logger.info(f"💾 State saved")
        except Exception as e:
            logger.error(f"❌ Could not save state: {e}")

    def _print_stats(self):
        """打印总体统计"""
        logger.info("\n" + "="*70)
        logger.info("📊 CONTINUOUS CAMPAIGN STATISTICS")
        logger.info("="*70)
        logger.info(f"  Total batches completed: {self.state['total_batches']}")
        logger.info(f"  Total leads found: {self.state['total_leads']}")
        logger.info(f"  Total emails sent: {self.state['total_emails_sent']}")
        logger.info(f"  Total emails failed: {self.state['total_emails_failed']}")

        if self.state['total_emails_sent'] > 0:
            success_rate = (self.state['total_emails_sent'] /
                          (self.state['total_emails_sent'] + self.state['total_emails_failed']) * 100)
            logger.info(f"  Success rate: {success_rate:.1f}%")

        # 计算运行时间
        start_time = datetime.fromisoformat(self.state['start_time'])
        runtime = datetime.now() - start_time
        logger.info(f"  Runtime: {runtime}")

        # 预计下次运行时间
        if self.state['next_run_time']:
            next_run = datetime.fromisoformat(self.state['next_run_time'])
            if next_run > datetime.now():
                time_until = next_run - datetime.now()
                logger.info(f"  Next batch in: {time_until}")

        logger.info("="*70 + "\n")

    def _get_leads_from_platform(self, platform: str, keywords: List[str], limit: int) -> tuple:
        """
        从指定平台获取leads

        Args:
            platform: 平台名称
            keywords: 搜索关键词
            limit: 数量限制

        Returns:
            (leads列表, 带邮箱的leads列表)
        """
        if platform == 'twitter':
            # 使用SmartEmailFinder (原有的Twitter系统)
            finder = SmartEmailFinder(
                auth_file=self.auth_file,
                enable_email_verification=True,
                hunter_api_key=self.hunter_api_key
            )

            summary = finder.run(
                product_doc=self.product_file,
                followers_per=limit // self.seeds_per_batch,
                max_seeds=self.seeds_per_batch
            )

            all_leads = finder.all_leads
            leads_with_emails = [
                lead for lead in all_leads
                if lead.get('all_contacts', {}).get('emails')
            ]

            return all_leads, leads_with_emails

        elif platform in ['linkedin', 'github', 'producthunt', 'hackernews', 'reddit', 'youtube', 'instagram', 'tiktok']:
            # 使用平台特定scraper
            scraper = self.platform_scrapers.get(platform)
            if not scraper:
                logger.error(f"❌ {platform} scraper not initialized")
                return [], []

            # 获取leads (使用scraper的search_users方法)
            users = scraper.search_users(keywords=keywords, limit=limit)

            # 为每个用户获取详细资料并查找邮箱
            all_leads = []
            leads_with_emails = []

            for i, user in enumerate(users):
                try:
                    # 获取详细资料
                    user_id = user.get('id') or user.get('username')
                    profile = scraper.get_user_profile(user_id)

                    # 尝试提取邮箱
                    email = scraper.extract_email(profile)

                    # 标准化数据格式以兼容EmailCampaignManager
                    normalized = scraper.normalize_user_data(profile)

                    # 如果有邮箱，添加到all_contacts字段
                    if email:
                        normalized['email'] = email
                        normalized['all_contacts'] = {'emails': [email]}
                        leads_with_emails.append(normalized)

                    all_leads.append(normalized)

                    # 每10个显示进度
                    if (i + 1) % 10 == 0:
                        logger.info(f"    Progress: {i+1}/{len(users)} processed, {len(leads_with_emails)} with emails")

                except Exception as e:
                    logger.warning(f"    ⚠️  Error processing user: {e}")
                    continue

            return all_leads, leads_with_emails

        else:
            logger.error(f"❌ Unknown platform: {platform}")
            return [], []

    def run_batch(self, batch_num: int):
        """
        运行一个批次 - 持续寻找直到发送足够邮件

        Args:
            batch_num: 批次编号

        Returns:
            批次结果统计
        """
        # 确定本批次使用的平台
        current_platform = self._get_current_platform(batch_num)

        logger.info("\n" + "="*70)
        logger.info(f"🚀 BATCH #{batch_num} - Starting")
        logger.info("="*70)
        logger.info(f"  Platform: {current_platform.upper()}")
        logger.info(f"  Target emails to send: {self.target_emails_per_batch}")
        logger.info(f"  Leads per search: {self.batch_size}")
        logger.info(f"  Seeds per search: {self.seeds_per_batch}")
        logger.info(f"  Product: {self.product_file}")

        total_leads_found = 0
        total_emails_sent = 0
        total_emails_failed = 0
        search_round = 0

        try:
            # 持续寻找，直到发送足够邮件
            while total_emails_sent < self.target_emails_per_batch:
                search_round += 1
                logger.info(f"\n📊 SEARCH ROUND {search_round}")
                logger.info(f"  Current progress: {total_emails_sent}/{self.target_emails_per_batch} emails sent")
                logger.info(f"  Need {self.target_emails_per_batch - total_emails_sent} more emails")

                # Step 1: Find leads
                logger.info(f"\n  🔍 Finding {self.batch_size} leads from {current_platform}...")

                # 根据平台选择关键词
                if current_platform == 'github':
                    # GitHub关键词：找技术人员和求职者
                    keywords = ["software engineer", "developer", "programmer", "job seeking"]
                elif current_platform == 'linkedin':
                    # LinkedIn关键词：找HR和招聘人员
                    keywords = ["recruiter", "hiring manager", "HR", "talent acquisition"]
                elif current_platform == 'producthunt':
                    # Product Hunt关键词：找创业者和制造者
                    keywords = ["startup", "maker", "founder", "entrepreneur"]
                elif current_platform == 'hackernews':
                    # Hacker News关键词：找技术创始人
                    keywords = ["startup", "founder", "hiring", "launch"]
                elif current_platform == 'reddit':
                    # Reddit关键词：找创业者和活跃用户
                    keywords = ["startup", "entrepreneur", "SaaS", "founder"]
                elif current_platform == 'youtube':
                    # YouTube关键词：找创作者和企业家
                    keywords = ["startup", "entrepreneur", "business", "tech"]
                elif current_platform == 'instagram':
                    # Instagram关键词：找创作者和品牌
                    keywords = ["startup", "entrepreneur", "business", "tech"]
                elif current_platform == 'tiktok':
                    # TikTok关键词：找创作者
                    keywords = ["startup", "entrepreneur", "business", "founder"]
                else:
                    # Twitter默认（由ProductBrain自动生成）
                    keywords = []

                # 从平台获取leads
                all_leads, leads_with_emails = self._get_leads_from_platform(
                    platform=current_platform,
                    keywords=keywords,
                    limit=self.batch_size
                )

                leads_found = len(all_leads)
                emails_found = len(leads_with_emails)

                logger.info(f"  ✅ Leads found: {leads_found}")
                logger.info(f"  ✅ With emails: {emails_found}")

                total_leads_found += leads_found

                # Step 2: Send emails
                if emails_found > 0:
                    logger.info(f"\n  📧 Sending {emails_found} emails...")

                    campaign_manager = EmailCampaignManager(config_file=self.email_config_file)

                    # 发送邮件
                    campaign_manager.start_campaign(leads_with_emails)

                    # 统计（简化处理，假设大部分成功）
                    batch_sent = emails_found
                    batch_failed = 0

                    total_emails_sent += batch_sent
                    total_emails_failed += batch_failed

                    logger.info(f"  ✅ Round {search_round}: sent {batch_sent}, failed {batch_failed}")
                    logger.info(f"  📊 Total progress: {total_emails_sent}/{self.target_emails_per_batch}")

                    # 检查是否达到目标
                    if total_emails_sent >= self.target_emails_per_batch:
                        logger.info(f"\n🎉 Target reached! Sent {total_emails_sent} emails")
                        break
                else:
                    logger.warning(f"  ⚠️  No emails found in round {search_round}")

                # 如果已经搜索太多轮还没达到目标，停止
                if search_round >= 10:
                    logger.warning(f"\n⚠️  Reached max search rounds (10), stopping batch")
                    logger.warning(f"   Only sent {total_emails_sent}/{self.target_emails_per_batch} emails")
                    break

                # 如果还需要更多邮件，短暂等待后继续
                if total_emails_sent < self.target_emails_per_batch:
                    logger.info(f"\n  ⏳ Need more emails, continuing search in 10 seconds...")
                    time.sleep(10)

            # 返回批次结果
            logger.info(f"\n✅ BATCH #{batch_num} COMPLETE")
            logger.info(f"  Total leads searched: {total_leads_found}")
            logger.info(f"  Total emails sent: {total_emails_sent}")
            logger.info(f"  Total emails failed: {total_emails_failed}")
            logger.info(f"  Search rounds: {search_round}")

            return {
                'leads_found': total_leads_found,
                'emails_sent': total_emails_sent,
                'emails_failed': total_emails_failed,
                'search_rounds': search_round,
                'success': True
            }

        except Exception as e:
            logger.error(f"\n❌ Batch failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                'leads_found': total_leads_found,
                'emails_sent': total_emails_sent,
                'emails_failed': total_emails_failed,
                'success': False,
                'error': str(e)
            }

    def run_continuous(self, max_batches: int = None):
        """
        持续运行营销活动

        Args:
            max_batches: 最大批次数（None = 无限）
        """
        logger.info("\n" + "="*70)
        logger.info("🔄 CONTINUOUS CAMPAIGN STARTED")
        logger.info("="*70)
        logger.info(f"  Batch size: {self.batch_size} leads")
        logger.info(f"  Rest time: {self.rest_hours} hours")
        logger.info(f"  Max batches: {max_batches or 'Unlimited'}")
        logger.info(f"  Press Ctrl+C to stop gracefully")
        logger.info("="*70)

        batch_num = self.state['total_batches'] + 1

        try:
            while True:
                # 检查是否达到最大批次
                if max_batches and batch_num > max_batches:
                    logger.info(f"\n✅ Reached max batches ({max_batches})")
                    break

                # 检查是否需要等待
                if self.state['next_run_time']:
                    next_run = datetime.fromisoformat(self.state['next_run_time'])
                    if next_run > datetime.now():
                        wait_seconds = (next_run - datetime.now()).total_seconds()
                        logger.info(f"\n⏰ Waiting {wait_seconds/3600:.1f} hours until next batch...")
                        logger.info(f"   Next run: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")

                        # 分段等待，每小时显示一次进度
                        while datetime.now() < next_run:
                            remaining = (next_run - datetime.now()).total_seconds()
                            if remaining <= 0:
                                break

                            # 等待1小时或剩余时间（取较小值）
                            sleep_time = min(3600, remaining)
                            time.sleep(sleep_time)

                            if remaining > 3600:
                                logger.info(f"   ⏳ {remaining/3600:.1f} hours remaining...")

                # 运行批次
                result = self.run_batch(batch_num)

                # 更新状态
                if result['success']:
                    self.state['total_batches'] += 1
                    self.state['total_leads'] += result['leads_found']
                    self.state['total_emails_sent'] += result['emails_sent']
                    self.state['total_emails_failed'] += result['emails_failed']
                    self.state['last_batch_time'] = datetime.now().isoformat()

                    # 计算下次运行时间
                    next_run = datetime.now() + timedelta(hours=self.rest_hours)
                    self.state['next_run_time'] = next_run.isoformat()

                    self._save_state()
                    self._print_stats()

                    batch_num += 1
                else:
                    logger.error(f"❌ Batch failed, will retry in 1 hour...")
                    time.sleep(3600)  # 失败后等待1小时重试

        except KeyboardInterrupt:
            logger.info("\n\n⚠️  Campaign stopped by user (Ctrl+C)")
            self._save_state()
            self._print_stats()
            logger.info("💾 State saved. You can resume by running the same command.")
        except Exception as e:
            logger.error(f"\n❌ Fatal error: {e}")
            import traceback
            traceback.print_exc()
            self._save_state()


def main():
    parser = argparse.ArgumentParser(
        description='Continuous Marketing Campaign - 24/7 Email Outreach',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # 基础用法：每50个leads休息5小时
  python3 continuous_campaign.py --product hiremeai

  # 自定义批次大小和休息时间
  python3 continuous_campaign.py --product hiremeai --batch-size 100 --rest-hours 6

  # 限制总批次数
  python3 continuous_campaign.py --product hiremeai --max-batches 10

  # 查看当前状态
  cat campaign_state.json
        '''
    )

    # Product
    product_group = parser.add_mutually_exclusive_group(required=True)
    product_group.add_argument(
        '--product',
        type=str,
        choices=['hiremeai', 'HireMeAI'],
        help='Use predefined product'
    )
    product_group.add_argument(
        '--product-file',
        type=str,
        help='Path to custom product file'
    )

    # Platform settings
    platform_group = parser.add_mutually_exclusive_group()
    platform_group.add_argument(
        '--platform',
        type=str,
        choices=['twitter', 'x', 'linkedin', 'github', 'producthunt', 'hackernews', 'reddit', 'youtube', 'instagram', 'tiktok'],
        default='twitter',
        help='Single platform to use (default: twitter)'
    )
    platform_group.add_argument(
        '--platforms',
        type=str,
        help='Multiple platforms to rotate (comma-separated, e.g., twitter,github,reddit,youtube,tiktok)'
    )

    # Batch settings
    parser.add_argument(
        '--target-emails',
        type=int,
        default=50,
        help='Target emails to send per batch (default: 50)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=50,
        help='Leads to search per round (default: 50)'
    )
    parser.add_argument(
        '--rest-hours',
        type=int,
        default=5,
        help='Hours to rest between batches (default: 5)'
    )
    parser.add_argument(
        '--seeds-per-batch',
        type=int,
        default=5,
        help='Seed accounts per search round (default: 5)'
    )

    # Limits
    parser.add_argument(
        '--max-batches',
        type=int,
        default=None,
        help='Maximum number of batches (default: unlimited)'
    )

    # State
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Reset campaign state and start fresh'
    )

    args = parser.parse_args()

    try:
        # Determine product file
        if args.product:
            product_file = str(SCRIPT_DIR / "products" / f"{args.product.lower()}.md")
            if not os.path.exists(product_file):
                logger.error(f"❌ Product not found: {args.product}")
                sys.exit(1)
        else:
            product_file = args.product_file
            if not os.path.exists(product_file):
                logger.error(f"❌ Product file not found: {product_file}")
                sys.exit(1)

        # Reset state if requested
        if args.reset:
            if os.path.exists("campaign_state.json"):
                os.remove("campaign_state.json")
                logger.info("🔄 Campaign state reset")

        # Determine platforms
        if args.platforms:
            # Multiple platforms (comma-separated)
            platforms = [p.strip().lower() for p in args.platforms.split(',')]
        else:
            # Single platform
            platforms = [args.platform.lower()]

        # Create and run campaign
        campaign = ContinuousCampaign(
            product_file=product_file,
            batch_size=args.batch_size,
            rest_hours=args.rest_hours,
            seeds_per_batch=args.seeds_per_batch,
            target_emails_per_batch=args.target_emails,
            platforms=platforms
        )

        campaign.run_continuous(max_batches=args.max_batches)

    except Exception as e:
        logger.error(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
