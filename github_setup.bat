@echo off
echo Setting up your project for GitHub...

REM Initialize Git repository
git init

REM Add all files to Git
git add .

REM Create initial commit
git commit -m "Initial commit with complete project setup"

REM Pull remote changes
git pull --allow-unrelated-histories origin main

REM Push changes to remote repository
git push -u origin main

echo.
echo Your repository is now ready to be pushed to GitHub.
echo.
echo To push to GitHub:
echo 1. Create a new repository on GitHub
echo 2. Run the following commands (replace with your repository URL):
echo.
echo    git remote add origin https://github.com/Secrets-Star/billiard-simulation.git
echo    git branch -M main
echo    git push -u origin main
echo.
echo Press any key to exit...
pause 