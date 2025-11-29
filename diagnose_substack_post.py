#!/usr/bin/env python3
"""
Substack发帖诊断脚本
详细显示每一步的执行情况，帮助定位问题
"""

import sys
sys.path.insert(0, 'src')
from playwright.sync_api import sync_playwright
import json
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def diagnose():
    """诊断Substack发帖流程"""

    logger.info("\n" + "="*80)
    logger.info("🔍 Substack Posting Diagnosis")
    logger.info("="*80)

    # Load auth
    try:
        with open('substack_auth.json', 'r') as f:
            auth_data = json.load(f)
        logger.info("✅ Auth file loaded")
    except:
        logger.error("❌ Cannot load substack_auth.json")
        return

    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)

    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    )

    if auth_data and 'cookies' in auth_data:
        context.add_cookies(auth_data['cookies'])
        logger.info("✅ Cookies loaded")

    page = context.new_page()

    try:
        # Step 1: Go to home
        logger.info("\n📍 Step 1: Going to Substack home...")
        page.goto("https://substack.com/home", wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)
        page.screenshot(path="diagnose_01_home.png")
        logger.info("   ✅ Screenshot: diagnose_01_home.png")

        # Step 2: Find all buttons
        logger.info("\n📍 Step 2: Finding all buttons on page...")
        buttons = page.query_selector_all('button')
        logger.info(f"   Found {len(buttons)} buttons:")
        for i, btn in enumerate(buttons[:15]):  # Show first 15
            try:
                text = btn.inner_text().strip()
                visible = btn.is_visible()
                if text:
                    logger.info(f"      {i+1}. '{text}' (visible: {visible})")
            except:
                pass

        # Step 3: Find all links
        logger.info("\n📍 Step 3: Finding all links on page...")
        links = page.query_selector_all('a')
        relevant_links = []
        for link in links:
            try:
                text = link.inner_text().strip()
                href = link.get_attribute('href')
                if text and ('post' in text.lower() or 'write' in text.lower() or 'publish' in href):
                    relevant_links.append(f"'{text}' -> {href}")
            except:
                pass

        logger.info(f"   Found {len(relevant_links)} relevant links:")
        for link in relevant_links[:10]:
            logger.info(f"      - {link}")

        # Step 4: Try to click "New post" button
        logger.info("\n📍 Step 4: Attempting to click 'New post' button...")

        selectors_to_try = [
            'button:has-text("Create")',  # New Substack UI
            'button:has-text("New post")',
            'a:has-text("New post")',
            'button:has-text("Write")',
            'a[href*="/publish/post/new"]',
            'a[href*="/publish"]'
        ]

        clicked = False
        for selector in selectors_to_try:
            try:
                logger.info(f"   Trying: {selector}")
                elem = page.wait_for_selector(selector, timeout=2000)
                if elem and elem.is_visible():
                    logger.info(f"      ✅ Found and clicking...")
                    elem.click()
                    clicked = True
                    time.sleep(3)
                    break
            except Exception as e:
                logger.info(f"      ❌ Not found or error: {str(e)[:50]}")

        if not clicked:
            logger.error("\n❌ Could not find 'Create' button")
            page.screenshot(path="diagnose_no_button.png")
            logger.info("   Screenshot: diagnose_no_button.png")
            return

        logger.info(f"   ✅ Clicked, waiting for page...")
        time.sleep(2)

        # Check for dropdown menu (Note, Post, Video)
        logger.info("   Checking for dropdown menu...")
        menu_selectors = [
            'text="Post"',  # Exact match
            'a:has-text("Post")',
            'button:has-text("Post")',
            '[role="menuitem"]:has-text("Post")',
            'a:has-text("New post")',  # Fallback
        ]

        menu_clicked = False
        for selector in menu_selectors:
            try:
                logger.info(f"      Trying menu item: {selector}")
                menu_item = page.wait_for_selector(selector, timeout=2000)
                if menu_item and menu_item.is_visible():
                    logger.info(f"      ✅ Found menu item, clicking...")
                    menu_item.click()
                    menu_clicked = True
                    time.sleep(3)
                    break
            except Exception as e:
                logger.info(f"      ❌ Not found: {str(e)[:30]}")

        if not menu_clicked:
            logger.info("      ℹ️  No menu found, proceeding...")

        page.screenshot(path="diagnose_02_editor.png")
        logger.info("   ✅ Editor page, screenshot: diagnose_02_editor.png")

        # Step 5: Find title input
        logger.info("\n📍 Step 5: Finding title input...")

        title_selectors = [
            'textarea[placeholder*="Post title" i]',
            'input[placeholder*="Post title" i]',
            'textarea[placeholder*="Title" i]',
            'textarea[name="title"]'
        ]

        title_found = False
        for selector in title_selectors:
            try:
                logger.info(f"   Trying: {selector}")
                elem = page.wait_for_selector(selector, timeout=2000)
                if elem and elem.is_visible():
                    logger.info(f"      ✅ Found title input")
                    elem.click()
                    time.sleep(1)
                    elem.fill("Test Post - Diagnostic")
                    logger.info(f"      ✅ Title filled")
                    title_found = True
                    break
            except Exception as e:
                logger.info(f"      ❌ Not found: {str(e)[:50]}")

        if not title_found:
            logger.error("\n❌ Could not find title input")

            # Debug: show all textareas and inputs
            logger.info("\n   Debug: All textareas on page:")
            textareas = page.query_selector_all('textarea')
            for i, ta in enumerate(textareas):
                try:
                    placeholder = ta.get_attribute('placeholder') or 'no placeholder'
                    visible = ta.is_visible()
                    logger.info(f"      {i+1}. placeholder='{placeholder}' visible={visible}")
                except:
                    pass

            page.screenshot(path="diagnose_no_title.png")
            logger.info("   Screenshot: diagnose_no_title.png")
            return

        page.screenshot(path="diagnose_03_title_filled.png")
        logger.info("   ✅ Screenshot: diagnose_03_title_filled.png")

        # Step 6: Find body editor
        logger.info("\n📍 Step 6: Finding body editor...")

        page.keyboard.press('Enter')
        time.sleep(1)

        body_selectors = [
            'div[contenteditable="true"]',
            'div[data-testid="post-body"]',
            'div.ProseMirror',
            'div[role="textbox"]'
        ]

        body_found = False
        for selector in body_selectors:
            try:
                logger.info(f"   Trying: {selector}")
                elems = page.query_selector_all(selector)
                logger.info(f"      Found {len(elems)} elements")
                for elem in elems:
                    if elem.is_visible():
                        logger.info(f"      ✅ Found visible body editor")
                        elem.click()
                        time.sleep(1)
                        page.keyboard.type("This is a test post for diagnostics.")
                        logger.info(f"      ✅ Body text typed")
                        body_found = True
                        break
                if body_found:
                    break
            except Exception as e:
                logger.info(f"      ❌ Error: {str(e)[:50]}")

        if not body_found:
            logger.warning("\n⚠️  Could not find body editor, trying direct keyboard input...")
            page.keyboard.type("This is a test post for diagnostics.")

        time.sleep(2)
        page.screenshot(path="diagnose_04_content_filled.png")
        logger.info("   ✅ Screenshot: diagnose_04_content_filled.png")

        # Step 7: Look for publish button
        logger.info("\n📍 Step 7: Looking for Publish button...")

        publish_selectors = [
            'button:has-text("Publish")',
            'button:has-text("Publish now")',
            'button[data-testid="publish-button"]',
            'button:has-text("Save")'
        ]

        publish_found = False
        for selector in publish_selectors:
            try:
                logger.info(f"   Trying: {selector}")
                elem = page.wait_for_selector(selector, timeout=2000)
                if elem and elem.is_visible():
                    logger.info(f"      ✅ Found: {selector}")
                    publish_found = True
                    break
            except Exception as e:
                logger.info(f"      ❌ Not found: {str(e)[:30]}")

        if publish_found:
            logger.info("   ℹ️  Publish button found (not clicking in diagnostic mode)")
        else:
            logger.warning("   ⚠️  No publish button found (article may auto-save)")

        page.screenshot(path="diagnose_05_final.png")
        logger.info("   ✅ Screenshot: diagnose_05_final.png")

        # Summary
        logger.info("\n" + "="*80)
        logger.info("📊 Diagnosis Summary")
        logger.info("="*80)
        logger.info(f"✅ Home page loaded: Yes")
        logger.info(f"✅ 'New post' clicked: {clicked}")
        logger.info(f"✅ Title input found: {title_found}")
        logger.info(f"✅ Body editor found: {body_found}")
        logger.info(f"✅ Publish button found: {publish_found}")
        logger.info("="*80)
        logger.info("\n📸 Check screenshots:")
        logger.info("   1. diagnose_01_home.png")
        logger.info("   2. diagnose_02_editor.png")
        logger.info("   3. diagnose_03_title_filled.png")
        logger.info("   4. diagnose_04_content_filled.png")
        logger.info("   5. diagnose_05_final.png")
        logger.info("="*80)

    except Exception as e:
        logger.error(f"\n❌ Fatal error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        page.screenshot(path="diagnose_error.png")

    finally:
        input("\nPress Enter to close browser...")
        browser.close()
        playwright.stop()


if __name__ == "__main__":
    diagnose()
