#!/usr/bin/env python3
"""
Fully Automated Email Campaign System
完全自动化的邮件营销系统

完整流程（无需人工干预）：
1. 自动从项目目录生成关键词
2. 在Twitter上自动寻找潜在客户
3. 自动验证邮箱地址
4. 自动发送邮件（带随机延迟）
5. 自动追踪转化
6. 24小时后自动跟进

使用方法：
    python fully_automated_campaign.py --auto-generate --leads 100
    或
    python fully_automated_campaign.py --product-file product.md --leads 100
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add src directory to Python path
SCRIPT_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(SCRIPT_DIR / "src"))
sys.path.insert(0, str(SCRIPT_DIR))

try:
    from src.ultimate_email_finder_hunter import UltimateEmailFinderWithHunter
    from src.email_campaign_manager import EmailCampaignManager
except ImportError:
    # Try without src prefix (if running from src directory)
    from ultimate_email_finder_hunter import UltimateEmailFinderWithHunter
    from email_campaign_manager import EmailCampaignManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def auto_generate_product_keywords(project_dir: str = ".") -> str:
    """
    自动从项目目录生成产品关键词

    扫描项目中的：
    - README.md
    - package.json
    - setup.py
    - 其他文档文件

    返回生成的关键词文件路径
    """
    logger.info("\n🔍 Auto-generating keywords from project directory...")

    # 查找项目文档
    doc_files = []
    for pattern in ['README.md', 'README.txt', 'DESCRIPTION.md', 'package.json', 'setup.py']:
        file_path = Path(project_dir) / pattern
        if file_path.exists():
            doc_files.append(str(file_path))
            logger.info(f"   Found: {file_path}")

    if not doc_files:
        logger.warning("   ⚠️  No project documentation found. Using default keywords.")
        # 创建默认产品描述
        default_content = """
Product: AI-Powered Tool
Description: An innovative AI solution that helps users achieve their goals.
Target Audience: Tech professionals, developers, entrepreneurs
Keywords: AI, automation, productivity, innovation
"""
        default_file = "auto_generated_product.md"
        with open(default_file, 'w') as f:
            f.write(default_content)
        return default_file

    # 读取并合并内容
    combined_content = []
    for doc_file in doc_files:
        try:
            with open(doc_file, 'r', encoding='utf-8') as f:
                combined_content.append(f"# From {doc_file}\n")
                combined_content.append(f.read())
        except Exception as e:
            logger.warning(f"   ⚠️  Could not read {doc_file}: {e}")

    # 保存合并内容
    output_file = "auto_generated_product.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n\n".join(combined_content))

    logger.info(f"   ✅ Generated: {output_file}")
    return output_file


def run_fully_automated_campaign(
    product_file: str,
    num_leads: int = 100,
    seeds: int = 5,
    skip_confirmation: bool = True,
    auto_followup: bool = True
):
    """
    运行完全自动化的营销活动

    Args:
        product_file: 产品描述文件
        num_leads: 要获取的leads数量
        seeds: Twitter种子账号数量
        skip_confirmation: 是否跳过人工确认
        auto_followup: 是否自动设置跟进任务
    """
    logger.info("="*70)
    logger.info("🚀 FULLY AUTOMATED EMAIL CAMPAIGN SYSTEM")
    logger.info("="*70)
    logger.info(f"\n📋 Configuration:")
    logger.info(f"   Product file: {product_file}")
    logger.info(f"   Target leads: {num_leads}")
    logger.info(f"   Seed accounts: {seeds}")
    logger.info(f"   Auto-confirm: {skip_confirmation}")
    logger.info(f"   Auto-followup: {auto_followup}")

    # Step 1: Find leads from Twitter
    logger.info("\n" + "="*70)
    logger.info("📊 STEP 1: Finding Leads from Twitter")
    logger.info("="*70)

    # Use auth.json from script directory
    auth_file = str(SCRIPT_DIR / "auth.json")

    # Use Hunter.io enhanced email finder
    finder = UltimateEmailFinderWithHunter(
        auth_file=auth_file,
        enable_email_verification=True,  # Will use Hunter.io verifier
        smtp_timeout=10
    )

    summary = finder.run(
        product_doc=product_file,
        followers_per=num_leads // seeds,
        max_seeds=seeds
    )

    logger.info(f"\n✅ Lead Discovery Complete!")
    logger.info(f"   Total leads found: {summary['total_leads']}")
    logger.info(f"   With verified emails: {summary['leads_with_email']}")
    logger.info(f"   Success rate: {summary['leads_with_email']/summary['total_leads']*100:.1f}%")

    # Step 2: Send emails (auto-confirm if enabled)
    if summary['leads_with_email'] > 0:
        logger.info("\n" + "="*70)
        logger.info("📧 STEP 2: Starting Email Campaign")
        logger.info("="*70)

        # Auto-confirm or ask
        if skip_confirmation:
            logger.info(f"\n✅ Auto-confirming: Sending to {summary['leads_with_email']} leads...")
            send_emails = True
        else:
            response = input(f"\n⚠️  Send emails to {summary['leads_with_email']} leads? (y/n): ")
            send_emails = response.lower() == 'y'

        if send_emails:
            # Initialize campaign manager with absolute path to config
            email_config_file = str(SCRIPT_DIR / "email_config.json")
            campaign_manager = EmailCampaignManager(config_file=email_config_file)

            # Get leads with emails
            leads_with_emails = [
                lead for lead in finder.all_leads
                if lead.get('all_contacts', {}).get('emails')
            ]

            # Start campaign
            logger.info(f"\n📤 Sending emails (with human-like delays)...")
            campaign_manager.start_campaign(leads_with_emails)

            logger.info("\n" + "="*70)
            logger.info("✅ EMAIL CAMPAIGN COMPLETED!")
            logger.info("="*70)
            logger.info(f"\n📊 Results:")
            logger.info(f"   Emails sent: {summary['leads_with_email']}")
            logger.info(f"   Database: campaign_tracking.db")

            # Step 3: Setup auto-followup
            if auto_followup:
                logger.info("\n" + "="*70)
                logger.info("🔄 STEP 3: Setting Up Auto-Followup")
                logger.info("="*70)

                setup_auto_followup()

            # Show next steps
            logger.info("\n" + "="*70)
            logger.info("📋 NEXT STEPS")
            logger.info("="*70)
            logger.info("\n1. Monitor conversions:")
            logger.info("   python src/email_campaign_manager.py --stats")
            logger.info("\n2. Check database:")
            logger.info("   sqlite3 campaign_tracking.db 'SELECT * FROM campaigns'")
            logger.info("\n3. Manual follow-up check (if cron not set):")
            logger.info("   python src/email_campaign_manager.py --check-followups")

            logger.info("\n" + "="*70)
            logger.info("🎉 FULLY AUTOMATED CAMPAIGN COMPLETE!")
            logger.info("="*70)

        else:
            logger.info("\n❌ Campaign cancelled by user")
    else:
        logger.info("\n⚠️  No leads with emails found. Cannot start campaign.")


def setup_auto_followup():
    """
    设置自动跟进（cron job或后台任务）
    """
    logger.info("\n⏰ Setting up automatic follow-up checks...")

    # 检查操作系统
    import platform
    system = platform.system()

    project_dir = os.getcwd()

    if system in ['Linux', 'Darwin']:  # Linux or macOS
        cron_command = f"0 */6 * * * cd {project_dir} && python3 src/email_campaign_manager.py --check-followups >> email_campaign.log 2>&1"

        logger.info("\n✅ Cron job command generated:")
        logger.info(f"   {cron_command}")
        logger.info("\n💡 To install, run:")
        logger.info("   crontab -e")
        logger.info("   Then add the above line")

        # 可选：自动添加到crontab
        try:
            import subprocess

            # 获取现有crontab
            result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            existing_cron = result.stdout if result.returncode == 0 else ""

            # 检查是否已存在
            if 'check-followups' in existing_cron:
                logger.info("   ℹ️  Cron job already exists, skipping...")
            else:
                response = input("\n❓ Auto-install cron job? (y/n): ")
                if response.lower() == 'y':
                    # 添加新的cron job
                    new_cron = existing_cron + "\n" + cron_command + "\n"
                    proc = subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE)
                    proc.communicate(new_cron.encode())
                    logger.info("   ✅ Cron job installed successfully!")
                else:
                    logger.info("   ℹ️  Skipped auto-install. You can add it manually.")
        except Exception as e:
            logger.warning(f"   ⚠️  Could not auto-install cron: {e}")
            logger.info("   Please add the cron job manually (see above)")

    elif system == 'Windows':
        # Windows Task Scheduler
        logger.info("\n💡 For Windows, create a Scheduled Task:")
        logger.info("   1. Open Task Scheduler")
        logger.info("   2. Create Basic Task")
        logger.info(f"   3. Action: python {project_dir}\\src\\email_campaign_manager.py --check-followups")
        logger.info("   4. Trigger: Every 6 hours")

    else:
        logger.warning(f"   ⚠️  Unknown system: {system}")


def main():
    parser = argparse.ArgumentParser(
        description='Fully Automated Email Campaign System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Auto-generate keywords from project and run campaign
  python fully_automated_campaign.py --auto-generate --leads 100

  # Use existing product file
  python fully_automated_campaign.py --product-file product.md --leads 50

  # With manual confirmation
  python fully_automated_campaign.py --auto-generate --leads 100 --no-auto-confirm

  # Without auto-followup setup
  python fully_automated_campaign.py --auto-generate --leads 100 --no-auto-followup
        '''
    )

    # Product source
    product_group = parser.add_mutually_exclusive_group(required=True)
    product_group.add_argument(
        '--auto-generate',
        action='store_true',
        help='Auto-generate keywords from project directory'
    )
    product_group.add_argument(
        '--product-file',
        type=str,
        help='Path to product description file'
    )

    # Campaign settings
    parser.add_argument(
        '--leads',
        type=int,
        default=100,
        help='Number of leads to find (default: 100)'
    )
    parser.add_argument(
        '--seeds',
        type=int,
        default=5,
        help='Number of seed Twitter accounts (default: 5)'
    )

    # Automation settings
    parser.add_argument(
        '--no-auto-confirm',
        action='store_true',
        help='Require manual confirmation before sending emails'
    )
    parser.add_argument(
        '--no-auto-followup',
        action='store_true',
        help='Skip automatic follow-up setup'
    )

    # Project directory
    parser.add_argument(
        '--project-dir',
        type=str,
        default='.',
        help='Project directory for auto-generation (default: current directory)'
    )

    args = parser.parse_args()

    try:
        # Determine product file
        if args.auto_generate:
            product_file = auto_generate_product_keywords(args.project_dir)
        else:
            product_file = args.product_file
            if not os.path.exists(product_file):
                logger.error(f"❌ Product file not found: {product_file}")
                sys.exit(1)

        # Run automated campaign
        run_fully_automated_campaign(
            product_file=product_file,
            num_leads=args.leads,
            seeds=args.seeds,
            skip_confirmation=not args.no_auto_confirm,
            auto_followup=not args.no_auto_followup
        )

    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Campaign interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
