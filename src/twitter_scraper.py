"""
Twitter Web Scraper - Bypass API rate limits by scraping the website directly
直接爬取Twitter网页，避免API限制
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
import logging
from typing import List, Dict, Optional
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TwitterWebScraper:
    """爬取Twitter网页获取粉丝信息"""

    def __init__(self, headless: bool = True, auto_login: bool = True):
        """
        初始化浏览器

        Args:
            headless: 是否无头模式（不显示浏览器窗口）
            auto_login: 是否自动登录（从.env读取账号密码）
        """
        self.headless = headless
        self.auto_login = auto_login
        self.driver = None
        self.logged_in = False

    def _setup_driver(self):
        """设置Chrome驱动"""
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service

        options = Options()

        if self.headless:
            options.add_argument('--headless')

        # 反爬虫设置
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        # 禁用自动化特征
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        self.driver = webdriver.Chrome(options=options)

        # 隐藏webdriver特征
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        logger.info("✓ Chrome driver initialized")

    def _human_delay(self, min_sec: float = 2.0, max_sec: float = 5.0):
        """模拟人类操作延迟"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)

    def _scroll_slowly(self, scrolls: int = 3):
        """缓慢滚动页面，模拟人类浏览"""
        for i in range(scrolls):
            # 随机滚动距离
            scroll_amount = random.randint(300, 800)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")

            # 随机停顿时间
            self._human_delay(1.0, 3.0)

            # 偶尔向上滚动一点（人类行为）
            if random.random() < 0.2:
                self.driver.execute_script(f"window.scrollBy(0, -{random.randint(100, 300)});")
                self._human_delay(0.5, 1.5)

    def login(self, username: str, password: str) -> bool:
        """
        登录Twitter

        Args:
            username: Twitter用户名或邮箱
            password: 密码

        Returns:
            是否登录成功
        """
        if not self.driver:
            self._setup_driver()

        try:
            logger.info("Logging into Twitter...")
            self.driver.get("https://twitter.com/i/flow/login")

            self._human_delay(4, 6)

            # 输入用户名
            try:
                username_input = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="username"]'))
                )

                # 清空并输入用户名
                username_input.clear()
                self._human_delay(0.5, 1)

                # 模拟人类打字
                for char in username:
                    username_input.send_keys(char)
                    time.sleep(random.uniform(0.1, 0.25))

                self._human_delay(1, 2)
                username_input.send_keys(Keys.RETURN)

            except Exception as e:
                logger.error(f"Error entering username: {e}")
                return False

            self._human_delay(3, 5)

            # 输入密码
            try:
                password_input = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="password"]'))
                )

                password_input.clear()
                self._human_delay(0.5, 1)

                for char in password:
                    password_input.send_keys(char)
                    time.sleep(random.uniform(0.1, 0.25))

                self._human_delay(1, 2)
                password_input.send_keys(Keys.RETURN)

            except Exception as e:
                logger.error(f"Error entering password: {e}")
                return False

            # 等待登录完成
            self._human_delay(5, 8)

            # 验证是否登录成功 - 检查多个可能的成功标志
            current_url = self.driver.current_url.lower()
            if "home" in current_url or "compose" in current_url or len(self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="SideNav_AccountSwitcher_Button"]')) > 0:
                self.logged_in = True
                logger.info("✓ Successfully logged in to Twitter")
                return True
            else:
                logger.warning(f"Login may have failed. Current URL: {current_url}")
                # 即使URL不对，也尝试继续（有时Twitter会重定向）
                self.logged_in = True
                return True

        except Exception as e:
            logger.error(f"Login error: {e}")
            import traceback
            traceback.print_exc()
            return False

    def get_followers(
        self,
        username: str,
        max_followers: int = 100,
        extract_emails: bool = True
    ) -> List[Dict]:
        """
        获取指定用户的粉丝列表

        Args:
            username: Twitter用户名（不带@）
            max_followers: 最多获取多少粉丝
            extract_emails: 是否提取邮箱

        Returns:
            粉丝信息列表
        """
        if not self.driver:
            self._setup_driver()

        # 自动登录（如果需要且未登录）
        if self.auto_login and not self.logged_in:
            self._auto_login_from_env()

        followers = []

        try:
            # 访问粉丝页面
            url = f"https://twitter.com/{username}/followers"
            logger.info(f"Scraping followers from: {url}")
            self.driver.get(url)

            self._human_delay(3, 5)

            # 等待页面加载
            self._human_delay(5, 8)

            # 滚动加载粉丝
            scrolls = 0
            max_scrolls = max(max_followers // 5, 20)  # 至少滚动20次
            last_height = 0
            no_new_data_count = 0

            while len(followers) < max_followers and scrolls < max_scrolls:
                # 尝试多种选择器来找粉丝元素
                follower_elements = self._find_follower_elements()

                logger.info(f"Found {len(follower_elements)} follower elements on page (scroll {scrolls})")

                for element in follower_elements:
                    if len(followers) >= max_followers:
                        break

                    try:
                        follower_data = self._extract_follower_data(element, extract_emails)

                        # 检查是否已经添加过（避免重复）
                        if follower_data and not any(f['username'] == follower_data['username'] for f in followers):
                            followers.append(follower_data)
                            logger.info(f"✓ Scraped: @{follower_data['username']} - {follower_data.get('email', 'No email')}")

                    except Exception as e:
                        logger.debug(f"Error extracting follower: {e}")
                        continue

                # 如果没有新数据，可能需要更多滚动
                if len(follower_elements) == 0:
                    no_new_data_count += 1
                    if no_new_data_count >= 5:
                        logger.warning("No new followers found after 5 scrolls, stopping")
                        break
                else:
                    no_new_data_count = 0

                # 滚动加载更多
                self._scroll_slowly(3)
                scrolls += 1

                # 检查是否还能加载更多
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height and scrolls > 5:
                    logger.info("Reached end of followers list")
                    break
                last_height = new_height

                logger.info(f"Progress: {len(followers)}/{max_followers} followers scraped")

            logger.info(f"✓ Total scraped: {len(followers)} followers")
            return followers

        except Exception as e:
            logger.error(f"Error scraping followers: {e}")
            return followers

    def _find_follower_elements(self) -> list:
        """尝试多种选择器来找到粉丝元素"""
        selectors = [
            '[data-testid="UserCell"]',
            '[data-testid="cellInnerDiv"]',
            'div[data-testid*="User"]',
            'article[role="article"]',
            'div[class*="css-"][class*="r-"]',  # Twitter的动态类名
        ]

        for selector in selectors:
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                logger.debug(f"Found elements with selector: {selector}")
                return elements

        # 如果都找不到，尝试XPath
        try:
            elements = self.driver.find_elements(By.XPATH, '//div[contains(@aria-label, "Follow")]/..')
            if elements:
                logger.debug("Found elements with XPath")
                return elements
        except:
            pass

        return []

    def _extract_follower_data(self, element, extract_emails: bool = True) -> Optional[Dict]:
        """
        从页面元素提取粉丝数据

        Args:
            element: Selenium WebElement
            extract_emails: 是否提取邮箱

        Returns:
            粉丝数据字典
        """
        try:
            # 提取用户名 - 尝试多种方法
            username = None
            try:
                # 方法1: 通过链接
                links = element.find_elements(By.TAG_NAME, 'a')
                for link in links:
                    href = link.get_attribute('href')
                    if href and 'twitter.com/' in href and '/status/' not in href:
                        parts = href.rstrip('/').split('/')
                        if len(parts) > 0:
                            username = parts[-1]
                            break
            except:
                pass

            # 方法2: 通过@符号的文本
            if not username:
                try:
                    text_elements = element.find_elements(By.TAG_NAME, 'span')
                    for elem in text_elements:
                        text = elem.text
                        if text.startswith('@'):
                            username = text[1:]  # 去掉@
                            break
                except:
                    pass

            if not username:
                return None

            # 提取显示名称
            name = username
            try:
                # 尝试找到名字（通常在@用户名之前）
                spans = element.find_elements(By.TAG_NAME, 'span')
                for span in spans:
                    text = span.text.strip()
                    if text and not text.startswith('@') and len(text) > 1 and len(text) < 50:
                        name = text
                        break
            except:
                pass

            # 提取简介
            bio = ""
            try:
                # 尝试多种方法找bio
                bio_selectors = [
                    '[data-testid="UserDescription"]',
                    'div[dir="auto"]',
                ]
                for selector in bio_selectors:
                    try:
                        bio_elem = element.find_element(By.CSS_SELECTOR, selector)
                        bio_text = bio_elem.text.strip()
                        if bio_text and not bio_text.startswith('@'):
                            bio = bio_text
                            break
                    except:
                        continue
            except:
                pass

            follower_data = {
                'username': username,
                'name': name,
                'bio': bio,
                'profile_url': f"https://twitter.com/{username}",
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }

            # 提取邮箱（如果有）
            if extract_emails and bio:
                email = self._extract_email_from_text(bio)
                if email:
                    follower_data['email'] = email

            return follower_data

        except Exception as e:
            logger.debug(f"Error extracting follower data: {e}")
            return None

    def _extract_email_from_text(self, text: str) -> Optional[str]:
        """从文本中提取邮箱"""
        # 邮箱正则表达式
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

        emails = re.findall(email_pattern, text)
        return emails[0] if emails else None

    def get_profile_details(self, username: str) -> Optional[Dict]:
        """
        获取用户详细资料（包括邮箱、网站等）

        Args:
            username: Twitter用户名

        Returns:
            用户详细信息
        """
        if not self.driver:
            self._setup_driver()

        try:
            url = f"https://twitter.com/{username}"
            self.driver.get(url)

            self._human_delay(2, 4)

            profile_data = {
                'username': username,
                'profile_url': url
            }

            # 提取简介
            try:
                bio = self.driver.find_element(By.CSS_SELECTOR, '[data-testid="UserDescription"]').text
                profile_data['bio'] = bio

                # 从简介提取邮箱
                email = self._extract_email_from_text(bio)
                if email:
                    profile_data['email'] = email
            except:
                pass

            # 提取网站链接
            try:
                website_element = self.driver.find_element(By.CSS_SELECTOR, 'a[href*="t.co"]')
                website = website_element.text
                profile_data['website'] = website
            except:
                pass

            # 提取粉丝数
            try:
                followers_element = self.driver.find_element(By.XPATH, '//a[contains(@href, "/followers")]//span')
                followers_text = followers_element.text
                # 解析 "1.2K" 或 "1,234" 格式
                followers_count = self._parse_count(followers_text)
                profile_data['followers_count'] = followers_count
            except:
                pass

            return profile_data

        except Exception as e:
            logger.error(f"Error getting profile details: {e}")
            return None

    def _parse_count(self, count_str: str) -> int:
        """解析粉丝数（处理 K、M 等单位）"""
        count_str = count_str.strip().replace(',', '')

        if 'K' in count_str.upper():
            return int(float(count_str.replace('K', '').replace('k', '')) * 1000)
        elif 'M' in count_str.upper():
            return int(float(count_str.replace('M', '').replace('m', '')) * 1000000)
        else:
            try:
                return int(count_str)
            except:
                return 0

    def _auto_login_from_env(self) -> bool:
        """从环境变量自动登录"""
        import os
        from dotenv import load_dotenv

        load_dotenv()

        username = os.getenv('TWITTER_USERNAME')
        password = os.getenv('TWITTER_PASSWORD')

        if not username or not password:
            logger.warning("No Twitter credentials in .env file, skipping auto-login")
            return False

        logger.info(f"Auto-logging in as {username}...")
        return self.login(username, password)

    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")


# 示例使用
if __name__ == "__main__":
    # 创建爬虫实例（显示浏览器，方便调试）
    scraper = TwitterWebScraper(headless=False)

    try:
        # 可选：登录（如果需要访问受保护的账号）
        # scraper.login("your_username", "your_password")

        # 爬取粉丝
        followers = scraper.get_followers(
            username="elonmusk",  # 示例：爬取马斯克的粉丝
            max_followers=20,
            extract_emails=True
        )

        # 打印结果
        print(f"\n✓ Scraped {len(followers)} followers\n")

        for i, follower in enumerate(followers, 1):
            print(f"{i}. @{follower['username']}")
            print(f"   Name: {follower['name']}")
            if follower.get('email'):
                print(f"   Email: {follower['email']}")
            print(f"   Bio: {follower['bio'][:100]}...")
            print()

        # 导出到CSV
        import pandas as pd
        df = pd.DataFrame(followers)
        df.to_csv('twitter_followers.csv', index=False, encoding='utf-8-sig')
        print("✓ Data exported to twitter_followers.csv")

    finally:
        scraper.close()
