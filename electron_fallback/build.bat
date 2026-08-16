@echo off
echo Building Electron fallback wrapper...
npm install electron --save-dev
npm install electron-builder --save-dev
npx electron-builder -w
echo Build complete.
