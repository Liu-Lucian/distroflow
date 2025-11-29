#!/usr/bin/env python3
"""
Substack Autopilot - Combined Publishing + Comment Farming
Runs both systems in coordination for continuous organic growth
"""

import sys
sys.path.insert(0, 'src')
import subprocess
import time
import json
import os
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


# Autopilot Configuration
CONFIG = {
    # Comment farming
    "comment_runs_per_day": 3,  # How many times to run comment farmer per day
    "comment_run_times": ["09:00", "14:00", "20:00"],  # Specific times to run

    # Publishing schedule (already handled by schedule_substack_posts.py)
    "publishing_enabled": True,

    # Safety limits
    "max_comments_per_day": 15,
    "min_delay_between_runs": 180,  # Minimum 3 hours between runs (in minutes)
}


def get_today_comment_count():
    """Count how many comments were posted today"""
    try:
        with open('substack_commented_posts.json', 'r') as f:
            history = json.load(f)

        today = datetime.now().date()
        today_comments = [
            p for p in history
            if datetime.fromisoformat(p['commented_at']).date() == today
        ]
        return len(today_comments)
    except FileNotFoundError:
        return 0


def should_run_comments():
    """Check if we should run comment farmer based on limits"""
    today_count = get_today_comment_count()

    if today_count >= CONFIG['max_comments_per_day']:
        logger.warning(f"⚠️  Already posted {today_count} comments today (limit: {CONFIG['max_comments_per_day']})")
        return False

    return True


def run_comment_farmer():
    """Run the comment farming script"""
    logger.info("\n" + "="*80)
    logger.info("🌾 Starting Comment Farming Session")
    logger.info("="*80)

    if not should_run_comments():
        logger.info("⏭️  Skipping comment farming (daily limit reached)")
        return

    try:
        # Run with live output (no capture_output)
        result = subprocess.run(
            ['python3', 'substack_comment_farmer.py'],
            env=os.environ.copy()
        )

        if result.returncode == 0:
            logger.info("\n✅ Comment farming completed successfully")
        else:
            logger.error(f"\n❌ Comment farming failed with code {result.returncode}")

    except Exception as e:
        logger.error(f"❌ Error running comment farmer: {e}")


def check_scheduled_posts():
    """Check if there are scheduled posts coming up"""
    try:
        # This is just informational - scheduling is handled by schedule_substack_posts.py
        logger.info("\n📅 Scheduled Posts Status:")
        logger.info("   (Check your Substack dashboard → Posts → Scheduled)")
        logger.info("   Run 'python3 schedule_substack_posts.py' to schedule more posts")
    except Exception as e:
        logger.error(f"Error checking scheduled posts: {e}")


def run_autopilot_session():
    """Run one complete autopilot session"""
    logger.info("\n" + "="*80)
    logger.info("🤖 Substack Autopilot Session")
    logger.info("="*80)
    logger.info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Check daily stats
    today_comments = get_today_comment_count()
    logger.info(f"📊 Today's comments: {today_comments}/{CONFIG['max_comments_per_day']}")

    # Run comment farming
    run_comment_farmer()

    # Check publishing status
    if CONFIG['publishing_enabled']:
        check_scheduled_posts()

    logger.info("\n" + "="*80)
    logger.info("✅ Autopilot session complete")
    logger.info("="*80)


def run_continuous():
    """Run autopilot continuously"""
    logger.info("="*80)
    logger.info("🚀 Substack Autopilot - Continuous Mode")
    logger.info("="*80)
    logger.info("Configuration:")
    logger.info(f"  • Comment runs per day: {CONFIG['comment_runs_per_day']}")
    logger.info(f"  • Max comments per day: {CONFIG['max_comments_per_day']}")
    logger.info(f"  • Run times: {', '.join(CONFIG['comment_run_times'])}")
    logger.info("")
    logger.info("Press Ctrl+C to stop")
    logger.info("="*80)

    last_run = None

    while True:
        try:
            current_time = datetime.now()
            current_time_str = current_time.strftime("%H:%M")

            # Check if it's time to run
            should_run = False
            for run_time in CONFIG['comment_run_times']:
                # Check if current time matches (within 1 minute)
                run_hour, run_minute = map(int, run_time.split(':'))
                if current_time.hour == run_hour and abs(current_time.minute - run_minute) <= 1:
                    # Make sure we haven't run in the last hour
                    if last_run is None or (current_time - last_run).total_seconds() > 3600:
                        should_run = True
                        break

            if should_run:
                logger.info(f"\n⏰ Scheduled run time: {current_time_str}")
                run_autopilot_session()
                last_run = current_time

                # Sleep for 2 minutes to avoid duplicate runs
                time.sleep(120)
            else:
                # Check every minute
                time.sleep(60)

        except KeyboardInterrupt:
            logger.info("\n\n⏹️  Autopilot stopped by user")
            break
        except Exception as e:
            logger.error(f"❌ Error in continuous mode: {e}")
            logger.info("⏳ Waiting 5 minutes before retry...")
            time.sleep(300)


def run_once():
    """Run autopilot once and exit"""
    run_autopilot_session()


def main():
    """Main entry point"""
    import sys

    if not os.environ.get('OPENAI_API_KEY'):
        logger.error("❌ OPENAI_API_KEY not set")
        logger.info("Set it with: export OPENAI_API_KEY='sk-proj-...'")
        return

    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--continuous":
            run_continuous()
        elif sys.argv[1] == "--once":
            run_once()
        elif sys.argv[1] == "--help":
            print("""
Substack Autopilot - Combined Publishing + Comment Farming

Usage:
  python3 substack_autopilot.py              Run once and exit
  python3 substack_autopilot.py --once       Run once and exit (explicit)
  python3 substack_autopilot.py --continuous Run continuously
  python3 substack_autopilot.py --help       Show this help

Configuration:
  Edit CONFIG dictionary in this file to customize:
  - comment_runs_per_day: How many times to run per day
  - comment_run_times: What times to run (24-hour format)
  - max_comments_per_day: Daily comment limit

For scheduled publishing:
  Run separately: python3 schedule_substack_posts.py

For manual comment farming:
  Run separately: python3 substack_comment_farmer.py
            """)
        else:
            logger.error(f"Unknown argument: {sys.argv[1]}")
            logger.info("Use --help for usage information")
    else:
        # Default: run once
        run_once()


if __name__ == "__main__":
    main()
