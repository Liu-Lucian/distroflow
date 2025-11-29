#!/usr/bin/env python3
"""
Twitter自动发布脚本 - 带智能调试功能
遇到障碍自动分析并重试，直到成功
"""
import sys
sys.path.insert(0, 'src')
from twitter_poster import TwitterPoster
import json
import logging
import time
import traceback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_error(error_msg: str, screenshot_path: str = None) -> dict:
    """分析错误并提供解决方案"""
    error_msg_lower = error_msg.lower()

    # 错误类型分析
    if 'graduated-access' in error_msg_lower or 'unlock more' in error_msg_lower:
        return {
            'type': 'RATE_LIMIT',
            'description': 'Twitter账号被限流，需要人工验证',
            'solution': 'MANUAL_ACTION',
            'retry': False,
            'message': '需要用户点击"Got it"按钮或验证手机号'
        }

    elif 'timeout' in error_msg_lower or 'timed out' in error_msg_lower:
        return {
            'type': 'TIMEOUT',
            'description': '页面加载或操作超时',
            'solution': 'INCREASE_TIMEOUT',
            'retry': True,
            'wait_time': 10,
            'message': '增加超时时间并重试'
        }

    elif 'not found' in error_msg_lower or 'no element' in error_msg_lower:
        return {
            'type': 'ELEMENT_NOT_FOUND',
            'description': '找不到页面元素',
            'solution': 'RETRY_WITH_DELAY',
            'retry': True,
            'wait_time': 5,
            'message': '等待页面加载完成后重试'
        }

    elif 'login' in error_msg_lower or 'authentication' in error_msg_lower:
        return {
            'type': 'AUTH_FAILED',
            'description': '登录验证失败',
            'solution': 'MANUAL_ACTION',
            'retry': False,
            'message': '需要重新登录或更新cookies'
        }

    else:
        return {
            'type': 'UNKNOWN',
            'description': '未知错误',
            'solution': 'RETRY',
            'retry': True,
            'wait_time': 3,
            'message': '通用重试策略'
        }

def post_with_auto_debug(max_attempts: int = 5):
    """带自动调试的Twitter发布"""

    # 加载内容 - 使用每条都带URL的版本
    logger.info('📖 加载Twitter内容...')
    try:
        with open('tweets_all_with_url.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        twitter_content = data['twitter']
        logger.info(f'   ✅ 已加载 {len(twitter_content["tweets"])} 条tweets (每条都包含URL)')

        # 验证每条都有URL
        url_count = sum(1 for tweet in twitter_content['tweets'] if 'https://interviewasssistant.com' in tweet)
        logger.info(f'   ✅ {url_count}/{len(twitter_content["tweets"])} 条tweets包含URL')
    except FileNotFoundError:
        logger.error('   ❌ 找不到tweets_all_with_url.json')
        sys.exit(1)

    # 显示内容预览
    logger.info('\n📝 准备发布的内容:')
    for i, tweet in enumerate(twitter_content['tweets'][:3], 1):
        preview = tweet[:80] + '...' if len(tweet) > 80 else tweet
        logger.info(f'   {i}. {preview}')
    if len(twitter_content['tweets']) > 3:
        logger.info(f'   ... 还有 {len(twitter_content["tweets"]) - 3} 条')

    attempt = 0
    last_error = None

    while attempt < max_attempts:
        attempt += 1
        logger.info(f'\n{"="*80}')
        logger.info(f'🔄 尝试 #{attempt}/{max_attempts}')
        logger.info(f'{"="*80}')

        poster = TwitterPoster()

        try:
            # 设置浏览器
            logger.info('🌐 启动浏览器...')
            poster.setup_browser(headless=False)
            logger.info('   ✅ 浏览器已启动')

            # 验证登录
            logger.info('🔐 验证登录状态...')
            if not poster.verify_login():
                raise Exception('登录验证失败')
            logger.info('   ✅ 登录验证成功')

            # 发布内容
            logger.info('📤 开始发布Twitter thread...')
            success = poster.create_post(twitter_content)

            if success:
                logger.info(f'\n{"="*80}')
                logger.info('✅ Twitter thread发布成功！')
                logger.info(f'   📊 共发布 {len(twitter_content["tweets"])} 条tweets')
                logger.info('   ✅ 品牌: HireMeAI (无中文)')
                logger.info('   ✅ URL: https://interviewasssistant.com')
                logger.info(f'{"="*80}\n')

                # 等待确认
                logger.info('⏸️  浏览器将保持打开60秒以供检查...')
                time.sleep(60)
                poster.close_browser()
                return True
            else:
                raise Exception('发布失败，但没有具体错误信息')

        except Exception as e:
            last_error = str(e)
            error_trace = traceback.format_exc()

            logger.error(f'\n❌ 发布失败: {last_error}')

            # 分析错误
            logger.info('\n🔍 分析错误...')
            analysis = analyze_error(last_error)

            logger.info(f'   错误类型: {analysis["type"]}')
            logger.info(f'   描述: {analysis["description"]}')
            logger.info(f'   解决方案: {analysis["solution"]}')
            logger.info(f'   建议: {analysis["message"]}')

            # 保持浏览器打开供检查
            if poster.page:
                logger.info('\n📸 保存错误截图...')
                try:
                    poster.take_screenshot('auto_debug_error')
                    logger.info('   ✅ 截图已保存')
                except:
                    pass

                logger.info('⏸️  浏览器将保持打开30秒以供检查错误...')
                time.sleep(30)

            try:
                poster.close_browser()
            except:
                pass

            # 决定是否重试
            if not analysis['retry']:
                logger.error(f'\n❌ 无法自动修复，需要人工干预: {analysis["message"]}')
                logger.error('\n完整错误信息:')
                logger.error(error_trace)
                return False

            if attempt < max_attempts:
                wait_time = analysis.get('wait_time', 5)
                logger.info(f'\n⏳ 等待 {wait_time} 秒后重试...')
                time.sleep(wait_time)
            else:
                logger.error(f'\n❌ 已达到最大尝试次数 ({max_attempts})')
                logger.error(f'最后错误: {last_error}')
                logger.error('\n完整错误信息:')
                logger.error(error_trace)
                return False

    return False

if __name__ == "__main__":
    logger.info('🚀 启动Twitter自动发布系统')
    logger.info('   带智能错误分析和自动调试功能')
    logger.info('   将持续尝试直到成功或遇到无法自动解决的问题\n')

    success = post_with_auto_debug(max_attempts=5)

    if success:
        logger.info('\n✅ 任务完成！Twitter thread已成功发布')
        sys.exit(0)
    else:
        logger.error('\n❌ 任务失败，无法自动解决问题')
        logger.error('请检查错误日志和截图，可能需要人工干预')
        sys.exit(1)
