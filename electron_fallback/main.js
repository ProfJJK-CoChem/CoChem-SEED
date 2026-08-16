const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let pythonServer;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  // Wait for React to start in dev mode or load production build
  mainWindow.loadURL('http://localhost:3000');
}

app.whenReady().then(() => {
  // Spawn FastAPI server
  pythonServer = spawn('uvicorn', ['backend.app.main:app', '--port', '8000'], {
    cwd: path.join(__dirname, '..')
  });

  pythonServer.stdout.on('data', (data) => {
    console.log(`FastAPI: ${data}`);
  });

  pythonServer.stderr.on('data', (data) => {
    console.error(`FastAPI Error: ${data}`);
  });

  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('will-quit', () => {
  if (pythonServer) {
    pythonServer.kill();
  }
});
