#!/usr/bin/env python3
"""
Interactive Setup Wizard for MarketingMind AI Email Campaign System
Helps configure email_config.json with user-friendly prompts
"""

import json
import os
import sys

def print_header():
    print("\n" + "="*60)
    print("🧙 MarketingMind AI - Setup Wizard")
    print("="*60)
    print("\nThis wizard will help you configure the email campaign system.")
    print("Press Ctrl+C at any time to exit.\n")

def print_section(title):
    print("\n" + "-"*60)
    print(f"📋 {title}")
    print("-"*60)

def get_input(prompt, default=None, required=True):
    """Get user input with optional default value"""
    if default:
        prompt_text = f"{prompt} [{default}]: "
    else:
        prompt_text = f"{prompt}: "

    while True:
        value = input(prompt_text).strip()

        if value:
            return value
        elif default:
            return default
        elif not required:
            return ""
        else:
            print("❌ This field is required. Please enter a value.")

def confirm(prompt):
    """Ask for yes/no confirmation"""
    while True:
        response = input(f"{prompt} (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Please enter 'y' or 'n'")

def main():
    print_header()

    # Load existing config or use template
    config_file = 'email_config.json'

    if os.path.exists(config_file):
        print(f"✅ Found existing {config_file}")
        if not confirm("Do you want to reconfigure it?"):
            print("👋 Setup cancelled. Existing config preserved.")
            sys.exit(0)

        with open(config_file, 'r') as f:
            config = json.load(f)
    else:
        print(f"📝 Creating new {config_file}")
        # Load from example
        with open('email_config.example.json', 'r') as f:
            config = json.load(f)

    # Section 1: SMTP Configuration
    print_section("Step 1: Gmail SMTP Configuration")
    print("\n💡 You'll need a Gmail App Password for this.")
    print("   Visit: https://myaccount.google.com/apppasswords")
    print("   (Make sure 2-Step Verification is enabled first)\n")

    config['smtp']['username'] = get_input(
        "Gmail address",
        default=config['smtp'].get('username')
    )
    config['smtp']['from_email'] = config['smtp']['username']

    config['smtp']['password'] = get_input(
        "Gmail App Password (16 characters)",
        default=config['smtp'].get('password') if config['smtp'].get('password') != 'your-app-password-here' else None
    )

    config['smtp']['from_name'] = get_input(
        "Your name (sender name)",
        default=config['smtp'].get('from_name')
    )

    print(f"\n✅ SMTP configured with {config['smtp']['username']}")

    # Section 2: Campaign Configuration
    print_section("Step 2: Product/Campaign Configuration")

    config['campaign']['product_name'] = get_input(
        "Product name",
        default=config['campaign'].get('product_name')
    )

    config['campaign']['product_url'] = get_input(
        "Product URL (e.g., https://yoursite.com)",
        default=config['campaign'].get('product_url')
    )

    config['campaign']['company_name'] = get_input(
        "Company name",
        default=config['campaign'].get('company_name')
    )

    config['campaign']['support_email'] = get_input(
        "Support email",
        default=config['campaign'].get('support_email')
    )

    print(f"\n✅ Campaign configured for {config['campaign']['product_name']}")

    # Section 3: Promo Codes
    print_section("Step 3: Promo Code Configuration")
    print("\n💡 Initial promo code sent in first email")
    print("   Follow-up promo code sent after 24 hours if no conversion\n")

    if confirm("Do you want to customize promo codes?"):
        config['promo_codes']['initial']['code'] = get_input(
            "Initial promo code",
            default=config['promo_codes']['initial']['code']
        )
        config['promo_codes']['initial']['discount'] = get_input(
            "Initial discount (e.g., 20%)",
            default=config['promo_codes']['initial']['discount']
        )

        config['promo_codes']['followup']['code'] = get_input(
            "Follow-up promo code",
            default=config['promo_codes']['followup']['code']
        )
        config['promo_codes']['followup']['discount'] = get_input(
            "Follow-up discount (e.g., 30%)",
            default=config['promo_codes']['followup']['discount']
        )

        print(f"\n✅ Promo codes: {config['promo_codes']['initial']['code']} → {config['promo_codes']['followup']['code']}")
    else:
        print(f"✅ Using default: {config['promo_codes']['initial']['code']} (20%) → {config['promo_codes']['followup']['code']} (30%)")

    # Section 4: Test Mode
    print_section("Step 4: Test Mode Configuration")
    print("\n💡 Test mode sends ALL emails to a single test address")
    print("   This is HIGHLY RECOMMENDED before running real campaigns!\n")

    test_enabled = confirm("Enable test mode? (recommended)")
    config['test_mode']['enabled'] = test_enabled
    config['test_mode']['send_to_test_only'] = test_enabled

    if test_enabled:
        config['test_mode']['test_email'] = get_input(
            "Test email address",
            default=config['test_mode'].get('test_email', 'liu.lucian6@gmail.com')
        )
        print(f"\n✅ Test mode enabled - all emails will go to {config['test_mode']['test_email']}")
    else:
        print("\n⚠️  Test mode disabled - emails will be sent to real recipients!")

    # Save configuration
    print_section("Step 5: Saving Configuration")

    print("\n📋 Configuration Summary:")
    print(f"   SMTP: {config['smtp']['username']}")
    print(f"   Product: {config['campaign']['product_name']}")
    print(f"   Promo: {config['promo_codes']['initial']['code']} → {config['promo_codes']['followup']['code']}")
    print(f"   Test Mode: {'✅ Enabled' if config['test_mode']['enabled'] else '❌ Disabled'}")
    if config['test_mode']['enabled']:
        print(f"   Test Email: {config['test_mode']['test_email']}")

    print()
    if confirm("Save this configuration?"):
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"\n✅ Configuration saved to {config_file}")

        # Next steps
        print("\n" + "="*60)
        print("🎉 Setup Complete!")
        print("="*60)
        print("\n📋 Next Steps:")
        print("\n1. Test your configuration:")
        print("   python test_email_system.py")
        print("\n2. Run a test campaign (10 leads):")
        print("   python src/ultimate_email_finder_with_campaign.py saas_product_optimized.md 10 1")
        print("\n3. Check test email:")
        if config['test_mode']['enabled']:
            print(f"   Open {config['test_mode']['test_email']} to see the emails")
        print("\n4. View statistics:")
        print("   python src/email_campaign_manager.py --stats")
        print("\n📖 Full documentation: QUICK_START_CAMPAIGN.md")
        print()
    else:
        print("\n❌ Configuration not saved. Run setup_wizard.py again to retry.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error during setup: {e}")
        print("Please check your input and try again.")
        sys.exit(1)
