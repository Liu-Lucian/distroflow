#!/usr/bin/env python3
"""
Monitor Campaign Progress
"""
import json
import time
import sys

def monitor():
    print("🔍 Monitoring campaign progress...")
    print("Press Ctrl+C to stop monitoring\n")

    try:
        while True:
            try:
                with open('campaign_state.json', 'r') as f:
                    state = json.load(f)

                print(f"\r📊 Batches: {state['total_batches']}/7 | "
                      f"Leads: {state['total_leads']} | "
                      f"Emails Sent: {state['total_emails_sent']} | "
                      f"Failed: {state['total_emails_failed']}",
                      end='', flush=True)

                if state['total_batches'] >= 7:
                    print("\n\n✅ Campaign Complete!")
                    print(f"\n📊 Final Statistics:")
                    print(f"   Total Batches: {state['total_batches']}")
                    print(f"   Total Leads: {state['total_leads']}")
                    print(f"   Emails Sent: {state['total_emails_sent']}")
                    print(f"   Emails Failed: {state['total_emails_failed']}")
                    if state['total_emails_sent'] > 0:
                        success_rate = (state['total_emails_sent'] /
                                      (state['total_emails_sent'] + state['total_emails_failed']) * 100)
                        print(f"   Success Rate: {success_rate:.1f}%")
                    break

            except FileNotFoundError:
                print("\r⏳ Waiting for campaign to start...", end='', flush=True)
            except json.JSONDecodeError:
                pass

            time.sleep(5)

    except KeyboardInterrupt:
        print("\n\n⏸️  Monitoring stopped")

if __name__ == "__main__":
    monitor()
