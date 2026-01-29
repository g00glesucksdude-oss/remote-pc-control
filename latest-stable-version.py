import os
import time
import cv2
import numpy as np
import mss
import pyautogui
from flask import Flask, render_template_string, request, Response, session, redirect, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import json
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "night_shift_joystick_secure_v2")

# --- CONFIGURATION ---
PASSWORD_HASH = generate_password_hash(os.environ.get("REMOTE_PASS", "1234"))
SCREEN_W, SCREEN_H = pyautogui.size()
pyautogui.FAILSAFE = False
zoom_factor = 1.0
zoom_center_x = SCREEN_W // 2
zoom_center_y = SCREEN_H // 2
last_click_time = 0

# Initialize audio control
try:
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    audio_available = True
except:
    audio_available = False
    volume = None

# --- HTML INTERFACE ---
INTERFACE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/nipplejs/0.10.1/nipplejs.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            background: #0a0a0a; 
            color: white; 
            font-family: 'Segoe UI', sans-serif; 
            overflow: hidden; 
            touch-action: none;
            user-select: none;
            -webkit-user-select: none;
        }
        
        /* Normal Mode */
        #normal-mode { display: block; }
        #fullscreen-mode { display: none; }
        
        /* Fullscreen Mode */
        .fullscreen #normal-mode { display: none; }
        .fullscreen #fullscreen-mode { display: block; }
        
        #viewer { 
            width: 100vw; 
            height: 55vh; 
            background: #111; 
            position: relative; 
            overflow: hidden;
        }
        
        .fs-viewer {
            cursor: crosshair !important;
        }
        
        #stream { 
            width: 100%; 
            height: 100%; 
            object-fit: contain; 
            cursor: crosshair; 
        }
        
        #stream-fs {
            width: 100%; 
            height: 100%; 
            object-fit: contain; 
            cursor: crosshair;
            pointer-events: auto;
        }
        
        .fullscreen #viewer {
            height: 100vh;
            width: 100vw;
        }
        
        #joystick-zone { 
            width: 100vw; 
            height: 20vh; 
            background: #1a1a1a; 
            position: relative; 
            border-top: 2px solid #333;
        }
        
        #joystick-zone-fs {
            position: fixed;
            bottom: 60px;
            left: 20px;
            height: 180px;
            width: 180px;
            background: rgba(26, 26, 26, 0.8);
            border-radius: 50%;
            border: 2px solid #444;
            z-index: 100;
        }
        
        .fullscreen #joystick-zone {
            display: none;
        }
        
        .typing { 
            padding: 8px; 
            background: #222; 
            display: flex;
            gap: 8px;
        }
        
        .typing input { 
            flex: 1;
            background: #111; 
            color: #fff; 
            border: 1px solid #444; 
            padding: 10px;
            border-radius: 5px;
            font-size: 14px;
        }
        
        .typing button {
            width: 80px;
        }
        
        .controls { 
            display: grid; 
            grid-template-columns: repeat(3, 1fr); 
            gap: 8px; 
            padding: 10px; 
            background: #1a1a1a;
            border-top: 2px solid #333;
        }
        
        button { 
            background: linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%);
            color: white; 
            border: 1px solid #444; 
            border-radius: 8px; 
            font-size: 12px;
            font-weight: 600;
            padding: 12px 8px;
            cursor: pointer;
            transition: all 0.2s;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        button:active { 
            transform: scale(0.95); 
            background: linear-gradient(135deg, #1a1a1a 0%, #0a0a0a 100%);
        }
        
        .active { 
            background: linear-gradient(135deg, #ff4444 0%, #cc0000 100%) !important; 
            box-shadow: 0 0 15px rgba(255, 68, 68, 0.5);
        }
        
        /* Settings Panel */
        #settings-panel {
            position: fixed;
            top: 0;
            right: -100%;
            width: 300px;
            height: 100vh;
            background: #1a1a1a;
            border-left: 2px solid #333;
            transition: right 0.3s;
            overflow-y: auto;
            z-index: 1000;
            padding: 20px;
        }
        
        #settings-panel.open {
            right: 0;
        }
        
        .setting-item {
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid #333;
        }
        
        .setting-label {
            display: block;
            margin-bottom: 8px;
            color: #aaa;
            font-size: 13px;
        }
        
        input[type="range"] {
            width: 100%;
            accent-color: #4a9eff;
        }
        
        .toggle-switch {
            position: relative;
            width: 50px;
            height: 26px;
            background: #333;
            border-radius: 13px;
            cursor: pointer;
            transition: 0.3s;
        }
        
        .toggle-switch.active {
            background: #4a9eff;
        }
        
        .toggle-switch::before {
            content: '';
            position: absolute;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: white;
            top: 3px;
            left: 3px;
            transition: 0.3s;
        }
        
        .toggle-switch.active::before {
            left: 27px;
        }
        
        /* Fullscreen UI */
        .fullscreen-controls {
            position: fixed;
            display: none;
        }
        
        .fullscreen .fullscreen-controls {
            display: block;
        }
        
        .fs-btn {
            position: absolute;
            background: rgba(42, 42, 42, 0.9);
            border: 2px solid #555;
            border-radius: 12px;
            padding: 15px;
            font-size: 11px;
            min-width: 70px;
            backdrop-filter: blur(10px);
            cursor: pointer;
            transition: all 0.2s;
            z-index: 200;
        }
        
        .fs-btn.draggable {
            border-color: #4a9eff;
            box-shadow: 0 0 15px rgba(74, 158, 255, 0.5);
            cursor: move;
        }
        
        .fs-btn.dragging {
            opacity: 0.7;
            transform: scale(1.1);
        }
        
        /* Volume Control */
        #volume-control {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(26, 26, 26, 0.95);
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #444;
            display: none;
        }
        
        #volume-control.show {
            display: block;
        }
        
        .volume-slider {
            width: 150px;
            margin: 10px 0;
        }
        
        /* Scroll Indicator */
        #scroll-indicator {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(74, 158, 255, 0.9);
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            display: none;
            pointer-events: none;
            z-index: 2000;
        }
        
        /* Status Bar */
        #status-bar {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: rgba(26, 26, 26, 0.95);
            padding: 8px 15px;
            font-size: 11px;
            color: #888;
            display: flex;
            justify-content: space-between;
            z-index: 999;
            border-bottom: 1px solid #333;
        }
        
        .fullscreen #status-bar {
            background: rgba(26, 26, 26, 0.7);
            backdrop-filter: blur(10px);
        }
        
        .zoom-badge {
            background: #4a9eff;
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 10px;
        }
    </style>
</head>
<body>
    <!-- Status Bar -->
    <div id="status-bar">
        <span>🖥️ Remote Desktop</span>
        <span id="zoom-display">Zoom: <span class="zoom-badge">100%</span></span>
        <span id="connection-status">●</span>
    </div>

    <!-- Scroll Indicator -->
    <div id="scroll-indicator"></div>
    
    <!-- Volume Control -->
    <div id="volume-control">
        <div style="text-align: center; margin-bottom: 5px;">🔊 Volume</div>
        <input type="range" class="volume-slider" id="volume-slider" min="0" max="100" value="50">
        <div id="volume-value" style="text-align: center; font-size: 12px; color: #4a9eff;">50%</div>
    </div>

    <!-- Settings Panel -->
    <div id="settings-panel">
        <h3 style="margin-bottom: 20px; color: #4a9eff;">⚙️ Settings</h3>
        
        <div class="setting-item">
            <span class="setting-label">Gyroscope Control</span>
            <div class="toggle-switch" id="gyro-toggle" onclick="toggleGyro()"></div>
        </div>
        
        <div class="setting-item">
            <span class="setting-label">Mouse Sensitivity</span>
            <input type="range" id="sensitivity-slider" min="1" max="10" value="5">
            <div style="text-align: center; color: #4a9eff; font-size: 12px;" id="sensitivity-value">5</div>
        </div>
        
        <div class="setting-item">
            <span class="setting-label">Stream Quality</span>
            <select style="width: 100%; padding: 8px; background: #111; color: white; border: 1px solid #444; border-radius: 5px;">
                <option value="low">Low (Faster)</option>
                <option value="medium" selected>Medium</option>
                <option value="high">High (Slower)</option>
            </select>
        </div>
        
        <button onclick="resetButtonPositions()" style="width: 100%; margin-top: 20px;">Reset Button Positions</button>
        <button onclick="toggleSettings()" style="width: 100%; margin-top: 10px; background: #ff4444;">Close</button>
    </div>

    <!-- Normal Mode -->
    <div id="normal-mode">
        <div id="viewer">
            <img id="stream" src="{{ url_for('video_feed') }}">
        </div>
        <div id="joystick-zone"></div>
        <div class="typing">
            <input type="text" id="kb" placeholder="Type here..." onkeypress="if(event.key==='Enter')sendText()">
            <button onclick="sendText()">SEND</button>
        </div>
        <div class="controls">
            <button onclick="doAction('click')">🖱️ LEFT</button>
            <button onclick="doAction('right_click')">🖱️ RIGHT</button>
            <button id="dragBtn" onclick="toggleDrag()">✋ DRAG OFF</button>
            
            <button onclick="doAction('scroll_up')">⬆️ SCROLL</button>
            <button onclick="doAction('scroll_down')">⬇️ SCROLL</button>
            <button onclick="toggleVolume()">🔊 VOLUME</button>
            
            <button onclick="doAction('zoom_in')">🔍 ZOOM+</button>
            <button onclick="doAction('zoom_out')">🔍 ZOOM-</button>
            <button onclick="doAction('zoom_reset')">↺ RESET</button>
            
            <button onclick="toggleFullscreen()">⛶ FULL</button>
            <button onclick="toggleSettings()">⚙️ SETTINGS</button>
            <button onclick="location.href='/logout'">🔒 LOCK</button>
        </div>
    </div>

    <!-- Fullscreen Mode -->
    <div id="fullscreen-mode">
        <div id="viewer" class="fs-viewer">
            <img id="stream-fs" src="{{ url_for('video_feed') }}">
        </div>
        <div id="joystick-zone-fs"></div>
        
        <!-- Fullscreen Controls -->
        <div class="fullscreen-controls">
            <button class="fs-btn" id="fs-edit" style="top: 60px; right: 20px;" onclick="toggleEditMode()">🔓 EDIT</button>
            <button class="fs-btn" id="fs-click" style="bottom: 280px; left: 20px;" onclick="doAction('click')">LEFT</button>
            <button class="fs-btn" id="fs-right" style="bottom: 280px; left: 110px;" onclick="doAction('right_click')">RIGHT</button>
            <button class="fs-btn" id="fs-drag" style="bottom: 210px; left: 20px;" onclick="toggleDrag()">DRAG</button>
            <button class="fs-btn" id="fs-scroll-up" style="bottom: 210px; left: 110px;" onclick="doAction('scroll_up')">↑</button>
            <button class="fs-btn" id="fs-scroll-down" style="bottom: 140px; left: 110px;" onclick="doAction('scroll_down')">↓</button>
            
            <button class="fs-btn" id="fs-zoom-in" style="top: 130px; right: 20px;" onclick="doAction('zoom_in')">🔍+</button>
            <button class="fs-btn" id="fs-zoom-out" style="top: 200px; right: 20px;" onclick="doAction('zoom_out')">🔍-</button>
            <button class="fs-btn" id="fs-exit" style="top: 60px; left: 20px;" onclick="toggleFullscreen()">EXIT</button>
        </div>
    </div>

    <script>
        let isDragging = false;
        let isFullscreen = false;
        let gyroEnabled = false;
        let sensitivity = 5;
        let lastOrientation = { beta: 0, gamma: 0 };
        let orientationInitialized = false;
        let currentZoom = 1.0;
        let isEditMode = false;
        
        // Managers for both joysticks
        let normalManager = null;
        let fullscreenManager = null;
        
        // Initialize normal mode joystick
        function initNormalJoystick() {
            if (normalManager) normalManager.destroy();
            normalManager = nipplejs.create({
                zone: document.getElementById('joystick-zone'),
                mode: 'static',
                position: {left: '50%', top: '50%'},
                color: '#4a9eff',
                size: 120
            });

            let lastMove = 0;
            normalManager.on('move', function (evt, data) {
                if (gyroEnabled) return;
                
                let now = Date.now();
                if (data.direction && now - lastMove > 40) {
                    lastMove = now;
                    let speed = data.distance / 2;
                    let angle = data.angle.radian;
                    let vx = Math.cos(angle) * speed * (sensitivity / 5);
                    let vy = -Math.sin(angle) * speed * (sensitivity / 5);
                    fetch(`/action?type=move_joy&x=${vx}&y=${vy}`);
                }
            });
        }
        
        // Initialize fullscreen joystick
        function initFullscreenJoystick() {
            if (fullscreenManager) fullscreenManager.destroy();
            fullscreenManager = nipplejs.create({
                zone: document.getElementById('joystick-zone-fs'),
                mode: 'static',
                position: {left: '50%', top: '50%'},
                color: '#4a9eff',
                size: 140
            });

            let lastMove = 0;
            fullscreenManager.on('move', function (evt, data) {
                if (gyroEnabled) return;
                
                let now = Date.now();
                if (data.direction && now - lastMove > 40) {
                    lastMove = now;
                    let speed = data.distance / 2;
                    let angle = data.angle.radian;
                    let vx = Math.cos(angle) * speed * (sensitivity / 5);
                    let vy = -Math.sin(angle) * speed * (sensitivity / 5);
                    fetch(`/action?type=move_joy&x=${vx}&y=${vy}`);
                }
            });
        }
        
        // Initialize on load
        initNormalJoystick();
        initFullscreenJoystick();

        // Gyroscope control
        function toggleGyro() {
            gyroEnabled = !gyroEnabled;
            const toggle = document.getElementById('gyro-toggle');
            toggle.classList.toggle('active');
            
            if (gyroEnabled && typeof DeviceOrientationEvent !== 'undefined') {
                if (typeof DeviceOrientationEvent.requestPermission === 'function') {
                    DeviceOrientationEvent.requestPermission()
                        .then(permissionState => {
                            if (permissionState === 'granted') {
                                window.addEventListener('deviceorientation', handleOrientation);
                            } else {
                                gyroEnabled = false;
                                toggle.classList.remove('active');
                                alert('Permission denied for gyroscope');
                            }
                        })
                        .catch(console.error);
                } else {
                    window.addEventListener('deviceorientation', handleOrientation);
                }
            } else {
                window.removeEventListener('deviceorientation', handleOrientation);
                orientationInitialized = false;
            }
        }

        function handleOrientation(event) {
            if (!gyroEnabled) return;
            
            const beta = event.beta;
            const gamma = event.gamma;
            
            if (!orientationInitialized) {
                lastOrientation = { beta, gamma };
                orientationInitialized = true;
                return;
            }
            
            const deltaX = (gamma - lastOrientation.gamma) * sensitivity * 2;
            const deltaY = (beta - lastOrientation.beta) * sensitivity * 2;
            
            if (Math.abs(deltaX) > 0.5 || Math.abs(deltaY) > 0.5) {
                fetch(`/action?type=move_joy&x=${deltaX}&y=${deltaY}`);
            }
            
            lastOrientation = { beta, gamma };
        }

        // Sensitivity control
        document.getElementById('sensitivity-slider').addEventListener('input', function(e) {
            sensitivity = parseInt(e.target.value);
            document.getElementById('sensitivity-value').textContent = sensitivity;
        });

        // Volume control
        function toggleVolume() {
            const vol = document.getElementById('volume-control');
            vol.classList.toggle('show');
        }

        document.getElementById('volume-slider').addEventListener('input', function(e) {
            const val = e.target.value;
            document.getElementById('volume-value').textContent = val + '%';
            fetch(`/action?type=volume&val=${val}`);
        });

        // Get current volume on load
        fetch('/get_volume').then(r => r.json()).then(data => {
            if (data.volume !== null) {
                const vol = Math.round(data.volume * 100);
                document.getElementById('volume-slider').value = vol;
                document.getElementById('volume-value').textContent = vol + '%';
            }
        });

        function toggleDrag() {
            isDragging = !isDragging;
            const btns = document.querySelectorAll('#dragBtn, #fs-drag');
            btns.forEach(btn => {
                btn.innerText = isDragging ? "✋ DRAG ON" : "✋ DRAG OFF";
                btn.classList.toggle('active');
            });
            fetch(`/action?type=${isDragging ? 'drag_start' : 'drag_end'}`);
        }

        function toggleFullscreen() {
            isFullscreen = !isFullscreen;
            document.body.classList.toggle('fullscreen');
            
            // Load saved button positions if exiting edit mode
            if (isFullscreen) {
                loadButtonPositions();
            }
            
            // Request fullscreen API
            if (isFullscreen && document.documentElement.requestFullscreen) {
                document.documentElement.requestFullscreen();
            } else if (document.exitFullscreen) {
                document.exitFullscreen();
            }
        }

        function toggleSettings() {
            document.getElementById('settings-panel').classList.toggle('open');
        }

        function sendText() {
            const input = document.getElementById('kb');
            if (input.value.trim() !== "") {
                fetch(`/action?type=type&val=${encodeURIComponent(input.value)}`);
                input.value = '';
            }
        }

        function doAction(type) {
            fetch(`/action?type=${type}`);
        }

        // Click/tap on screen to move mouse (NORMAL MODE)
        document.getElementById('viewer').addEventListener('click', function(e) {
            if (e.target.tagName === 'IMG') {
                const rect = e.target.getBoundingClientRect();
                const x = (e.clientX - rect.left) / rect.width * {{ screen_w }};
                const y = (e.clientY - rect.top) / rect.height * {{ screen_h }};
                fetch(`/action?type=move_abs&x=${x}&y=${y}`);
            }
        });
        
        // Click/tap on screen to move mouse (FULLSCREEN MODE)
        document.addEventListener('click', function(e) {
            if (!isFullscreen) return;
            
            const streamFs = document.getElementById('stream-fs');
            const viewer = streamFs.closest('.fs-viewer');
            
            // Check if click is on the video stream (not on buttons)
            if (e.target === streamFs || e.target === viewer) {
                const rect = streamFs.getBoundingClientRect();
                const x = (e.clientX - rect.left) / rect.width * {{ screen_w }};
                const y = (e.clientY - rect.top) / rect.height * {{ screen_h }};
                fetch(`/action?type=move_abs&x=${x}&y=${y}`);
            }
        });

        // Wheel scroll on desktop
        document.getElementById('viewer').addEventListener('wheel', function(e) {
            e.preventDefault();
            const direction = e.deltaY > 0 ? 'scroll_down' : 'scroll_up';
            const indicator = document.getElementById('scroll-indicator');
            indicator.textContent = e.deltaY > 0 ? '↓ Scroll Down' : '↑ Scroll Up';
            indicator.style.display = 'block';
            fetch(`/action?type=${direction}`);
            setTimeout(() => indicator.style.display = 'none', 500);
        }, { passive: false });

        // Touch scroll on mobile (two-finger swipe)
        let touchStartY = 0;
        const viewers = [document.getElementById('viewer'), document.querySelector('.fs-viewer')];
        
        viewers.forEach(viewer => {
            if (!viewer) return;
            
            viewer.addEventListener('touchstart', function(e) {
                if (e.touches.length === 2) {
                    touchStartY = (e.touches[0].clientY + e.touches[1].clientY) / 2;
                }
            });

            viewer.addEventListener('touchmove', function(e) {
                if (e.touches.length === 2) {
                    e.preventDefault();
                    const currentY = (e.touches[0].clientY + e.touches[1].clientY) / 2;
                    const delta = touchStartY - currentY;
                    
                    if (Math.abs(delta) > 30) {
                        const direction = delta > 0 ? 'scroll_up' : 'scroll_down';
                        const indicator = document.getElementById('scroll-indicator');
                        indicator.textContent = delta > 0 ? '↑ Scroll Up' : '↓ Scroll Down';
                        indicator.style.display = 'block';
                        fetch(`/action?type=${direction}`);
                        touchStartY = currentY;
                        setTimeout(() => indicator.style.display = 'none', 500);
                    }
                }
            }, { passive: false });
        });

        // Update zoom display
        setInterval(() => {
            fetch('/get_zoom').then(r => r.json()).then(data => {
                const zoomPercent = Math.round(data.zoom * 100);
                document.querySelector('.zoom-badge').textContent = zoomPercent + '%';
                currentZoom = data.zoom;
            });
        }, 1000);

        // Edit mode for draggable buttons
        function toggleEditMode() {
            isEditMode = !isEditMode;
            const editBtn = document.getElementById('fs-edit');
            const buttons = document.querySelectorAll('.fs-btn:not(#fs-edit):not(#fs-exit)');
            
            if (isEditMode) {
                editBtn.textContent = '🔒 LOCK';
                editBtn.classList.add('active');
                buttons.forEach(btn => {
                    btn.classList.add('draggable');
                    makeDraggable(btn);
                });
            } else {
                editBtn.textContent = '🔓 EDIT';
                editBtn.classList.remove('active');
                buttons.forEach(btn => {
                    btn.classList.remove('draggable');
                    removeDraggable(btn);
                });
                saveButtonPositions();
            }
        }

        // Draggable functionality
        function makeDraggable(element) {
            let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
            
            element.onmousedown = dragMouseDown;
            element.ontouchstart = dragTouchStart;

            function dragMouseDown(e) {
                e.preventDefault();
                pos3 = e.clientX;
                pos4 = e.clientY;
                document.onmouseup = closeDragElement;
                document.onmousemove = elementDrag;
                element.classList.add('dragging');
            }
            
            function dragTouchStart(e) {
                e.preventDefault();
                const touch = e.touches[0];
                pos3 = touch.clientX;
                pos4 = touch.clientY;
                document.ontouchend = closeDragElement;
                document.ontouchmove = elementDragTouch;
                element.classList.add('dragging');
            }

            function elementDrag(e) {
                e.preventDefault();
                pos1 = pos3 - e.clientX;
                pos2 = pos4 - e.clientY;
                pos3 = e.clientX;
                pos4 = e.clientY;
                
                const newTop = element.offsetTop - pos2;
                const newLeft = element.offsetLeft - pos1;
                
                // Keep within bounds
                const maxTop = window.innerHeight - element.offsetHeight;
                const maxLeft = window.innerWidth - element.offsetWidth;
                
                element.style.top = Math.max(0, Math.min(newTop, maxTop)) + "px";
                element.style.left = Math.max(0, Math.min(newLeft, maxLeft)) + "px";
                element.style.bottom = 'auto';
                element.style.right = 'auto';
            }
            
            function elementDragTouch(e) {
                e.preventDefault();
                const touch = e.touches[0];
                pos1 = pos3 - touch.clientX;
                pos2 = pos4 - touch.clientY;
                pos3 = touch.clientX;
                pos4 = touch.clientY;
                
                const newTop = element.offsetTop - pos2;
                const newLeft = element.offsetLeft - pos1;
                
                const maxTop = window.innerHeight - element.offsetHeight;
                const maxLeft = window.innerWidth - element.offsetWidth;
                
                element.style.top = Math.max(0, Math.min(newTop, maxTop)) + "px";
                element.style.left = Math.max(0, Math.min(newLeft, maxLeft)) + "px";
                element.style.bottom = 'auto';
                element.style.right = 'auto';
            }

            function closeDragElement() {
                document.onmouseup = null;
                document.onmousemove = null;
                document.ontouchend = null;
                document.ontouchmove = null;
                element.classList.remove('dragging');
            }
        }

        function removeDraggable(element) {
            element.onmousedown = null;
            element.ontouchstart = null;
        }

        // Save and load button positions
        function saveButtonPositions() {
            const positions = {};
            document.querySelectorAll('.fs-btn').forEach(btn => {
                if (btn.id && btn.id !== 'fs-edit' && btn.id !== 'fs-exit') {
                    positions[btn.id] = {
                        top: btn.style.top,
                        left: btn.style.left,
                        bottom: btn.style.bottom,
                        right: btn.style.right
                    };
                }
            });
            localStorage.setItem('buttonPositions', JSON.stringify(positions));
        }

        function loadButtonPositions() {
            const saved = localStorage.getItem('buttonPositions');
            if (saved) {
                const positions = JSON.parse(saved);
                Object.keys(positions).forEach(id => {
                    const btn = document.getElementById(id);
                    if (btn) {
                        Object.assign(btn.style, positions[id]);
                    }
                });
            }
        }

        function resetButtonPositions() {
            localStorage.removeItem('buttonPositions');
            location.reload();
        }

        // Keep connection status updated
        setInterval(() => {
            fetch('/ping').then(() => {
                document.getElementById('connection-status').style.color = '#4eff4e';
            }).catch(() => {
                document.getElementById('connection-status').style.color = '#ff4444';
            });
        }, 2000);
        
        // Load button positions on startup
        setTimeout(loadButtonPositions, 500);
    </script>
</body>
</html>
"""

# --- ROUTES ---
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        pw = request.form.get('p')
        if pw and check_password_hash(PASSWORD_HASH, pw):
            session['auth'] = True
            session.permanent = True
            app.permanent_session_lifetime = timedelta(hours=2)
            return redirect(url_for('remote'))
        else:
            return render_template_string("""
            <body style='background:#0a0a0a;color:#fff;text-align:center;padding:50px;font-family:sans-serif;'>
                <div style='max-width:300px;margin:auto;'>
                    <h2 style='color:#ff4444;margin-bottom:20px;'>❌ Invalid Password</h2>
                    <form method='POST'>
                        <input type='password' name='p' placeholder='Enter password' 
                               style='width:100%;padding:12px;background:#1a1a1a;color:#fff;border:1px solid #444;border-radius:5px;margin-bottom:10px;'>
                        <input type='submit' value='Login' 
                               style='width:100%;padding:12px;background:#4a9eff;color:#fff;border:none;border-radius:5px;cursor:pointer;font-weight:bold;'>
                    </form>
                </div>
            </body>
            """)
    return render_template_string("""
    <body style='background:#0a0a0a;color:#fff;text-align:center;padding:50px;font-family:sans-serif;'>
        <div style='max-width:300px;margin:auto;'>
            <h2 style='color:#4a9eff;margin-bottom:20px;'>🖥️ Remote Desktop</h2>
            <form method='POST'>
                <input type='password' name='p' placeholder='Enter password' 
                       style='width:100%;padding:12px;background:#1a1a1a;color:#fff;border:1px solid #444;border-radius:5px;margin-bottom:10px;'>
                <input type='submit' value='Login' 
                       style='width:100%;padding:12px;background:#4a9eff;color:#fff;border:none;border-radius:5px;cursor:pointer;font-weight:bold;'>
            </form>
        </div>
    </body>
    """)

@app.route('/remote')
def remote():
    if not session.get('auth'): 
        return redirect(url_for('login'))
    return render_template_string(INTERFACE, screen_w=SCREEN_W, screen_h=SCREEN_H)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/ping')
def ping():
    if not session.get('auth'):
        return "Unauthorized", 401
    return "OK"

@app.route('/get_volume')
def get_volume():
    if not session.get('auth'):
        return jsonify({'volume': None}), 401
    if audio_available and volume:
        try:
            current_vol = volume.GetMasterVolumeLevelScalar()
            return jsonify({'volume': current_vol})
        except:
            pass
    return jsonify({'volume': None})

@app.route('/get_zoom')
def get_zoom():
    if not session.get('auth'):
        return jsonify({'zoom': 1.0}), 401
    return jsonify({'zoom': zoom_factor})

@app.route('/video_feed')
def video_feed():
    if not session.get('auth'):
        return "Unauthorized", 401
        
    def gen():
        global zoom_factor, zoom_center_x, zoom_center_y, last_click_time
        with mss.mss() as sct:
            monitor = sct.monitors[1]
            while True:
                img = np.array(sct.grab(monitor))
                frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

                # Get current mouse position for zoom center
                pos_x, pos_y = pyautogui.position()

                # Zoom logic - zoom at mouse cursor position
                if zoom_factor > 1.0:
                    h, w = frame.shape[:2]
                    
                    # Calculate the size of the zoomed region
                    new_h = int(h / zoom_factor)
                    new_w = int(w / zoom_factor)
                    
                    # Center the zoom on the mouse cursor
                    center_x = int(pos_x * w / SCREEN_W)
                    center_y = int(pos_y * h / SCREEN_H)
                    
                    # Calculate crop boundaries
                    x1 = max(0, center_x - new_w // 2)
                    y1 = max(0, center_y - new_h // 2)
                    x2 = min(w, x1 + new_w)
                    y2 = min(h, y1 + new_h)
                    
                    # Adjust if at edges
                    if x2 - x1 < new_w:
                        x1 = max(0, x2 - new_w)
                    if y2 - y1 < new_h:
                        y1 = max(0, y2 - new_h)
                    
                    frame = frame[y1:y2, x1:x2]
                    frame = cv2.resize(frame, (960, 540))
                else:
                    frame = cv2.resize(frame, (960, 540))

                # Cursor overlay
                scale_x = 960 / SCREEN_W
                scale_y = 540 / SCREEN_H
                
                if zoom_factor > 1.0:
                    # Adjust cursor position for zoomed view
                    cx = int((pos_x - x1 * SCREEN_W / w) * 960 / (new_w * SCREEN_W / w))
                    cy = int((pos_y - y1 * SCREEN_H / h) * 540 / (new_h * SCREEN_H / h))
                else:
                    cx = int(pos_x * scale_x)
                    cy = int(pos_y * scale_y)
                
                # Only draw cursor if it's within bounds
                if 0 <= cx < 960 and 0 <= cy < 540:
                    cv2.circle(frame, (cx, cy), 12, (74, 158, 255), 2)
                    cv2.circle(frame, (cx, cy), 2, (74, 158, 255), -1)

                    # Click highlight
                    if time.time() - last_click_time < 0.3:
                        cv2.circle(frame, (cx, cy), 30, (0, 255, 0), 3)

                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 30])
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                time.sleep(0.04)  # ~25 FPS
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

# --- ACTION HANDLER ---
def mark_click():
    global last_click_time
    last_click_time = time.time()

def zoom_in():
    global zoom_factor, zoom_center_x, zoom_center_y
    zoom_center_x, zoom_center_y = pyautogui.position()
    zoom_factor = min(zoom_factor + 0.25, 4.0)

def zoom_out():
    global zoom_factor
    zoom_factor = max(zoom_factor - 0.25, 1.0)

def zoom_reset():
    global zoom_factor
    zoom_factor = 1.0

def set_volume(val):
    if audio_available and volume:
        try:
            volume.SetMasterVolumeLevelScalar(float(val) / 100, None)
        except:
            pass

def scroll_up():
    pyautogui.scroll(3)

def scroll_down():
    pyautogui.scroll(-3)

ACTIONS = {
    "click": lambda: (pyautogui.click(), mark_click()),
    "right_click": lambda: (pyautogui.rightClick(), mark_click()),
    "drag_start": lambda: pyautogui.mouseDown(),
    "drag_end": lambda: pyautogui.mouseUp(),
    "type": lambda val: pyautogui.write(val, interval=0.01),
    "move_joy": lambda x, y: pyautogui.moveRel(float(x)*2, float(y)*2, _pause=False),
    "move_abs": lambda x, y: (setattr(__import__('__main__'), 'zoom_center_x', float(x)), 
                               setattr(__import__('__main__'), 'zoom_center_y', float(y)),
                               pyautogui.moveTo(float(x), float(y), _pause=False)),
    "zoom_in": zoom_in,
    "zoom_out": zoom_out,
    "zoom_reset": zoom_reset,
    "volume": set_volume,
    "scroll_up": scroll_up,
    "scroll_down": scroll_down,
}

@app.route('/action')
def action():
    if not session.get('auth'):
        return "Unauthorized", 401
    t = request.args.get('type')
    if t in ACTIONS:
        if t == "type":
            ACTIONS[t](request.args.get('val', ''))
        elif t in ["move_joy", "move_abs"]:
            ACTIONS[t](request.args.get('x', 0), request.args.get('y', 0))
        elif t == "volume":
            ACTIONS[t](request.args.get('val', 50))
        else:
            ACTIONS[t]()
    return "OK"

# --- MAIN ---
if __name__ == '__main__':
    print("=" * 50)
    print("🖥️  Enhanced Remote Desktop Server")
    print("=" * 50)
    print(f"🌐 Access at: http://0.0.0.0:5000")
    print(f"🔒 Default password: 1234")
    print(f"📱 Screen size: {SCREEN_W}x{SCREEN_H}")
    print(f"🔊 Audio control: {'Enabled' if audio_available else 'Disabled (install pycaw)'}")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=False)
