Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Starting n8n + Gemini AI Interactive Simulator" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "Open your browser at: http://127.0.0.1:5050" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop." -ForegroundColor Yellow
Write-Host ""
python simulator\server.py
