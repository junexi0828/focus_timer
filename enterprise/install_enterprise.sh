#!/bin/bash

# Focus Timer Enterprise - 시스템 서비스 설치 스크립트
# 상업용 출시 버전

set -e

PRODUCT_NAME="Focus Timer Enterprise"
VERSION="2.0.0"
COMPANY="FocusTimer Inc."

echo "🚀 $PRODUCT_NAME v$VERSION 설치를 시작합니다..."
echo "© $COMPANY - 상업용 집중 모드 시스템"

# 현재 디렉토리 확인
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENTERPRISE_PATH="$SCRIPT_DIR/focus_timer_enterprise.py"

# 필수 파일 확인
if [ ! -f "$ENTERPRISE_PATH" ]; then
    echo "❌ focus_timer_enterprise.py 파일을 찾을 수 없습니다."
    echo "💡 이 스크립트를 focus_timer_enterprise.py와 같은 디렉토리에 위치시켜주세요."
    exit 1
fi

# 관리자 권한 확인
if [ "$EUID" -ne 0 ]; then
    echo "❌ 관리자 권한이 필요합니다."
    echo "💡 sudo ./install_enterprise.sh로 실행해주세요."
    exit 1
fi

# 시스템 요구사항 확인
echo "🔍 시스템 요구사항 확인 중..."

# Python 3 확인
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3가 설치되어 있지 않습니다."
    exit 1
fi

# 가상환경 생성 및 필수 Python 패키지 설치
echo "📦 Python 가상환경 생성 및 패키지 설치 중..."

# 가상환경 디렉토리
VENV_DIR="/Applications/FocusTimer/venv"

# 가상환경 생성
python3 -m venv "$VENV_DIR"

# 가상환경 활성화 및 패키지 설치
source "$VENV_DIR/bin/activate"
pip install watchdog psutil flask

echo "✅ Python 패키지 설치 완료"

# 애플리케이션 디렉토리 생성
APP_DIR="/Applications/FocusTimer"
echo "📁 애플리케이션 디렉토리 생성: $APP_DIR"
mkdir -p "$APP_DIR"

# 실행 파일 복사
echo "📋 실행 파일 복사 중..."
cp "$ENTERPRISE_PATH" "$APP_DIR/focus_timer_enterprise.py"
chmod +x "$APP_DIR/focus_timer_enterprise.py"

# 설정 디렉토리 생성
CONFIG_DIR="/Library/Application Support/FocusTimer"
echo "⚙️ 설정 디렉토리 생성: $CONFIG_DIR"
mkdir -p "$CONFIG_DIR"

# 로그 디렉토리 생성
LOG_DIR="/var/log/FocusTimer"
echo "📝 로그 디렉토리 생성: $LOG_DIR"
mkdir -p "$LOG_DIR"
chmod 755 "$LOG_DIR"

# LaunchDaemon plist 파일 생성
PLIST_FILE="/Library/LaunchDaemons/com.focustimer.enterprise.plist"

echo "🔧 시스템 서비스 설정 파일 생성 중..."

cat > "$PLIST_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.focustimer.enterprise</string>
    <key>ProgramArguments</key>
    <array>
        <string>$VENV_DIR/bin/python</string>
        <string>$APP_DIR/focus_timer_enterprise.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$LOG_DIR/focus_timer.log</string>
    <key>StandardErrorPath</key>
    <string>$LOG_DIR/focus_timer_error.log</string>
    <key>WorkingDirectory</key>
    <string>$APP_DIR</string>
    <key>UserName</key>
    <string>root</string>
    <key>GroupName</key>
    <string>wheel</string>
    <key>ProcessType</key>
    <string>Background</string>
    <key>ThrottleInterval</key>
    <integer>60</integer>
    <key>ExitTimeOut</key>
    <integer>30</integer>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>$VENV_DIR/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
</dict>
</plist>
EOF

# 권한 설정
chmod 644 "$PLIST_FILE"
chown root:wheel "$PLIST_FILE"

# LaunchDaemon 등록
echo "🚀 시스템 서비스 등록 중..."
launchctl load "$PLIST_FILE"

# 브라우저 확장 프로그램 설치 (선택적)
echo "🌐 브라우저 확장 프로그램 설치 옵션"
read -p "Chrome 확장 프로그램을 설치하시겠습니까? (y/n): " install_extension

if [ "$install_extension" = "y" ]; then
    echo "📦 Chrome 확장 프로그램 설치 중..."
    EXTENSION_DIR="$APP_DIR/extensions"
    mkdir -p "$EXTENSION_DIR"

    # 확장 프로그램 매니페스트 생성
    cat > "$EXTENSION_DIR/manifest.json" << EOF
{
  "manifest_version": 3,
  "name": "Focus Timer Enterprise",
  "version": "2.0.0",
  "description": "Enterprise-grade focus mode extension",
  "permissions": [
    "webRequest",
    "webRequestBlocking",
    "storage",
    "tabs"
  ],
  "host_permissions": [
    "*://*.youtube.com/*",
    "*://*.facebook.com/*",
    "*://*.instagram.com/*",
    "*://*.twitter.com/*",
    "*://*.tiktok.com/*",
    "*://*.reddit.com/*"
  ],
  "background": {
    "service_worker": "background.js"
  },
  "content_scripts": [
    {
      "matches": [
        "*://*.youtube.com/*",
        "*://*.facebook.com/*",
        "*://*.instagram.com/*",
        "*://*.twitter.com/*",
        "*://*.tiktok.com/*",
        "*://*.reddit.com/*"
      ],
      "js": ["content.js"],
      "run_at": "document_start"
    }
  ],
  "action": {
    "default_popup": "popup.html",
    "default_title": "Focus Timer Enterprise"
  }
}
EOF

    # 백그라운드 스크립트 생성
    cat > "$EXTENSION_DIR/background.js" << EOF
chrome.webRequest.onBeforeRequest.addListener(
  function(details) {
    return {cancel: true};
  },
  {
    urls: [
      "*://*.youtube.com/*",
      "*://*.facebook.com/*",
      "*://*.instagram.com/*",
      "*://*.twitter.com/*",
      "*://*.tiktok.com/*",
      "*://*.reddit.com/*"
    ]
  },
  ["blocking"]
);
EOF

    # 콘텐츠 스크립트 생성
    cat > "$EXTENSION_DIR/content.js" << EOF
// 집중 모드 활성화 시 페이지 차단
document.body.innerHTML = \`
<div style="
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 999999;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  color: white;
  text-align: center;
">
  <div style="font-size: 4rem; margin-bottom: 2rem;">🔒</div>
  <h1 style="font-size: 2.5rem; margin-bottom: 1rem;">집중 모드 활성화</h1>
  <p style="font-size: 1.2rem; margin-bottom: 2rem;">
    현재 집중 모드가 활성화되어 있습니다.<br>
    이 사이트에 접근할 수 없습니다.
  </p>
  <div style="
    background: rgba(255, 255, 255, 0.1);
    padding: 1rem 2rem;
    border-radius: 10px;
    backdrop-filter: blur(10px);
  ">
    <p style="margin: 0; font-size: 1rem;">
      집중 모드를 해제하려면 Focus Timer Enterprise를 종료하세요.
    </p>
  </div>
</div>
\`;
EOF

    # 팝업 HTML 생성
    cat > "$EXTENSION_DIR/popup.html" << EOF
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {
      width: 300px;
      padding: 20px;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      margin: 0;
    }
    .header {
      text-align: center;
      margin-bottom: 20px;
    }
    .status {
      background: rgba(255, 255, 255, 0.1);
      padding: 15px;
      border-radius: 10px;
      margin-bottom: 15px;
      backdrop-filter: blur(10px);
    }
    .button {
      width: 100%;
      padding: 10px;
      background: rgba(255, 255, 255, 0.2);
      border: none;
      border-radius: 5px;
      color: white;
      cursor: pointer;
      margin-bottom: 10px;
    }
    .button:hover {
      background: rgba(255, 255, 255, 0.3);
    }
  </style>
</head>
<body>
  <div class="header">
    <h2>🔒 Focus Timer Enterprise</h2>
    <p>Enterprise-grade Focus Mode</p>
  </div>

  <div class="status">
    <h3>상태</h3>
    <p id="status">확인 중...</p>
  </div>

  <button class="button" id="checkStatus">상태 확인</button>
  <button class="button" id="openSettings">설정 열기</button>

  <script src="popup.js"></script>
</body>
</html>
EOF

    # 팝업 스크립트 생성
    cat > "$EXTENSION_DIR/popup.js" << EOF
document.addEventListener('DOMContentLoaded', function() {
  // 상태 확인
  chrome.storage.local.get(['focusMode'], function(result) {
    const status = result.focusMode ? '활성화' : '비활성화';
    document.getElementById('status').textContent = \`집중 모드: \${status}\`;
  });

  // 상태 확인 버튼
  document.getElementById('checkStatus').addEventListener('click', function() {
    chrome.storage.local.get(['focusMode'], function(result) {
      const status = result.focusMode ? '활성화' : '비활성화';
      document.getElementById('status').textContent = \`집중 모드: \${status}\`;
    });
  });

  // 설정 열기 버튼
  document.getElementById('openSettings').addEventListener('click', function() {
    chrome.tabs.create({url: 'chrome://extensions/'});
  });
});
EOF

    echo "✅ Chrome 확장 프로그램 설치 완료"
    echo "💡 Chrome에서 chrome://extensions/로 이동하여 '압축해제된 확장 프로그램 로드'로 설치하세요."
fi

# 웹 관리 인터페이스 설치 (선택적)
echo "🌐 웹 관리 인터페이스 설치 옵션"
read -p "웹 관리 인터페이스를 설치하시겠습니까? (y/n): " install_web_ui

if [ "$install_web_ui" = "y" ]; then
    echo "🌐 웹 관리 인터페이스 설치 중..."
    WEB_DIR="$APP_DIR/web"
    mkdir -p "$WEB_DIR"

    # Flask 앱 생성
    cat > "$WEB_DIR/app.py" << EOF
from flask import Flask, render_template, jsonify, request
import json
import os
import subprocess
from datetime import datetime

app = Flask(__name__)

STATE_PATH = "/Library/Application Support/FocusTimer/state.json"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    try:
        if os.path.exists(STATE_PATH):
            with open(STATE_PATH, 'r') as f:
                state = json.load(f)
            return jsonify(state)
        else:
            return jsonify({"error": "상태 파일을 찾을 수 없습니다."})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/start', methods=['POST'])
def start_focus_mode():
    try:
        data = request.json
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        # Focus Timer 시작 명령
        subprocess.run([
            'sudo', 'launchctl', 'start', 'com.focustimer.enterprise'
        ], check=True)

        return jsonify({"success": True, "message": "집중 모드가 시작되었습니다."})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/api/stop', methods=['POST'])
def stop_focus_mode():
    try:
        # Focus Timer 중지 명령
        subprocess.run([
            'sudo', 'launchctl', 'stop', 'com.focustimer.enterprise'
        ], check=True)

        return jsonify({"success": True, "message": "집중 모드가 중지되었습니다."})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
EOF

    # HTML 템플릿 생성
    mkdir -p "$WEB_DIR/templates"
    cat > "$WEB_DIR/templates/index.html" << EOF
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Focus Timer Enterprise - 관리자 패널</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .status-card {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .controls {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 20px;
        }
        .control-group {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
        }
        input, select {
            width: 100%;
            padding: 10px;
            margin: 5px 0;
            border: none;
            border-radius: 5px;
            background: rgba(255, 255, 255, 0.2);
            color: white;
        }
        button {
            width: 100%;
            padding: 15px;
            border: none;
            border-radius: 5px;
            background: rgba(255, 255, 255, 0.2);
            color: white;
            cursor: pointer;
            font-size: 16px;
            margin: 5px 0;
        }
        button:hover {
            background: rgba(255, 255, 255, 0.3);
        }
        .start-btn {
            background: #4CAF50;
        }
        .stop-btn {
            background: #f44336;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 Focus Timer Enterprise</h1>
            <p>Enterprise-grade Focus Mode Management</p>
        </div>

        <div class="status-card">
            <h3>시스템 상태</h3>
            <div id="status">로딩 중...</div>
        </div>

        <div class="controls">
            <div class="control-group">
                <h3>집중 모드 시작</h3>
                <input type="time" id="startTime" value="09:00">
                <input type="time" id="endTime" value="18:00">
                <button class="start-btn" onclick="startFocusMode()">집중 모드 시작</button>
            </div>

            <div class="control-group">
                <h3>집중 모드 제어</h3>
                <button class="stop-btn" onclick="stopFocusMode()">집중 모드 중지</button>
                <button onclick="refreshStatus()">상태 새로고침</button>
            </div>
        </div>
    </div>

    <script>
        function refreshStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    const statusDiv = document.getElementById('status');
                    if (data.error) {
                        statusDiv.innerHTML = \`<p style="color: #ff6b6b;">\${data.error}</p>\`;
                    } else {
                        statusDiv.innerHTML = \`
                            <p><strong>집중 모드:</strong> \${data.is_focus_mode ? '활성화' : '비활성화'}</p>
                            <p><strong>차단 상태:</strong> \${data.is_blocked ? '차단됨' : '해제됨'}</p>
                            <p><strong>차단 횟수:</strong> \${data.block_count || 0}</p>
                            <p><strong>우회 시도:</strong> \${data.bypass_attempts || 0}</p>
                        \`;
                    }
                })
                .catch(error => {
                    document.getElementById('status').innerHTML = \`<p style="color: #ff6b6b;">오류: \${error}</p>\`;
                });
        }

        function startFocusMode() {
            const startTime = document.getElementById('startTime').value;
            const endTime = document.getElementById('endTime').value;

            fetch('/api/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    start_time: startTime,
                    end_time: endTime
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    refreshStatus();
                } else {
                    alert('오류: ' + data.error);
                }
            })
            .catch(error => {
                alert('오류: ' + error);
            });
        }

        function stopFocusMode() {
            fetch('/api/stop', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    refreshStatus();
                } else {
                    alert('오류: ' + data.error);
                }
            })
            .catch(error => {
                alert('오류: ' + error);
            });
        }

        // 페이지 로드 시 상태 확인
        refreshStatus();

        // 30초마다 상태 새로고침
        setInterval(refreshStatus, 30000);
    </script>
</body>
</html>
EOF

    # 웹 서비스 plist 생성
    WEB_PLIST="/Library/LaunchDaemons/com.focustimer.web.plist"
    cat > "$WEB_PLIST" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.focustimer.web</string>
    <key>ProgramArguments</key>
    <array>
        <string>$VENV_DIR/bin/python</string>
        <string>$WEB_DIR/app.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>WorkingDirectory</key>
    <string>$WEB_DIR</string>
    <key>UserName</key>
    <string>root</string>
    <key>GroupName</key>
    <string>wheel</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>$VENV_DIR/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    </dict>
</dict>
</plist>
EOF

    chmod 644 "$WEB_PLIST"
    chown root:wheel "$WEB_PLIST"
    launchctl load "$WEB_PLIST"

    echo "✅ 웹 관리 인터페이스 설치 완료"
    echo "🌐 관리자 패널: http://localhost:8080"
fi

# 설치 완료 메시지
echo ""
echo "🎉 $PRODUCT_NAME v$VERSION 설치가 완료되었습니다!"
echo ""
echo "📋 설치된 구성 요소:"
echo "  ✅ 시스템 서비스 (LaunchDaemon)"
echo "  ✅ 다중 레이어 차단 시스템"
echo "  ✅ 지속적 모니터링"
echo "  ✅ 웹 관리 인터페이스"
if [ "$install_extension" = "y" ]; then
    echo "  ✅ 브라우저 확장 프로그램"
fi
echo ""
echo "🔧 관리 명령어:"
echo "  시작: sudo launchctl start com.focustimer.enterprise"
echo "  중지: sudo launchctl stop com.focustimer.enterprise"
echo "  상태: sudo launchctl list | grep focustimer"
echo "  로그: tail -f $LOG_DIR/focus_timer.log"
echo ""
echo "🌐 웹 관리: http://localhost:8080"
echo ""
echo "💡 시스템 재시작 후 자동으로 실행됩니다."
echo "📞 기술 지원: support@focustimer.com"