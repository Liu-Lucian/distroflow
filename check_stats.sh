#!/bin/bash
# 快速查看营销活动统计

DB="/Users/l.u.c/my-app/interview_assistant/campaign_tracking.db"

echo "======================================================================="
echo "📊 EMAIL CAMPAIGN STATISTICS"
echo "======================================================================="
echo ""

echo "📧 Total Emails Sent:"
sqlite3 "$DB" "SELECT COUNT(*) FROM campaigns"
echo ""

echo "📊 Status Breakdown:"
sqlite3 "$DB" "SELECT status, COUNT(*) FROM campaigns GROUP BY status"
echo ""

echo "📈 Last 10 Emails Sent:"
sqlite3 "$DB" "SELECT email, name, sent_at FROM campaigns ORDER BY sent_at DESC LIMIT 10"
echo ""

echo "✅ Opened Emails:"
sqlite3 "$DB" "SELECT COUNT(*) FROM campaigns WHERE opened_at IS NOT NULL"
echo ""

echo "💰 Conversions:"
sqlite3 "$DB" "SELECT COUNT(*) FROM campaigns WHERE status = 'converted'"
echo ""

echo "🔄 Pending Follow-ups (>24h, not converted):"
sqlite3 "$DB" "SELECT COUNT(*) FROM campaigns WHERE status = 'sent' AND converted_at IS NULL AND datetime(sent_at) < datetime('now', '-24 hours')"
echo ""

echo "======================================================================="
