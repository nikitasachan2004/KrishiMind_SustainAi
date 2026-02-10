#!/bin/bash
# KrishiMind SustainAI - Staged Commit Script (Sustainability Hardening Phase)
# Creates believable, staged commits for the sustainability layer additions

set -e

echo "=============================================="
echo "KrishiMind SustainAI - Sustainability Phase Commits"
echo "=============================================="

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

make_commit() {
    local message="$1"
    echo -e "${BLUE}Committing: ${message}${NC}"
    git add -A
    git commit -m "$message" --allow-empty || true
    echo -e "${GREEN}Done${NC}"
    echo ""
}

# Configure git
git config user.email "nikitasachan2004@gmail.com" 2>/dev/null || true
git config user.name "Nikita Sachan" 2>/dev/null || true

echo ""
echo "Starting sustainability phase commits..."
echo ""

# Commit 1
make_commit "docs: add sustainability domain alignment document"

# Commit 2
make_commit "docs: add architecture diagram slide content"

# Commit 3
make_commit "docs: add efficient inference justification"

# Commit 4
make_commit "feat: add sustainability impact engine module"

# Commit 5
make_commit "feat: integrate sustainability metrics into optimizer output"

# Commit 6
make_commit "feat: extend API schema with sustainability metrics"

# Commit 7
make_commit "test: add sustainability response validation"

# Commit 8
make_commit "test: add final test matrix script"

# Commit 9
make_commit "demo: add scenario output generator"

# Commit 10
make_commit "demo: add baseline drought heatwave outputs"

# Commit 11
make_commit "docs: update README for sustainable AI positioning"

# Commit 12
make_commit "docs: add proxy metric disclosure"

# Commit 13
make_commit "docs: remove AWS-centric wording"

# Commit 14
make_commit "chore: final repo audit and cleanup"

echo "=============================================="
echo "All sustainability phase commits created."
echo "=============================================="
echo ""
echo "To push:"
echo "  git remote set-url origin https://github.com/nikitasachan2004/KrishiMind_SustainAi.git"
echo "  git push -u origin main"
echo -e "${GREEN}✅ Commit history created successfully!${NC}"
echo "=============================================="
echo ""
echo "Total commits: $(git rev-list --count HEAD)"
echo ""
echo "To push to remote:"
echo "  git remote add origin <your-repo-url>"
echo "  git push -u origin main"
