# PowerShell script to push project to GitHub
# Run this script: .\push_to_github.ps1

Write-Host "🚀 Preparing to push Orbital CDN Simulation to GitHub..." -ForegroundColor Cyan

# Check if git is initialized
if (-not (Test-Path .git)) {
    Write-Host "❌ Git not initialized. Run: git init" -ForegroundColor Red
    exit 1
}

# Show current status
Write-Host "`n📊 Current Git Status:" -ForegroundColor Yellow
git status

# Add all files
Write-Host "`n➕ Adding all files..." -ForegroundColor Green
git add .

# Show what will be committed
Write-Host "`n📝 Files to be committed:" -ForegroundColor Yellow
git status --short

# Commit changes
Write-Host "`n💾 Committing changes..." -ForegroundColor Green
$commitMessage = "Update: Enhanced features, fixed analytics charts, improved UI, and cleaned up unnecessary files"
git commit -m $commitMessage

# Check if remote exists
$remoteExists = git remote | Select-String -Pattern "origin"
if (-not $remoteExists) {
    Write-Host "`n⚠️  No remote 'origin' found." -ForegroundColor Yellow
    Write-Host "Please add your GitHub remote first:" -ForegroundColor Yellow
    Write-Host "git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git" -ForegroundColor Cyan
    exit 1
}

# Show remote URL
Write-Host "`n🌐 Remote repository:" -ForegroundColor Yellow
git remote -v

# Push to GitHub
Write-Host "`n📤 Pushing to GitHub..." -ForegroundColor Green
Write-Host "You may be prompted for GitHub credentials." -ForegroundColor Yellow
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Successfully pushed to GitHub!" -ForegroundColor Green
    Write-Host "🎉 Your project is now on GitHub!" -ForegroundColor Cyan
} else {
    Write-Host "`n❌ Push failed. Please check your credentials and try again." -ForegroundColor Red
}
