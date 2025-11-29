"""
DistroFlow CLI - Unified command-line interface

Usage:
    distroflow launch --platforms twitter,reddit --content "My post"
    distroflow schedule --workflow build-in-public --frequency daily
    distroflow setup
"""

import click
import asyncio
import json
import logging
from pathlib import Path
from typing import Optional, List

from distroflow import __version__
from distroflow.core.scheduler import Scheduler, Frequency
from distroflow.core.content_transformer import ContentTransformer, Platform
from distroflow.platforms.base import AuthConfig
from distroflow.platforms.twitter import TwitterPlatform
from distroflow.platforms.reddit import RedditPlatform
from distroflow.platforms.hackernews import HackerNewsPlatform
from distroflow.platforms.instagram import InstagramPlatform

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("distroflow")


# Platform registry
PLATFORMS = {
    "twitter": TwitterPlatform,
    "reddit": RedditPlatform,
    "hackernews": HackerNewsPlatform,
    "instagram": InstagramPlatform,
}


def get_auth_config(platform_name: str) -> Optional[AuthConfig]:
    """Load authentication config for a platform."""
    auth_file = Path.home() / ".distroflow" / f"{platform_name}_auth.json"

    if not auth_file.exists():
        # Try legacy auth files
        legacy_files = {
            "twitter": "auth.json",
            "reddit": "reddit_auth.json",
            "hackernews": "hackernews_auth.json",
            "instagram": "platforms_auth.json",
        }
        legacy_path = Path(legacy_files.get(platform_name, ""))
        if legacy_path.exists():
            auth_file = legacy_path
        else:
            return None

    try:
        with open(auth_file) as f:
            json.load(f)  # Validate JSON format
            return AuthConfig(
                auth_type="cookies", credentials={"cookie_path": str(auth_file)}
            )
    except Exception as e:
        logger.error(f"Error loading auth for {platform_name}: {e}")
        return None


async def post_to_platforms(
    platforms: List[str],
    content: str,
    title: Optional[str] = None,
    url: Optional[str] = None,
):
    """Post content to multiple platforms."""
    transformer = ContentTransformer()
    results = []

    for platform_name in platforms:
        logger.info(f"\n{'='*50}")
        logger.info(f"🚀 Posting to {platform_name.upper()}")
        logger.info(f"{'='*50}")

        # Get platform class
        platform_class = PLATFORMS.get(platform_name)
        if not platform_class:
            logger.error(f"❌ Unknown platform: {platform_name}")
            continue

        # Initialize platform
        platform = platform_class()

        # Setup auth
        auth_config = get_auth_config(platform_name)
        if not auth_config:
            logger.error(f"❌ No auth config found for {platform_name}")
            logger.info(f"   Run: distroflow setup {platform_name}")
            continue

        auth_success = await platform.setup_auth(auth_config)
        if not auth_success:
            logger.error(f"❌ Authentication failed for {platform_name}")
            continue

        # Transform content for platform
        try:
            platform_enum = Platform(platform_name)
        except ValueError:
            platform_enum = Platform.TWITTER  # Default

        transformed = transformer.transform(
            content=content, platform=platform_enum, title=title, url=url
        )

        # Post
        result = await platform.post(
            content=transformed["content"], title=transformed.get("title"), url=url
        )

        results.append(result)

        if result.success:
            logger.info(f"✅ Posted to {platform_name} successfully")
        else:
            logger.error(f"❌ Failed to post to {platform_name}: {result.error}")

        # Cleanup
        await platform.cleanup()

    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("📊 SUMMARY")
    logger.info(f"{'='*50}")
    successful = sum(1 for r in results if r.success)
    logger.info(f"✅ Successful: {successful}/{len(results)}")
    logger.info(f"❌ Failed: {len(results) - successful}/{len(results)}")


@click.group()
@click.version_option(version=__version__)
def cli():
    """
    DistroFlow - Cross-platform distribution automation

    Automate content distribution across Twitter, Reddit, HackerNews,
    Instagram, and more using AI-powered browser automation.
    """
    pass


@cli.command()
@click.option(
    "--platforms", "-p", required=True, help="Comma-separated platforms (e.g., twitter,reddit)"
)
@click.option("--content", "-c", required=True, help="Content to post")
@click.option("--title", "-t", help="Post title (for platforms that need it)")
@click.option("--url", "-u", help="URL to include")
def launch(platforms: str, content: str, title: Optional[str], url: Optional[str]):
    """
    Launch content on multiple platforms immediately.

    Example:
        distroflow launch -p twitter,reddit,hackernews \\
            -c "My new project!" -t "Show HN: Project Name"
    """
    platform_list = [p.strip() for p in platforms.split(",")]

    logger.info(f"🚀 Launching to: {', '.join(platform_list)}")
    logger.info(f"📝 Content: {content[:100]}...")

    asyncio.run(post_to_platforms(platform_list, content, title, url))


@cli.command()
@click.option("--workflow", "-w", required=True, help="Workflow name (e.g., build-in-public)")
@click.option("--platforms", "-p", required=True, help="Comma-separated platforms")
@click.option(
    "--frequency", "-f", type=click.Choice(["once", "daily", "weekly", "monthly"]), default="daily"
)
@click.option("--time", help="Time to run (HH:MM format, 24h)")
@click.option("--content", "-c", help="Content template")
def schedule(
    workflow: str, platforms: str, frequency: str, time: Optional[str], content: Optional[str]
):
    """
    Schedule a recurring workflow.

    Example:
        distroflow schedule -w build-in-public -p twitter,linkedin -f daily --time "09:00"
    """
    platform_list = [p.strip() for p in platforms.split(",")]
    freq = Frequency(frequency)

    scheduler = Scheduler()
    task_id = scheduler.schedule_task(
        workflow_name=workflow, platforms=platform_list, frequency=freq, content=content
    )

    logger.info(f"✅ Scheduled task {task_id}: {workflow}")
    logger.info(f"   Platforms: {', '.join(platform_list)}")
    logger.info(f"   Frequency: {frequency}")
    if time:
        logger.info(f"   Time: {time}")


@cli.command()
@click.argument("platform", required=False)
def setup(platform: Optional[str]):
    """
    Setup authentication for platforms.

    Example:
        distroflow setup twitter
        distroflow setup  # Interactive setup for all platforms
    """
    if platform:
        logger.info("🔐 Setting up authentication for %s", platform)
        logger.info("\nPlease follow these steps:")
        logger.info("1. Login to %s in a browser", platform)
        logger.info("2. Copy your cookies")
        logger.info("3. Save to: ~/.distroflow/%s_auth.json", platform)
        logger.info("\nFormat:")
        logger.info(
            """{
    "cookies": [
        {"name": "sessionid", "value": "..."},
        ...
    ]
}"""
        )
    else:
        logger.info("🔐 Interactive setup coming soon!")
        logger.info("For now, manually set up auth files:")
        for p in PLATFORMS.keys():
            logger.info(f"  - ~/.distroflow/{p}_auth.json")


@cli.command()
@click.option("--status", type=click.Choice(["pending", "running", "completed", "failed"]))
def list_tasks(status: Optional[str]):
    """
    List scheduled tasks.

    Example:
        distroflow list-tasks
        distroflow list-tasks --status pending
    """
    from distroflow.core.scheduler import TaskStatus

    scheduler = Scheduler()
    task_status = TaskStatus(status) if status else None
    tasks = scheduler.list_tasks(task_status)

    if not tasks:
        logger.info("📋 No tasks found")
        return

    logger.info(f"📋 Found {len(tasks)} task(s):\n")
    for task in tasks:
        logger.info(f"  ID: {task['id']}")
        logger.info(f"  Workflow: {task['workflow_name']}")
        logger.info(f"  Platforms: {', '.join(task['platforms'])}")
        logger.info(f"  Frequency: {task['frequency']}")
        logger.info(f"  Next run: {task['next_run']}")
        logger.info(f"  Status: {task['status']}")
        logger.info("")


@cli.command()
@click.argument("task_id", type=int)
def cancel(task_id: int):
    """
    Cancel a scheduled task.

    Example:
        distroflow cancel 123
    """
    scheduler = Scheduler()
    scheduler.cancel_task(task_id)
    logger.info(f"✅ Task {task_id} cancelled")


@cli.command()
def daemon():
    """
    Run the scheduler daemon.

    This will continuously check for and execute scheduled tasks.
    Press Ctrl+C to stop.
    """
    logger.info("🚀 Starting DistroFlow daemon...")

    async def executor(workflow_name, platforms, content, config):
        """Execute scheduled task."""
        logger.info(f"⏰ Executing scheduled task: {workflow_name}")
        await post_to_platforms(platforms, content or "Scheduled post")

    scheduler = Scheduler()

    try:
        asyncio.run(scheduler.run_daemon(executor))
    except KeyboardInterrupt:
        logger.info("\n⏹️  Daemon stopped by user")
        scheduler.stop_daemon()


@cli.command()
def version():
    """Show version information."""
    logger.info(f"DistroFlow v{__version__}")
    logger.info("Open-source cross-platform distribution infrastructure")
    logger.info("https://github.com/yourusername/distroflow")


@cli.command()
@click.option("--host", default="127.0.0.1", help="Server host")
@click.option("--port", default=8000, help="Server port")
def serve(host: str, port: int):
    """
    Start the API server for browser extension.

    Example:
        distroflow serve
        distroflow serve --host 0.0.0.0 --port 8080
    """
    logger.info(f"🚀 Starting DistroFlow API server on {host}:{port}")
    logger.info("📡 API docs available at: http://{host}:{port}/docs")
    logger.info("🔌 WebSocket endpoint: ws://{host}:{port}/ws")

    from distroflow.api.server import start_server

    start_server(host=host, port=port)


if __name__ == "__main__":
    cli()
