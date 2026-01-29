# 🖥️ Enhanced Remote Desktop Controller

A feature-rich web-based remote desktop controller optimized for mobile devices with advanced controls and security.

## ✨ New Features

### 🎮 Control Options
- **Virtual Joystick** - Smooth analog mouse control
- **Gyroscope/Accelerometer** - Tilt your phone to control the mouse (toggle in settings)
- **Touch Screen** - Tap anywhere on the screen to move cursor
- **Scroll Wheel** - Two-finger swipe or dedicated buttons for scrolling
- **Drag Mode** - Toggle to enable click-and-drag operations

### 🎨 UI Improvements
- **Fullscreen Mode** - Immersive gaming-style interface with overlay controls
- **Customizable Layout** - Drag buttons to your preferred positions (fullscreen mode)
- **Status Bar** - Real-time connection status and zoom level display
- **Modern Design** - Sleek dark theme with smooth animations
- **Visual Feedback** - Click highlights, scroll indicators, and status updates

### 🔒 Enhanced Security
- **Session Management** - 2-hour auto-logout with secure sessions
- **Password Protection** - Hashed passwords with environment variable support
- **Login Feedback** - Clear error messages for failed attempts
- **Connection Monitoring** - Real-time status indicator

### 🔧 Advanced Features
- **Smart Zoom** - Zoom centers on mouse cursor position (not screen center)
- **Volume Control** - System volume adjustment from your phone
- **Audio Integration** - Full Windows audio API integration
- **Adjustable Sensitivity** - Control mouse movement speed
- **Stream Quality Options** - Balance between speed and quality
- **Keyboard Input** - Type directly from your phone

## 📋 Requirements

- Python 3.8+
- Windows OS (for audio control features)
- Webcam/screen capture support

## 🚀 Installation

1. **Clone or download this repository**

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set environment variables (optional):**
```bash
# Windows Command Prompt
set SECRET_KEY=your_secure_secret_key_here
set REMOTE_PASS=your_password_here

# Windows PowerShell
$env:SECRET_KEY="your_secure_secret_key_here"
$env:REMOTE_PASS="your_password_here"

# Linux/Mac
export SECRET_KEY=your_secure_secret_key_here
export REMOTE_PASS=your_password_here
```

4. **Run the server:**
```bash
python enhanced_remote_desktop.py
```

5. **Access from your phone:**
   - Connect your phone to the same network
   - Find your computer's IP address:
     - Windows: `ipconfig` (look for IPv4 Address)
     - Mac/Linux: `ifconfig` or `ip addr`
   - Open browser on phone: `http://YOUR_IP:5000`
   - Default password: `1234`

## 🎯 Usage Guide

### Normal Mode
- **Joystick** - Move mouse by dragging the virtual joystick
- **Tap Screen** - Click anywhere on the video to move cursor there
- **Buttons** - Use control buttons for clicks, scrolling, zoom
- **Settings** - Access advanced options via settings panel

### Fullscreen Mode
- **Overlay Controls** - Buttons float over the screen
- **Joystick** - Positioned in bottom-left corner
- **Exit** - Top-left button to return to normal mode
- **All Features** - Full functionality in immersive view

### Gyroscope Control
1. Enable in Settings panel
2. Grant permission when prompted (iOS/Android)
3. Tilt phone to move mouse cursor
4. Adjust sensitivity to your preference

### Zoom Features
- **Zoom In/Out** - Use +/- buttons
- **Smart Center** - Zoom focuses on current mouse position
- **Reset** - Return to 100% zoom instantly
- **Range** - 100% to 400% zoom levels

### Volume Control
- Tap volume button to show slider
- Drag slider to adjust system volume
- Works with Windows audio system
- Real-time volume changes

## 🔧 Configuration

### Security Settings
Edit the script to change:
- `SECRET_KEY` - Flask session encryption key
- `PASSWORD_HASH` - Login password (hashed)
- Session timeout (default: 2 hours)

### Performance Settings
- Stream quality: Adjust JPEG quality (line ~550)
- Frame rate: Modify sleep time (line ~595)
- Resolution: Change resize dimensions (line ~572)

### Controls
- Mouse sensitivity: 1-10 scale in settings
- Joystick size: Auto-adjusts for fullscreen
- Scroll speed: 3 lines per scroll (adjustable in code)

## 📱 Mobile Optimization

### Gyroscope Support
- **iOS**: Requires HTTPS for gyroscope access
- **Android**: Works on HTTP and HTTPS
- **Permission**: Browser will prompt for motion sensors

### Touch Gestures
- **Single tap** - Move cursor
- **Two-finger swipe** - Scroll up/down
- **Joystick drag** - Analog mouse control

### Fullscreen Tips
- Use fullscreen for gaming/media control
- Button positions can be customized
- Joystick relocates to corner
- Exit button always accessible

## 🐛 Troubleshooting

### Audio Control Not Working
- Install pycaw: `pip install pycaw comtypes`
- Windows only - not supported on Mac/Linux
- Check admin privileges if issues persist

### Gyroscope Not Working
- **iOS**: Must use HTTPS (consider using ngrok)
- Grant browser permission for motion sensors
- Check if device has gyroscope/accelerometer
- Try toggling off and on again

### Connection Issues
- Verify both devices on same network
- Check firewall settings (allow port 5000)
- Try different browser
- Ensure Python script is running

### Performance Issues
- Lower stream quality in settings
- Reduce zoom level
- Close other applications
- Check network bandwidth

## 🔐 Security Notes

1. **Use on trusted networks only**
2. **Change default password immediately**
3. **Use strong SECRET_KEY in production**
4. **Consider using HTTPS** (for gyroscope on iOS)
5. **Firewall rules** - Restrict to local network
6. **Monitor access logs** - Check for unauthorized attempts

## 🎓 Advanced Usage

### Using HTTPS (for iOS gyroscope)
```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Modify the app.run() line to:
app.run(host='0.0.0.0', port=5000, threaded=True, ssl_context=('cert.pem', 'key.pem'))
```

### Remote Access (Use with caution!)
```bash
# Using ngrok for external access
ngrok http 5000
# Use the provided URL to access remotely
```


yes this read me was written by ai
and enhanced by ai
