; AutoHotkey Script for Remote Desktop Control
; Handles mouse movement, clicks, and audio volume control
#Persistent
#SingleInstance Force
#NoEnv
SetWorkingDir %A_ScriptDir%

; === MOUSE CONTROL FUNCTIONS ===

; Move mouse relatively (smooth movement)
MoveMouseRel(x, y)
{
    MouseMove, %x%, %y%, 0, R
}

; Move mouse to absolute position
MoveMouseAbs(x, y)
{
    MouseMove, %x%, %y%, 0
}

; Left Click
LeftClick()
{
    Click
}

; Right Click
RightClick()
{
    Click, Right
}

; Mouse Down (for dragging)
MouseDown()
{
    Click, Down
}

; Mouse Up (end dragging)
MouseUp()
{
    Click, Up
}

; Scroll Up
ScrollUp(amount := 3)
{
    Click, WheelUp, %amount%
}

; Scroll Down
ScrollDown(amount := 3)
{
    Click, WheelDown, %amount%
}

; === AUDIO CONTROL ===

; Set Volume (0-100)
SetVolume(vol)
{
    SoundSet, %vol%
}

; Get Current Volume
GetVolume()
{
    SoundGet, vol
    return vol
}

; Volume Up
VolumeUp(amount := 5)
{
    SoundSet, +%amount%
    SoundGet, vol
    ToolTip, 🔊 Volume: %vol%`%
    SetTimer, RemoveToolTip, -800
}

; Volume Down
VolumeDown(amount := 5)
{
    SoundSet, -%amount%
    SoundGet, vol
    ToolTip, 🔉 Volume: %vol%`%
    SetTimer, RemoveToolTip, -800
}

RemoveToolTip:
    ToolTip
    return

; === HOTKEYS (Optional - Right Click + Scroll for volume) ===
; Uncomment these if you want local hotkey control

; WheelUp::
;     if GetKeyState("RButton", "P")
;     {
;         VolumeUp(5)
;     }
;     else
;     {
;         Send, {WheelUp}
;     }
;     return

; WheelDown::
;     if GetKeyState("RButton", "P")
;     {
;         VolumeDown(5)
;     }
;     else
;     {
;         Send, {WheelDown}
;     }
;     return

; Exit script
+Esc::ExitApp

; === COMMAND LISTENER ===
; Listen for commands from Python via temp file
SetTimer, CheckCommands, 50
return

CheckCommands:
    if FileExist("ahk_command.tmp")
    {
        FileRead, command, ahk_command.tmp
        FileDelete, ahk_command.tmp
        
        ; Parse command
        parts := StrSplit(command, "|")
        action := parts[1]
        
        if (action = "move_rel")
        {
            x := parts[2]
            y := parts[3]
            MoveMouseRel(x, y)
        }
        else if (action = "move_abs")
        {
            x := parts[2]
            y := parts[3]
            MoveMouseAbs(x, y)
        }
        else if (action = "click")
        {
            LeftClick()
        }
        else if (action = "right_click")
        {
            RightClick()
        }
        else if (action = "mouse_down")
        {
            MouseDown()
        }
        else if (action = "mouse_up")
        {
            MouseUp()
        }
        else if (action = "scroll_up")
        {
            amount := parts[2] ? parts[2] : 3
            ScrollUp(amount)
        }
        else if (action = "scroll_down")
        {
            amount := parts[2] ? parts[2] : 3
            ScrollDown(amount)
        }
        else if (action = "set_volume")
        {
            vol := parts[2]
            SetVolume(vol)
        }
        else if (action = "volume_up")
        {
            amount := parts[2] ? parts[2] : 5
            VolumeUp(amount)
        }
        else if (action = "volume_down")
        {
            amount := parts[2] ? parts[2] : 5
            VolumeDown(amount)
        }
        else if (action = "get_volume")
        {
            vol := GetVolume()
            FileAppend, %vol%, ahk_response.tmp
        }
        else if (action = "exit")
        {
            ExitApp
        }
    }
    return
