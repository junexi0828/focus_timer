# Focus Timer - Professional Focus Management System

<div align="center">

![Focus Timer](https://img.shields.io/badge/Focus%20Timer-Professional-blue?style=for-the-badge&logo=python)
![Python](https://img.shields.io/badge/Python-3.13+-green?style=for-the-badge&logo=python)
![macOS](https://img.shields.io/badge/macOS-10.15+-orange?style=for-the-badge&logo=apple)
![License](https://img.shields.io/badge/License-Commercial-red?style=for-the-badge)

**Professional-grade focus management system for enhanced productivity**

[Personal](#personal-edition) • [macOS App](#-macos-앱) • [Enterprise CLI](#enterprise-cli-edition) • [Enterprise GUI](#enterprise-gui-edition) • [Enterprise Web](#enterprise-web-edition)

**[한국어 버전](README.md)**

</div>

---

## 🎯 Product Lineup

<div align="center">

| Product | Target | Features | Pricing |
|---------|--------|----------|---------|
| **[Personal Edition](#personal-edition)** | Individual Users | Simple Terminal-based | **Free** |
| **[macOS App](#-macos-앱)** | macOS Users | Native App Bundle | **$6/month** |
| **[Enterprise CLI Edition](#enterprise-cli-edition)** | Organizations | System Services + CLI | **$4/month** |
| **[Enterprise GUI Edition](#enterprise-gui-edition)** | Organizations | GUI + System Services | **$4/month** |
| **[Enterprise Web Edition](#enterprise-web-edition)** | Organizations | Web Interface + Cloud | **$7/month** |

</div>

---

## 📱 Personal Edition

<div align="center">

![Personal Edition](https://img.shields.io/badge/Personal-Edition-green?style=for-the-badge)

**Simple and effective personal focus management**

</div>

### ✨ Key Features
- 🚫 **Complete YouTube Blocking** - Core domains and API services blocking
- 🔐 **Algorithm-based Exit Prevention** - Difficulty-based problem solving required
- 🔄 **Browser Force Restart** - Automatic browser restart on focus mode start
- 🚀 **Auto-start System** - Automatic execution on system boot
- ⏰ **Flexible Time Settings** - Time-based/timer-based blocking

### 🎮 Usage Modes
1. **Time-based Blocking Mode** - Block at specified times daily
2. **Timer Blocking Mode** - Block for N hours from now
3. **Focus Mode (Enhanced)** - Complete exit prevention + browser restart

### 🚀 Quick Start
```bash
cd personal/
sudo python3 focus_timer.py
```

### 📁 File Structure
```
personal/
├── focus_timer.py              # Main program
├── install_focus_timer.sh      # Auto-start installation
├── uninstall_focus_timer.sh    # Auto-start removal
└── README.md                   # Detailed documentation
```

**[📖 Personal Edition Documentation →](personal/README.md)**

---

## 🍎 macOS App

<div align="center">

![macOS App](https://img.shields.io/badge/macOS-App%20Bundle-blue?style=for-the-badge&logo=apple)

**Integrated focus management system implemented as native macOS app**

</div>

### ✨ Key Features
- 🍎 **Native macOS App** - Perfect system integration
- 🖥️ **Integrated GUI Interface** - Intuitive user experience
- 💻 **CLI Command Line Tool** - Terminal control for advanced users
- 🔄 **Background Services** - Continuous monitoring and protection
- ⚙️ **Centralized Configuration Management** - JSON-based configuration system
- 🛡️ **System-level Protection** - Hosts file permission management
- 🚀 **Standalone Executable** - Fully independent app bundle with PyInstaller
- 🔄 **Auto-restart System** - LaunchAgent-based background services
- 🖥️ **Auto-start on System Boot** - Automatic execution after power restart
- 🛡️ **File Monitoring** - Hosts file tampering prevention and auto-recovery

### 🎮 Usage Modes
1. **GUI Mode** - All control via mouse clicks
2. **CLI Mode** - Advanced control via terminal
3. **Background Mode** - Automatic monitoring and protection

### 🚀 Quick Start
```bash
# App execution (double-click or terminal)
open /Applications/FocusTimer.app

# CLI mode
/Applications/FocusTimer.app/Contents/MacOS/FocusTimerCLI

# Background service status check
launchctl list | grep focustimer

# Log monitoring
tail -f /var/log/FocusTimer/focus_timer.log
```

### 📁 File Structure
```
FocusTimer.app/
├── Contents/
│   ├── Info.plist                    # App bundle information
│   ├── MacOS/
│   │   ├── FocusTimer               # Main GUI application (standalone executable)
│   │   ├── FocusTimerCLI            # Command line interface
│   │   └── FocusTimerHelper         # Background service
│   └── Resources/
│       ├── config.json              # App configuration file
│       ├── com.focustimer.helper.plist  # LaunchAgent configuration
│       ├── FocusTimer.icns          # App icon
│       ├── algorithm_tab.py         # Algorithm system
│       ├── gui_algorithm_manager.py # Algorithm GUI management
│       └── user_data/               # User data
```

**[📖 macOS App Documentation →](FocusTimer.app/README.md)**

---

## 💻 Enterprise CLI Edition

<div align="center">

![Enterprise CLI](https://img.shields.io/badge/Enterprise-CLI-blue?style=for-the-badge)

**System-level protection and continuous monitoring**

</div>

### ✨ Key Features
- 🛡️ **System-level Protection** - Hosts file permission management
- 👁️ **Continuous File Monitoring** - Real-time change detection
- 🔒 **Multi-layer Blocking** - Hosts + DNS + browser cache
- 🧮 **Algorithm Problem System** - 5-level difficulty
- 📊 **Real-time Logging** - Detailed system event recording
- 💾 **State Persistence Management** - Automatic configuration and state saving

### 🔧 System Services
- **LaunchDaemon Registration** - Automatic background execution
- **Auto-recovery** - Automatic re-application on unblock attempts
- **Security Enhancement** - Automatic response on bypass attempts

### 🚀 Quick Start
```bash
cd enterprise/
sudo python3 setup_enterprise.py      # Setup
sudo python3 focus_timer_enterprise.py # Execute
```

### 📁 File Structure
```
enterprise/
├── focus_timer_enterprise.py  # Main program
├── setup_enterprise.py        # Setup tool
└── README.md                  # Detailed documentation
```

**[📖 Enterprise CLI Edition Documentation →](enterprise/README.md)**

---

## 🖥️ Enterprise GUI Edition

<div align="center">

![Enterprise GUI](https://img.shields.io/badge/Enterprise-GUI-purple?style=for-the-badge)

**Perfect combination of GUI interface and system services**

</div>

### ✨ Key Features
- 🖥️ **Intuitive GUI Interface** - All control via mouse clicks
- 📊 **Real-time Status Monitoring** - Current status at a glance
- 🎛️ **Integrated Control Panel** - Focus mode start/stop, immediate block/unblock
- 📈 **Statistics Dashboard** - Block count, bypass attempts, difficulty display
- 📝 **Real-time Log Viewer** - Real-time system event monitoring
- ⚙️ **One-click Configuration** - Time, difficulty, security options setup

### 🎮 GUI Components
- **Status Display Panel** - Current focus mode status and time
- **Control Panel** - Focus mode start/stop, immediate block/unblock
- **Statistics Dashboard** - Block count, bypass attempts, current difficulty
- **Real-time Log Viewer** - System events, security warnings, error messages

### 🚀 Quick Start
```bash
cd enterprise_gui/
sudo python3 focus_timer_enterprise_gui.py
```

### 📁 File Structure
```
enterprise_gui/
├── focus_timer_enterprise_gui.py  # GUI main program
└── README.md                      # Detailed documentation
```

**[📖 Enterprise GUI Edition Documentation →](enterprise_gui/README.md)**

---

## 🌐 Enterprise Web Edition

<div align="center">

![Enterprise Web](https://img.shields.io/badge/Enterprise-Web-orange?style=for-the-badge)

**Web interface and cloud-based remote management**

</div>

### ✨ Key Features
- 🌐 **Web-based Interface** - Accessible via browser
- ☁️ **Cloud Management** - Remote system control
- 📱 **Responsive Design** - Mobile, tablet, desktop support
- 🔐 **Multi-user Support** - Team-level management
- 📊 **Advanced Analytics** - Usage patterns and productivity analysis
- 🔄 **Real-time Synchronization** - Settings sync across multiple devices

### 🎯 Use Cases
- **Enterprise Environment** - Centralized management by IT administrators
- **Team Collaboration** - Integrated focus mode management for team members
- **Remote Work** - Focus mode management in work-from-home environments
- **Educational Institutions** - Student learning environment management

### 🚀 Quick Start
```bash
cd enterprise_web/
sudo python3 focus_timer_enterprise_web.py
```

### 📁 File Structure
```
enterprise_web/
├── focus_timer_enterprise_web.py  # Web server program
└── README.md                      # Detailed documentation
```

**[📖 Enterprise Web Edition Documentation →](enterprise_web/README.md)**

---

## ⚙️ Configuration Management System

<div align="center">

![Config Management](https://img.shields.io/badge/Config-Management-gray?style=for-the-badge)

**Centralized configuration management and GUI editing tools**

</div>

### ✨ Key Features
- 📝 **JSON-based Configuration** - Structured configuration file management
- 🖥️ **GUI Configuration Editor** - 6-tab categorized configuration management
- 🔄 **Real-time Configuration Changes** - Immediate application of changes
- 📤 **Configuration Backup/Restore** - Export/import configurations
- ✅ **Configuration Validation** - Automatic configuration error detection
- 📊 **Configuration Summary View** - Current configuration status at a glance

### 🎛️ Configuration Categories
1. **General** - App information, system paths
2. **Websites** - Blocked site management
3. **Focus Mode** - Time, difficulty settings
4. **Security** - Security feature activation
5. **GUI** - Interface settings
6. **Advanced** - Logging, validation settings

### 🚀 Quick Start
```bash
cd config/
python3 config_gui.py
```

### 📁 File Structure
```
config/
├── config.json        # Main configuration file
├── config_manager.py  # Configuration management class
├── config_gui.py      # Configuration GUI tool
└── README.md          # Detailed documentation
```

**[📖 Configuration Management System Documentation →](config/README.md)**

---

## 🧮 Algorithm System (Phase 4)

<div align="center">

![Algorithm System](https://img.shields.io/badge/Algorithm-System-blue?style=for-the-badge)

**Enterprise-level algorithm problem system for coding tests**

</div>

### ✨ Key Features
- 🏗️ **Standardized Data Structures** - Platform-agnostic problem integration
- 🌐 **External Platform Integration** - Codeforces, LeetCode, Kaggle support
- 📊 **Advanced Difficulty System** - Easy, Medium, Hard, Expert levels
- 🏷️ **Algorithm Tag System** - 30+ algorithm categories
- 💾 **JSON Serialization** - Complete data storage and restoration
- 🔄 **Problem Collection Management** - Systematic problem classification and search

### 🎯 Phase 4 Plan
- **4-1 Phase**: ✅ Standard problem data structure design (Complete)
- **4-2 Phase**: ✅ External platform integration system (Complete)
- **4-3 Phase**: 📋 Advanced algorithm challenge system (Planned)
- **4-4 Phase**: 🖥️ GUI algorithm management interface (Planned)

### 📁 File Structure
```
algorithm_system/
├── problem_data_structures.py      # Core data structures
├── remote_problem_provider.py      # External platform integration system
├── example_problems.py             # Data structure usage examples
├── remote_provider_example.py      # External platform integration examples
├── __init__.py                     # Package initialization
└── README.md                       # Detailed documentation
```

### 🚀 Quick Start
```bash
# Data structure examples
cd algorithm_system
python3 example_problems.py

# External platform integration examples
python3 remote_provider_example.py
```

**[📖 Algorithm System Documentation →](algorithm_system/README.md)**

---

## 📦 Installation & Deployment

<div align="center">

![Installation](https://img.shields.io/badge/Installation-Scripts-yellow?style=for-the-badge)

**Automated installation and deployment scripts**

</div>

### 🚀 Installation Scripts
- **Personal Edition**: `personal/install_focus_timer.sh`
- **macOS App**: `installers/install_focustimer_app.sh`
- **Enterprise Edition**: `installers/install_enterprise.sh`
- **Uninstall Scripts**: Version-specific uninstall scripts

### 📋 System Requirements
- **OS**: macOS 10.15+
- **Python**: 3.13+
- **Permissions**: Administrator privileges (sudo)
- **Packages**: watchdog, psutil (Enterprise versions)

### 🔧 Dependency Installation
```bash
# Create Python virtual environment
python3 -m venv focus_timer_env
source focus_timer_env/bin/activate

# Install required packages
pip install watchdog psutil

# Install Tkinter (for GUI versions)
brew install python-tk@3.13
```

### 📁 Installation File Structure
```
installers/
├── install_focustimer_app.sh  # macOS app installation
├── uninstall_focustimer_app.sh # macOS app removal
├── update_focustimer_app.sh   # macOS app update
├── install_enterprise.sh      # Enterprise version installation
├── uninstall_enterprise.sh    # Enterprise version removal
└── README.md                  # Installation guide
```

---

## 📊 Feature Comparison

<div align="center">

| Feature | Personal | macOS App | Enterprise CLI | Enterprise GUI | Enterprise Web |
|---------|----------|-----------|----------------|----------------|----------------|
| **Basic Blocking** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Algorithm Problems** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Advanced Algorithm System** | ❌ | ✅ | ❌ | ❌ | ❌ |
| **System Services** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **GUI Interface** | ❌ | ✅ | ❌ | ✅ | ❌ |
| **CLI Interface** | ❌ | ✅ | ✅ | ❌ | ❌ |
| **Web Interface** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Configuration Management** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Logging System** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Multi-layer Blocking** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **File Monitoring** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Auto-recovery** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Remote Management** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Multi-user Support** | ❌ | ❌ | ❌ | ❌ | ✅ |

</div>

---

## 🎯 Use Cases

### 👤 Individual Users
- **Recommended Product**: Personal Edition
- **Purpose**: Personal productivity enhancement
- **Key Features**: YouTube blocking, exit prevention
- **Installation**: Single file execution

### 🍎 macOS Users
- **Recommended Product**: macOS App
- **Purpose**: macOS-optimized focus management
- **Key Features**: Native app, GUI/CLI integration
- **Installation**: App bundle installation

### 🏢 Small Organizations
- **Recommended Product**: Enterprise CLI Edition
- **Purpose**: Employee productivity management
- **Key Features**: System services, logging
- **Installation**: Automated installation script

### 🏢 Medium/Large Organizations
- **Recommended Product**: Enterprise GUI Edition
- **Purpose**: IT administrator convenience
- **Key Features**: GUI management, real-time monitoring
- **Installation**: Automated installation script

### 🌐 Cloud-based Organizations
- **Recommended Product**: Enterprise Web Edition
- **Purpose**: Remote management, team collaboration
- **Key Features**: Web interface, multi-user support
- **Installation**: Automated installation script

---

## 📞 Support & Contact

<div align="center">

![Support](https://img.shields.io/badge/Support-Available-green?style=for-the-badge)

</div>

### 📧 Contact Information
- **Developer**: juns
- **Email**: junexi0828@gmail.com
- **Blog**: [https://velog.io/@junexi0828/posts](https://velog.io/@junexi0828/posts)
- **GitHub**: [Focus Timer Repository](https://github.com/your-repo/focus-timer)

### 📚 Documentation
- **[Personal Edition](personal/README.md)** - Personal edition documentation
- **[macOS App](FocusTimer.app/README.md)** - macOS app documentation
- **[Enterprise CLI Edition](enterprise/README.md)** - Enterprise CLI documentation
- **[Enterprise GUI Edition](enterprise_gui/README.md)** - Enterprise GUI documentation
- **[Enterprise Web Edition](enterprise_web/README.md)** - Enterprise web documentation
- **[Configuration Management](config/README.md)** - Configuration management documentation
- **[Algorithm System](algorithm_system/README.md)** - Phase 4 algorithm system
- **[License](docs/LICENSE)** - License information

### 🐛 Troubleshooting
1. **Log Check**: `/var/log/FocusTimer/focus_timer.log`
2. **Permission Check**: `ls -la /etc/hosts`
3. **Service Status**: `sudo launchctl list | grep focustimer`
4. **Configuration Check**: `config/config.json`
5. **App Bundle Status**: `file /Applications/FocusTimer.app/Contents/MacOS/FocusTimer`
6. **LaunchAgent Status**: `launchctl list | grep focustimer`

---

<div align="center">

**💡 Focus Timer is designed to help enhance productivity and develop self-control.**

![Made with ❤️](https://img.shields.io/badge/Made%20with-❤️-red?style=for-the-badge)

</div>