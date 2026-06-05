# ⚡ Anarchy Matrix Launcher
### Ultra‑Premium Minecraft Instance Orchestrator for Bazzite & Immutable Linux

Anarchy Matrix is a high‑performance, cyberpunk‑themed Minecraft Instance Lifecycle Manager designed for modern immutable Linux systems like **Bazzite**, **Fedora Silverblue**, and **uBlue**.  
It delivers a fully isolated, sandboxed, AI‑augmented launcher experience that rivals advanced tools like Prism Launcher — but with a darker, faster, more modular architecture.

---

## ✨ Features

### 🧩 Instance Matrix & Modpack Hub
- Beautiful grid of isolated Minecraft instances  
- One‑click Modpack ingestion (Modrinth, CurseForge, FTB, Technic)  
- Configuration cloning & ZIP exporting  
- Clean folder isolation for every environment  

### 📦 Add‑On Repository & Dependency Solver
- Multi‑source add‑on search (Modrinth + CurseForge)  
- Auto‑resolving dependency engine  
- Smooth installation pipeline for Mods, Resource Packs, and Shaders  

### 🧑‍🚀 Identity Control Center
- Hot‑swappable Microsoft OAuth accounts  
- Offline developer personas for zero‑network testing  
- Skin & cape preview panel  

### ⚙️ System Tuning & Runtime Management
- Global & per‑instance RAM allocation  
- Java runtime detection (system + user‑space)  
- One‑click OpenJDK downloads (8 / 17 / 21)  
- Custom display overrides & JVM flag injection  

### 📡 Engine Telemetry & Lifecycle Controls
- Real‑time colored terminal output  
- Crash log exporting (mclo.gs‑style)  
- Emergency kill switch for frozen game processes  

### 🤖 In‑Game AI Automation Deck
- Live automation telemetry  
- Execution token tracking  
- Natural‑language command interface  
- Start/stop automation routines  

---

## 🧱 Architecture

The launcher is built with:

- **PySide6** (or PyQt5 fallback)  
- **Thread‑isolated backend services**  
- **Modular UI panels**  
- **Dedicated worker threads for all heavy operations**  
- **Immutable‑friendly filesystem behavior**  
- **Zero blocking on the main UI thread**

Everything is structured for clarity, extensibility, and long‑term maintainability.

---

## 🚀 Quick Start (Bazzite / Silverblue)

```bash
# 1. Enter a toolbox or distrobox (recommended)
toolbox create -y anarchy-matrix
toolbox enter anarchy-matrix

# 2. Install Python
sudo dnf install -y python3 python3-pip

# 3. Clone the repo
git clone https://github.com/YOURNAME/anarchy-matrix-launcher.git
cd anarchy-matrix-launcher

# 4. Install dependencies
pip install -r requirements.txt

# 5. Launch
python main.py
