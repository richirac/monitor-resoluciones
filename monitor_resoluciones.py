name: Monitor Resoluciones

on:
  schedule:
    - cron: "*/15 * * * *"   # cada 15 minutos
  workflow_dispatch:

permissions:
  contents: write

jobs:
  monitor:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout repo
      uses: actions/checkout@v3
      with:
        token: ${{ secrets.GITHUB_TOKEN }}

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.x'

    - name: Install dependencies
      run: pip install requests beautifulsoup4

    - name: Run monitor script
      run: python monitor_resoluciones.py

    - name: Show diff if changes
      run: |
        if [ -f last_text.txt ]; then
          git add last_text.txt last_hash.txt || true
          git diff --cached || echo "No hay cambios para mostrar"
          git reset
        else
          echo "⚠️ No existe last_text.txt (puede que el script no haya generado contenido)"
        fi

    - name: Commit changes if detected
      run: |
        git config user.name "github-actions"
        git config user.email "actions@github.com"
        [ -f last_text.txt ] && git add last_text.txt
        [ -f last_hash.txt ] && git add last_hash.txt
        git diff --cached --quiet || git commit -m "Update last_text and last_hash $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
        git pull --rebase origin main
        git push origin main
