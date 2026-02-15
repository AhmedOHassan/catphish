#!/bin/bash
# AASIST Model Setup Script (Optional)

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     🤖 AASIST Model Setup (Optional)                    ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

echo "This script will set up the AASIST anti-spoofing model."
echo "AASIST provides ~95% accuracy for AI voice detection."
echo "Without it, the system uses a fallback heuristic (~60-70% accuracy)."
echo ""
read -p "Do you want to proceed? (y/N) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Skipped. System will use fallback heuristic."
    exit 0
fi

# Create directories
mkdir -p models/aasist/models/weights

echo "Step 1/3: Cloning AASIST repository..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ ! -d "models/aasist/.git" ]; then
    git clone https://github.com/clovaai/aasist.git models/aasist
    echo "✅ Repository cloned"
else
    echo "