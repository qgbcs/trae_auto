// 使用JavaScript执行Trae签到自动化
const { execSync } = require('child_process');

console.log("=== Trae CN 签到脚本 v17 (JS版本) ===\n");

// 1. 查找Trae主窗口
console.log("步骤1: 查找Trae主窗口...");
try {
    const result = execSync(
        'powershell -Command "Get-Process -Name \'Trae CN\' | Where-Object { $_.MainWindowTitle -ne \'\' } | Select-Object Id, MainWindowTitle | ConvertTo-Json"',
        { encoding: 'utf-8' }
    );
    console.log("窗口信息:", result);
} catch (e) {
    console.log("查找窗口失败:", e.message);
}

// 2. 获取当前积分
console.log("\n步骤2: 获取当前积分...");
try {
    const fs = require('fs');
    const storagePath = 'C:\\Users\\Administrator\\AppData\\Roaming\\Trae CN\\User\\globalStorage\\storage.json';
    const data = JSON.parse(fs.readFileSync(storagePath, 'utf-8'));

    if (data['iCubeServerData://icube.cloudide']) {
        const serverData = JSON.parse(data['iCubeServerData://icube.cloudide']);
        console.log("当前总积分:", serverData.totalCredits);
        console.log("服务器时间:", new Date(serverData.serverTimeInfo.serverTime).toISOString());
    }
} catch (e) {
    console.log("读取积分失败:", e.message);
}

// 3. 使用pyautogui执行签到
console.log("\n步骤3: 准备执行UI自动化签到...");
console.log("需要安装pyautogui和pywin32库");
console.log("运行: C:\\QGB\\miniforge3\\python.exe C:\\test\\github\\trae_auto\\checkin_v17.py");
