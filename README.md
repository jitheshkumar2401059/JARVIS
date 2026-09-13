# JARVIS

A personal AI voice assistant inspired by JARVIS, built with Python, Gemini, and LiveKit.

## Features

- 🎤 Real-time voice interaction
- 🧠 Gemini-powered AI
- 🔊 Natural voice responses
- 🌦️ Weather information
- 📍 Location resolution and saved locations
- 🌐 Web search for current information

## Architecture

```text
User Voice
    ↓
LiveKit
    ↓
Gemini Realtime
    ↓
JARVIS Agent
    ↓
Python Tools
    ├── Weather
    ├── Location
    └── Web Search
    ↓
External APIs / Data
    ↓
JARVIS Voice Response
