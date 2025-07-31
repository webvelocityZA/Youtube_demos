# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a collection of YouTube demo implementations covering AI/ML applications, multi-agent systems, and web interfaces. Each directory represents a complete tutorial project with corresponding YouTube videos.

## Project Types & Technologies

### Python Projects
Most Python scripts are standalone demonstrations. Common dependencies include:
- **AI Frameworks**: AutoGen, CrewAI, Swarm, AgentKit, Instructor
- **ML Libraries**: torch, transformers, accelerate 
- **UI Frameworks**: Panel, Streamlit, Mesop, Taipy
- **APIs**: OpenAI, Gemini, Fireworks, OpenRouter, Groq

### React/TypeScript Projects
- **AutoGen_API/react_mini_app/**: Standard React app with Create React App
- **Frontend projects**: Vite + TypeScript + Tailwind CSS + Radix UI components

### Android Projects
- **gemini20-android*/**: Kotlin Android apps using Gradle build system
- Use standard Android Jetpack Compose for UI

### Chrome Extension
- **GeminiChrome/**: Manifest V3 Chrome extension with background scripts and content scripts

## Common Development Commands

### Python Projects
```bash
# Install dependencies
pip install -r requirements.txt

# Run most Python demos
python main.py
# or
python <script_name>.py
```

### React Projects
```bash
# Install dependencies
npm install

# Development server
npm start  # or npm run dev for Vite projects

# Build for production
npm run build

# Run tests
npm test

# Lint code
npm run lint
```

### Android Projects
```bash
# Build the project
./gradlew build

# Run on device/emulator
./gradlew installDebug
```

## Architecture Patterns

### Multi-Agent Systems
- **AutoGen**: Uses conversable agents with different roles and capabilities
- **CrewAI**: Task-based workflow with agents having specific tools and roles  
- **Swarm**: OpenAI's experimental multi-agent framework with handoffs
- **AgentKit**: Lightweight framework for agent orchestration

### Web UI Integration
- Most AI demos include web interfaces using Panel, Streamlit, or custom React frontends
- WebSocket connections for real-time communication with AI models
- Panel is commonly used for rapid prototyping of agent interfaces

### Multimodal Applications
- Integration of text, voice, and vision capabilities
- Real-time audio processing with WebRTC
- Screen sharing and camera access for interactive applications
- Local model deployment with transformers and torch

### API Integration Patterns
- Multiple LLM providers supported (OpenAI, Gemini, Fireworks, etc.)
- Environment variable configuration for API keys
- Streaming responses for real-time interactions

## Key Files to Check

- `requirements.txt` for Python dependencies
- `package.json` for Node.js projects  
- `manifest.json` for Chrome extensions
- `build.gradle.kts` for Android projects
- Individual README files in project directories for specific instructions

## Development Notes

- Each project directory is self-contained with its own dependencies
- Most projects are educational demos rather than production applications
- API keys and sensitive data should be handled via environment variables
- Many projects include both backend Python services and frontend web applications