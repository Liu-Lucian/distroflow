"""
Email Campaign Manager - 自动化邮件营销系统
功能：
1. 发送初始介绍邮件
2. 追踪优惠码使用
3. 自动跟进未转化的leads
4. 24小时后发送更大优惠
"""

import os
import json
import smtplib
import sqlite3
import logging
import time
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import threading
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class EmailCampaignManager:
    """Email campaign manager with automated follow-ups"""

    def __init__(self, config_file: str = "email_config.json"):
        """Initialize campaign manager"""
        self.config_file = config_file
        self.config = self._load_config()

        # Initialize tracking database
        self.db_file = self.config['tracking']['database_file']
        self._init_database()

        # SMTP connection (will be created when needed)
        self.smtp_server = None

    def _load_config(self) -> Dict:
        """Load email configuration"""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_file}\n"
                f"Please copy email_config.example.json to email_config.json and configure it."
            )

        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _init_database(self):
        """Initialize SQLite database for tracking"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        # Campaigns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                name TEXT,
                username TEXT,
                promo_code TEXT,
                status TEXT DEFAULT 'pending',
                sent_at TIMESTAMP,
                opened_at TIMESTAMP,
                converted_at TIMESTAMP,
                followup_count INTEGER DEFAULT 0,
                last_followup_at TIMESTAMP,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Email log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER,
                email_type TEXT,
                subject TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN,
                error_message TEXT,
                FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
            )
        ''')

        # Promo code tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS promo_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER,
                promo_code TEXT,
                used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
            )
        ''')

        conn.commit()
        conn.close()

        logger.info(f"✅ Database initialized: {self.db_file}")

    def _connect_smtp(self):
        """Connect to SMTP server"""
        if self.smtp_server is None:
            smtp_config = self.config['smtp']

            try:
                server = smtplib.SMTP(smtp_config['host'], smtp_config['port'])
                server.starttls()
                server.login(smtp_config['username'], smtp_config['password'])
                self.smtp_server = server
                logger.info(f"✅ Connected to SMTP server: {smtp_config['host']}")
            except Exception as e:
                logger.error(f"❌ Failed to connect to SMTP: {e}")
                raise

    def _disconnect_smtp(self):
        """Disconnect from SMTP server"""
        if self.smtp_server:
            try:
                self.smtp_server.quit()
                logger.info("✅ Disconnected from SMTP server")
            except:
                pass
            self.smtp_server = None

    def create_initial_email(self, lead: Dict, promo_code: str) -> MIMEMultipart:
        """Create initial introduction email"""
        campaign_config = self.config['campaign']
        promo_config = self.config['promo_codes']['initial']

        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"Your AI Interview Coach - 10 Minutes Before Your Interview"
        msg['From'] = f"{self.config['smtp']['from_name']} <{self.config['smtp']['from_email']}>"
        msg['To'] = lead['email']

        # Plain text version
        text_content = f"""
Hi {lead.get('name', 'there')},

I've noticed that many job seekers struggle with these interview challenges:
– Getting nervous and forgetting key points
– Interviewers asking questions too quickly to organize thoughts
– Resume not matching the job requirements well

We recently launched an AI-powered real-time interview assistant that can identify questions during your interview and generate optimal answer suggestions, while automatically optimizing your resume to improve your success rate.

📈 Over 2,000 job seekers are already using it, with an average interview success rate increase of 37%.

I'd love to invite you to try our Demo version (completely free, no download required):
👉 {campaign_config['product_url']}?promo={promo_code}&ref=@{lead['username']}

🎁 Exclusive code: {promo_code} ({promo_config['discount']} OFF)
If you'd like, we can also help you generate personalized interview Q&A templates matched to specific job positions to make your next interview even easier.

Cheers,
{self.config['smtp']['from_name']}
Founder @ {campaign_config['product_name']}
{campaign_config['support_email']}
(424) 439-1736

P.S. First 100 users get FREE Resume Optimization Service + AI Mock Interview!
"""

        # HTML version
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; line-height: 1.8; color: #2c3e50; background-color: #f4f7f9; margin: 0; padding: 0; }}
        .container {{ max-width: 600px; margin: 30px auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 28px; font-weight: 700; }}
        .header p {{ margin: 10px 0 0 0; font-size: 16px; opacity: 0.9; }}
        .content {{ padding: 40px 30px; }}
        .greeting {{ font-size: 18px; color: #2c3e50; margin-bottom: 20px; }}
        .problem-section {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 20px; margin: 25px 0; border-radius: 6px; }}
        .problem-section h3 {{ margin: 0 0 15px 0; color: #856404; font-size: 18px; }}
        .problem-list {{ margin: 10px 0; padding-left: 20px; }}
        .problem-list li {{ margin: 8px 0; color: #856404; font-size: 15px; }}
        .solution {{ background: #d1ecf1; border-left: 4px solid #17a2b8; padding: 20px; margin: 25px 0; border-radius: 6px; }}
        .solution h3 {{ margin: 0 0 10px 0; color: #0c5460; font-size: 18px; }}
        .social-proof {{ background: #d4edda; border-left: 4px solid #28a745; padding: 20px; margin: 25px 0; border-radius: 6px; text-align: center; }}
        .social-proof .stat {{ font-size: 36px; font-weight: bold; color: #155724; margin: 10px 0; }}
        .social-proof .stat-label {{ font-size: 14px; color: #155724; }}
        .promo-box {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 30px; margin: 30px 0; border-radius: 10px; text-align: center; box-shadow: 0 4px 15px rgba(245,87,108,0.3); }}
        .promo-code {{ font-size: 32px; font-weight: bold; letter-spacing: 4px; background: white; color: #f5576c; padding: 15px 25px; border-radius: 8px; display: inline-block; margin: 15px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.2); }}
        .discount-amount {{ font-size: 24px; margin: 10px 0; }}
        .cta-button {{ display: inline-block; background: #28a745; color: white; padding: 18px 45px; text-decoration: none; border-radius: 50px; margin: 25px 0; font-size: 18px; font-weight: bold; box-shadow: 0 4px 15px rgba(40,167,69,0.3); transition: all 0.3s; }}
        .cta-button:hover {{ background: #218838; transform: translateY(-2px); box-shadow: 0 6px 20px rgba(40,167,69,0.4); }}
        .features {{ margin: 30px 0; }}
        .feature {{ display: flex; align-items: start; margin: 20px 0; }}
        .feature-icon {{ font-size: 28px; margin-right: 15px; min-width: 40px; }}
        .feature-text h4 {{ margin: 0 0 5px 0; color: #2c3e50; font-size: 16px; }}
        .feature-text p {{ margin: 0; color: #7f8c8d; font-size: 14px; }}
        .urgency {{ background: #f8d7da; border: 2px dashed #f5c6cb; padding: 20px; margin: 25px 0; border-radius: 8px; text-align: center; color: #721c24; }}
        .urgency strong {{ font-size: 18px; }}
        .signature {{ margin-top: 40px; padding-top: 20px; border-top: 2px solid #e9ecef; }}
        .signature-name {{ font-weight: bold; font-size: 16px; color: #2c3e50; }}
        .signature-title {{ color: #7f8c8d; font-size: 14px; margin: 5px 0; }}
        .signature-contact {{ color: #7f8c8d; font-size: 13px; margin: 3px 0; }}
        .footer {{ background: #f8f9fa; padding: 25px 30px; text-align: center; color: #6c757d; font-size: 13px; }}
        .footer a {{ color: #667eea; text-decoration: none; }}
        .testimonial {{ background: #f8f9fa; border-left: 4px solid #667eea; padding: 20px; margin: 25px 0; border-radius: 6px; font-style: italic; color: #495057; }}
        .testimonial-author {{ font-style: normal; font-weight: bold; margin-top: 10px; color: #667eea; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 {campaign_config['product_name']}</h1>
            <p>AI-Powered Real-Time Interview Assistant</p>
        </div>

        <div class="content">
            <div class="greeting">
                Hi <strong>{lead.get('name', 'there')}</strong>,
            </div>

            <div class="problem-section">
                <h3>💭 Do you face these interview challenges?</h3>
                <ul class="problem-list">
                    <li>Getting nervous and forgetting key points</li>
                    <li>Questions come too fast to organize your thoughts</li>
                    <li>Resume doesn't match job requirements well</li>
                </ul>
            </div>

            <div class="solution">
                <h3>✨ {campaign_config['product_name']} Can Help You</h3>
                <p><strong>AI-powered real-time interview assistant</strong> that identifies questions during your interview and generates optimal answer suggestions, while automatically optimizing your resume to improve your success rate.</p>
            </div>

            <div class="social-proof">
                <div class="stat">2,000+</div>
                <div class="stat-label">Job Seekers Using It</div>
                <div class="stat" style="font-size: 42px; margin-top: 20px;">+37%</div>
                <div class="stat-label">Average Interview Success Rate Increase</div>
            </div>

            <div class="features">
                <div class="feature">
                    <div class="feature-icon">🎯</div>
                    <div class="feature-text">
                        <h4>Real-Time Question Recognition</h4>
                        <p>AI instantly identifies interviewer questions and generates optimal answer prompts</p>
                    </div>
                </div>
                <div class="feature">
                    <div class="feature-icon">📝</div>
                    <div class="feature-text">
                        <h4>Automatic Resume Optimization</h4>
                        <p>Automatically optimizes your resume based on job requirements</p>
                    </div>
                </div>
                <div class="feature">
                    <div class="feature-icon">💡</div>
                    <div class="feature-text">
                        <h4>Personalized Q&A Templates</h4>
                        <p>Custom interview Q&A library matched to specific positions</p>
                    </div>
                </div>
                <div class="feature">
                    <div class="feature-icon">⚡</div>
                    <div class="feature-text">
                        <h4>Completely Free Trial</h4>
                        <p>Demo version is free, no download required</p>
                    </div>
                </div>
            </div>

            <div class="promo-box">
                <h3 style="margin: 0 0 15px 0;">🎁 Exclusive Promo Code</h3>
                <div class="promo-code">{promo_code}</div>
                <div class="discount-amount">{promo_config['discount']} OFF All Premium Features</div>
                <p style="margin: 15px 0 0 0; font-size: 14px; opacity: 0.9;">⏰ Valid for {promo_config['valid_days']} days</p>
            </div>

            <center>
                <a href="{campaign_config['product_url']}?promo={promo_code}&email={lead['email']}&ref=@{lead['username']}" class="cta-button">
                    🚀 Try Free Demo Now →
                </a>
            </center>

            <div class="urgency">
                <strong>🔥 Limited Time Offer: First 100 Users Only</strong><br>
                ✓ FREE Resume Optimization Service (Worth $99)<br>
                ✓ AI Mock Interview (Worth $79)<br>
                ✓ 1-on-1 Career Advisor Session (Worth $199)
            </div>

            <div class="testimonial">
                "After using HireMe AI, my interview success rate jumped from 30% to 85%! The real-time prompts are amazing and gave me so much more confidence."
                <div class="testimonial-author">— Sarah Chen, Software Engineer @ Google</div>
            </div>

            <p style="margin-top: 30px; font-size: 15px; color: #2c3e50;">
                <strong>Want personalized Q&A templates?</strong><br>
                Just reply to this email, and I'll personally create a custom interview Q&A library matched to your target positions!
            </p>

            <div class="signature">
                <div class="signature-name">{self.config['smtp']['from_name']}</div>
                <div class="signature-title">Founder @ {campaign_config['product_name']}</div>
                <div class="signature-contact">{campaign_config['support_email']}</div>
                <div class="signature-contact">📞 (424) 439-1736</div>
            </div>
        </div>

        <div class="footer">
            <p><strong>P.S.</strong> This exclusive code is just for you. I noticed you follow @{lead.get('scraped_from', 'tech leaders')} on Twitter, so I know you're serious about your career development. Best of luck with your interviews! 🎉</p>
            <p style="margin-top: 20px;">
                <a href="{campaign_config['product_url']}/unsubscribe?email={lead['email']}">Unsubscribe</a>
            </p>
        </div>
    </div>
</body>
</html>
"""

        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))

        return msg

    def create_followup_email(self, lead: Dict, promo_code: str, followup_count: int) -> MIMEMultipart:
        """Create follow-up email with better offer"""
        campaign_config = self.config['campaign']
        promo_config = self.config['promo_codes']['followup']

        subject_lines = [
            f"[Last Chance] {promo_config['discount']} OFF + 3 Free Services Ending Soon",
            f"{lead.get('name', 'there')}, Your {promo_config['discount']} Discount Expires Soon",
            f"Final Reminder: {campaign_config['product_name']} VIP Offer Expires in 48 Hours"
        ]

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject_lines[min(followup_count - 1, len(subject_lines) - 1)]
        msg['From'] = f"{self.config['smtp']['from_name']} <{self.config['smtp']['from_email']}>"
        msg['To'] = lead['email']

        initial_promo_config = self.config['promo_codes']['initial']

        text_content = f"""
Hi {lead.get('name', 'there')},

I sent you an email about {campaign_config['product_name']} and noticed you haven't tried the Demo yet.

I don't want you to miss this opportunity, so I've decided to UPGRADE your discount:

🎁 UPGRADED OFFER (One-Time Only):
Original Code: {initial_promo_config['code']} ({initial_promo_config['discount']} OFF)
New Code: {promo_code} ({promo_config['discount']} OFF) ← UPGRADED!

Plus, the limited-time bonuses for first 100 users are still available:
✓ FREE Resume Optimization Service (Worth $99)
✓ AI Mock Interview (Worth $79)
✓ 1-on-1 Career Advisor Session (Worth $199)

⏰ This offer expires permanently in {promo_config['valid_days']} days!

Try it now: {campaign_config['product_url']}?promo={promo_code}&ref=followup

Have questions? Just reply to this email and I'll answer personally!

Looking forward to helping you,
{self.config['smtp']['from_name']}
Founder @ {campaign_config['product_name']}
{campaign_config['support_email']}
(424) 439-1736

P.S. Over 2,000 job seekers have already improved their interview success rate with our system. Don't let this opportunity slip away!
"""

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; line-height: 1.8; color: #2c3e50; background-color: #f4f7f9; margin: 0; padding: 0; }}
        .container {{ max-width: 600px; margin: 30px auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 40px 30px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 32px; font-weight: 700; }}
        .header p {{ margin: 10px 0 0 0; font-size: 18px; opacity: 0.9; }}
        .content {{ padding: 40px 30px; }}
        .greeting {{ font-size: 18px; color: #2c3e50; margin-bottom: 20px; }}
        .urgency-banner {{ background: #ff6b6b; color: white; padding: 20px; text-align: center; font-size: 20px; font-weight: bold; margin: 0 0 30px 0; }}
        .upgrade-box {{ background: linear-gradient(135deg, #fff3cd 0%, #ffe4a3 100%); border: 3px solid #ff6b6b; padding: 30px; margin: 25px 0; border-radius: 10px; text-align: center; }}
        .comparison {{ display: flex; justify-content: space-around; margin: 20px 0; }}
        .comparison-item {{ flex: 1; padding: 15px; }}
        .old-offer {{ opacity: 0.6; }}
        .old-offer .promo-code {{ text-decoration: line-through; background: #e9ecef; color: #6c757d; font-size: 20px; padding: 10px 15px; }}
        .new-offer .promo-code {{ background: white; color: #f5576c; font-size: 32px; font-weight: bold; letter-spacing: 4px; padding: 15px 25px; border-radius: 8px; box-shadow: 0 4px 15px rgba(245,87,108,0.3); }}
        .arrow {{ font-size: 36px; color: #f5576c; align-self: center; }}
        .benefits-grid {{ display: grid; grid-template-columns: 1fr; gap: 15px; margin: 25px 0; }}
        .benefit-item {{ background: #d4edda; border-left: 4px solid #28a745; padding: 15px; border-radius: 6px; }}
        .benefit-item strong {{ color: #155724; }}
        .benefit-value {{ float: right; color: #28a745; font-weight: bold; }}
        .cta-button {{ display: inline-block; background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%); color: white; padding: 20px 50px; text-decoration: none; border-radius: 50px; margin: 25px 0; font-size: 20px; font-weight: bold; box-shadow: 0 6px 20px rgba(245,87,108,0.4); transition: all 0.3s; }}
        .cta-button:hover {{ transform: translateY(-3px); box-shadow: 0 8px 25px rgba(245,87,108,0.5); }}
        .countdown {{ background: #fff3cd; border: 2px dashed #ffc107; padding: 25px; margin: 25px 0; border-radius: 10px; text-align: center; }}
        .countdown-timer {{ font-size: 48px; font-weight: bold; color: #dc3545; margin: 15px 0; }}
        .social-proof-mini {{ background: #f8f9fa; padding: 20px; margin: 25px 0; border-radius: 8px; text-align: center; }}
        .social-proof-mini .number {{ font-size: 28px; font-weight: bold; color: #667eea; }}
        .signature {{ margin-top: 40px; padding-top: 20px; border-top: 2px solid #e9ecef; }}
        .signature-name {{ font-weight: bold; font-size: 16px; color: #2c3e50; }}
        .signature-title {{ color: #7f8c8d; font-size: 14px; margin: 5px 0; }}
        .signature-contact {{ color: #7f8c8d; font-size: 13px; margin: 3px 0; }}
        .footer {{ background: #f8f9fa; padding: 25px 30px; text-align: center; color: #6c757d; font-size: 13px; }}
        .footer a {{ color: #667eea; text-decoration: none; }}
        .highlight-box {{ background: #e7f3ff; border-left: 4px solid #007bff; padding: 20px; margin: 25px 0; border-radius: 6px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="urgency-banner">
            ⏰ Last Chance: Expires Permanently in {promo_config['valid_days']} Days
        </div>

        <div class="header">
            <h1>⚡ DISCOUNT UPGRADED ⚡</h1>
            <p>Special VIP Offer Just For You</p>
        </div>

        <div class="content">
            <div class="greeting">
                Hi <strong>{lead.get('name', 'there')}</strong>,
            </div>

            <p>I sent you an email about <strong>{campaign_config['product_name']}</strong> and noticed you haven't tried the Demo yet.</p>

            <p>As the founder, I really want to help every job seeker succeed. So I've decided to:</p>

            <div class="upgrade-box">
                <h2 style="margin: 0 0 20px 0; color: #dc3545;">🎁 UPGRADE Your Discount (One-Time Only)</h2>

                <div class="comparison">
                    <div class="comparison-item old-offer">
                        <div style="font-size: 14px; color: #6c757d; margin-bottom: 10px;">Original Offer</div>
                        <div class="promo-code">{initial_promo_config['code']}</div>
                        <div style="margin-top: 10px; color: #6c757d;">{initial_promo_config['discount']} OFF</div>
                    </div>

                    <div class="arrow">→</div>

                    <div class="comparison-item new-offer">
                        <div style="font-size: 14px; color: #f5576c; margin-bottom: 10px; font-weight: bold;">UPGRADED ✨</div>
                        <div class="promo-code">{promo_code}</div>
                        <div style="margin-top: 10px; color: #f5576c; font-size: 20px; font-weight: bold;">{promo_config['discount']} OFF</div>
                    </div>
                </div>
            </div>

            <div class="highlight-box">
                <strong>✨ Plus, First 100 Users Bonuses Still Available:</strong>
            </div>

            <div class="benefits-grid">
                <div class="benefit-item">
                    <strong>✓ FREE Resume Optimization Service</strong>
                    <span class="benefit-value">Worth $99</span>
                </div>
                <div class="benefit-item">
                    <strong>✓ AI Mock Interview</strong>
                    <span class="benefit-value">Worth $79</span>
                </div>
                <div class="benefit-item">
                    <strong>✓ 1-on-1 Career Advisor Session</strong>
                    <span class="benefit-value">Worth $199</span>
                </div>
            </div>

            <div class="countdown">
                <div style="font-size: 18px; color: #721c24; margin-bottom: 10px;">⏰ Offer Countdown</div>
                <div class="countdown-timer">{promo_config['valid_days']} Days</div>
                <div style="color: #721c24; font-size: 16px;">Then it expires permanently!</div>
            </div>

            <center>
                <a href="{campaign_config['product_url']}?promo={promo_code}&email={lead['email']}&ref=followup" class="cta-button">
                    🚀 Claim {promo_config['discount']} Discount Now →
                </a>
            </center>

            <div class="social-proof-mini">
                <div class="number">2,000+</div>
                <div style="color: #6c757d;">Job seekers have improved their interview success rate</div>
                <div style="margin-top: 15px; font-size: 24px; color: #28a745; font-weight: bold;">+37%</div>
                <div style="color: #6c757d;">Average interview success rate increase</div>
            </div>

            <p style="margin-top: 30px; font-size: 15px; color: #2c3e50;">
                <strong>Have questions?</strong><br>
                Just reply to this email and I'll personally answer and help you create a custom interview strategy!
            </p>

            <div class="signature">
                <div>Looking forward to helping you,</div>
                <div class="signature-name" style="margin-top: 10px;">{self.config['smtp']['from_name']}</div>
                <div class="signature-title">Founder @ {campaign_config['product_name']}</div>
                <div class="signature-contact">{campaign_config['support_email']}</div>
                <div class="signature-contact">📞 (424) 439-1736</div>
            </div>
        </div>

        <div class="footer">
            <p><strong>P.S.</strong> I know job hunting is tough – that's exactly why I created {campaign_config['product_name']}. This exclusive code is just for you. Don't let this opportunity slip away! 💪</p>
            <p style="margin-top: 20px;">
                <a href="{campaign_config['product_url']}/unsubscribe?email={lead['email']}">Unsubscribe</a>
            </p>
        </div>
    </div>
</body>
</html>
"""

        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))

        return msg

    def send_email(self, msg: MIMEMultipart, to_email: str) -> bool:
        """Send email via SMTP"""
        try:
            if self.smtp_server is None:
                self._connect_smtp()

            self.smtp_server.send_message(msg)
            logger.info(f"✅ Email sent to {to_email}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to send email to {to_email}: {e}")
            return False

    def start_campaign(self, leads: List[Dict], delay_minutes: int = 0):
        """Start email campaign for leads"""
        test_mode = self.config['test_mode']['enabled']
        test_email = self.config['test_mode']['test_email']
        send_to_test_only = self.config['test_mode'].get('send_to_test_only', False)

        logger.info(f"\n🚀 Starting Email Campaign")
        logger.info(f"   Total leads: {len(leads)}")
        logger.info(f"   Test mode: {'ON' if test_mode else 'OFF'}")
        if test_mode:
            logger.info(f"   Test email: {test_email}")
            logger.info(f"   Send to test only: {send_to_test_only}")

        # Connect to SMTP
        self._connect_smtp()

        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        initial_promo = self.config['promo_codes']['initial']['code']

        sent_count = 0
        failed_count = 0

        for i, lead in enumerate(leads, 1):
            email = lead.get('all_contacts', {}).get('emails', [])
            if not email:
                continue

            email = email[0]  # First email
            name = lead.get('name', '')
            username = lead.get('username', '')

            # Prepare lead data
            lead_data = {
                'email': email,
                'name': name,
                'username': username,
                'scraped_from': lead.get('scraped_from', '')
            }

            logger.info(f"\n📧 [{i}/{len(leads)}] Sending to {name} ({email})...")

            # In test mode, send to test email
            if test_mode and send_to_test_only:
                logger.info(f"   🧪 Test mode: Redirecting to {test_email}")
                original_email = email
                email = test_email
                lead_data['email'] = test_email
                lead_data['name'] = f"{name} (TEST for {original_email})"

            # Create and send email
            msg = self.create_initial_email(lead_data, initial_promo)
            success = self.send_email(msg, email)

            # Record in database
            cursor.execute('''
                INSERT INTO campaigns (email, name, username, promo_code, status, sent_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (email, name, username, initial_promo, 'sent' if success else 'failed', datetime.now()))

            campaign_id = cursor.lastrowid

            cursor.execute('''
                INSERT INTO email_log (campaign_id, email_type, subject, success, error_message)
                VALUES (?, ?, ?, ?, ?)
            ''', (campaign_id, 'initial', msg['Subject'], success, None if success else 'SMTP error'))

            conn.commit()

            if success:
                sent_count += 1
            else:
                failed_count += 1

            # Human-like random delay between emails to avoid spam filters
            if i < len(leads):
                min_delay = self.config['timing'].get('send_delay_min_seconds', 30)
                max_delay = self.config['timing'].get('send_delay_max_seconds', 90)
                delay = random.uniform(min_delay, max_delay)
                logger.info(f"   ⏳ Waiting {delay:.0f} seconds before next email (human-like behavior)...")
                time.sleep(delay)

        conn.close()
        self._disconnect_smtp()

        logger.info(f"\n✅ Campaign Complete!")
        logger.info(f"   Sent: {sent_count}")
        logger.info(f"   Failed: {failed_count}")

        # Schedule follow-ups
        if sent_count > 0:
            followup_hours = self.config['timing']['followup_delay_hours']
            logger.info(f"\n⏰ Follow-ups scheduled in {followup_hours} hours")
            logger.info(f"   Run: python src/email_campaign_manager.py --check-followups")

    def check_and_send_followups(self):
        """Check for leads that need follow-up emails"""
        logger.info("\n🔍 Checking for follow-ups...")

        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        followup_delay_hours = self.config['timing']['followup_delay_hours']
        max_followups = self.config['timing']['max_followups']

        # Find leads that:
        # 1. Were sent initial email > followup_delay_hours ago
        # 2. Haven't converted
        # 3. Haven't reached max follow-ups
        cutoff_time = datetime.now() - timedelta(hours=followup_delay_hours)

        cursor.execute('''
            SELECT id, email, name, username, promo_code, followup_count, sent_at
            FROM campaigns
            WHERE status = 'sent'
            AND converted_at IS NULL
            AND followup_count < ?
            AND sent_at < ?
            AND (last_followup_at IS NULL OR last_followup_at < ?)
        ''', (max_followups, cutoff_time, cutoff_time))

        leads_to_followup = cursor.fetchall()

        logger.info(f"   Found {len(leads_to_followup)} leads needing follow-up")

        if not leads_to_followup:
            conn.close()
            return

        # Connect to SMTP
        self._connect_smtp()

        followup_promo = self.config['promo_codes']['followup']['code']

        for campaign_id, email, name, username, old_promo, followup_count, sent_at in leads_to_followup:
            logger.info(f"\n📧 Follow-up #{followup_count + 1} to {name} ({email})...")

            lead_data = {
                'email': email,
                'name': name,
                'username': username
            }

            # Create and send follow-up email
            msg = self.create_followup_email(lead_data, followup_promo, followup_count + 1)
            success = self.send_email(msg, email)

            if success:
                # Update campaign
                cursor.execute('''
                    UPDATE campaigns
                    SET followup_count = followup_count + 1,
                        last_followup_at = ?,
                        promo_code = ?
                    WHERE id = ?
                ''', (datetime.now(), followup_promo, campaign_id))

                # Log email
                cursor.execute('''
                    INSERT INTO email_log (campaign_id, email_type, subject, success)
                    VALUES (?, ?, ?, ?)
                ''', (campaign_id, f'followup_{followup_count + 1}', msg['Subject'], True))

                conn.commit()

            # Human-like random delay between follow-up emails
            if campaign_id != leads_to_followup[-1][0]:  # Not last email
                min_delay = self.config['timing'].get('followup_send_delay_min_seconds', 45)
                max_delay = self.config['timing'].get('followup_send_delay_max_seconds', 120)
                delay = random.uniform(min_delay, max_delay)
                logger.info(f"   ⏳ Waiting {delay:.0f} seconds before next follow-up (human-like behavior)...")
                time.sleep(delay)

        conn.close()
        self._disconnect_smtp()

        logger.info(f"\n✅ Follow-ups complete!")

    def mark_conversion(self, promo_code: str, email: Optional[str] = None):
        """Mark a lead as converted (used promo code)"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        if email:
            cursor.execute('''
                UPDATE campaigns
                SET status = 'converted', converted_at = ?
                WHERE email = ? AND promo_code = ?
            ''', (datetime.now(), email, promo_code))
        else:
            cursor.execute('''
                UPDATE campaigns
                SET status = 'converted', converted_at = ?
                WHERE promo_code = ?
            ''', (datetime.now(), promo_code))

        affected = cursor.rowcount
        conn.commit()
        conn.close()

        logger.info(f"✅ Marked {affected} conversion(s) for promo code: {promo_code}")

    def get_campaign_stats(self) -> Dict:
        """Get campaign statistics"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()

        # Total campaigns
        cursor.execute('SELECT COUNT(*) FROM campaigns')
        total = cursor.fetchone()[0]

        # Sent
        cursor.execute("SELECT COUNT(*) FROM campaigns WHERE status = 'sent'")
        sent = cursor.fetchone()[0]

        # Converted
        cursor.execute("SELECT COUNT(*) FROM campaigns WHERE status = 'converted'")
        converted = cursor.fetchone()[0]

        # Pending follow-up
        followup_delay_hours = self.config['timing']['followup_delay_hours']
        cutoff_time = datetime.now() - timedelta(hours=followup_delay_hours)

        cursor.execute('''
            SELECT COUNT(*) FROM campaigns
            WHERE status = 'sent'
            AND converted_at IS NULL
            AND sent_at < ?
        ''', (cutoff_time,))
        pending_followup = cursor.fetchone()[0]

        conn.close()

        conversion_rate = (converted / sent * 100) if sent > 0 else 0

        return {
            'total': total,
            'sent': sent,
            'converted': converted,
            'pending_followup': pending_followup,
            'conversion_rate': conversion_rate
        }


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--check-followups':
        # Check and send follow-ups
        manager = EmailCampaignManager()
        manager.check_and_send_followups()
    elif len(sys.argv) > 1 and sys.argv[1] == '--stats':
        # Show statistics
        manager = EmailCampaignManager()
        stats = manager.get_campaign_stats()
        print("\n📊 Campaign Statistics:")
        print(f"   Total campaigns: {stats['total']}")
        print(f"   Sent: {stats['sent']}")
        print(f"   Converted: {stats['converted']}")
        print(f"   Pending follow-up: {stats['pending_followup']}")
        print(f"   Conversion rate: {stats['conversion_rate']:.1f}%")
    else:
        print("Email Campaign Manager")
        print("\nUsage:")
        print("  python email_campaign_manager.py --check-followups  # Check and send follow-ups")
        print("  python email_campaign_manager.py --stats            # Show campaign statistics")
        print("\nTo start a campaign, use the integrated system:")
        print("  python src/ultimate_email_finder_with_campaign.py")
