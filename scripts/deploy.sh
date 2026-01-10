#!/bin/bash
# Lotto Auto Purchase - Deployment Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🚀 Starting Deployment Process..."
echo "========================================"
date "+%Y-%m-%d %H:%M:%S"
echo ""

# 1. Update Environment (Dependencies & Playwright)
echo "📦 Step 1: Updating environment..."
"$SCRIPT_DIR/setup-env.sh"
echo ""

# 2. Update Systemd Timer
# Only run if on Linux (systemctl check)
if command -v systemctl &> /dev/null; then
    echo "⏰ Step 2: Updating systemd timer..."
    "$SCRIPT_DIR/install-systemd.sh"
else
    echo "⚠️  Step 2: Systemd not found. Skipping timer update."
    echo "   (This is expected if running on macOS or inside a non-systemd container)"
fi

echo ""
echo "✅ Deployment completed successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
