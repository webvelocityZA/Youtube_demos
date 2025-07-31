# Gemini 2.0 Screen Sharing Demo

A real-time screen sharing application powered by Google's Gemini 2.0 Flash model that provides AI-powered analysis of shared screen content with audio responses.

## 🌟 Features

- **Real-time Screen Capture**: Share your screen with AI-powered analysis
- **Voice Interaction**: Talk to Gemini about what's on your screen
- **Audio Responses**: Get spoken responses from Gemini
- **Live WebSocket Connection**: Real-time bidirectional communication
- **Modern Web Interface**: Clean, responsive Material Design UI

## 🚀 Demo Overview

This project demonstrates how to integrate:
- **Gemini 2.0 Flash** for multimodal AI responses
- **WebRTC Screen Capture API** for screen sharing
- **Web Audio API** for real-time audio processing
- **WebSocket** communication for live data streaming

## 📋 Prerequisites

- Python 3.11+
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Google AI API key with Gemini 2.0 access
- HTTPS or localhost for WebRTC APIs

## 🛠️ Installation

1. **Clone or download the project**
   ```bash
   cd gemini20-screen
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**
   - Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   - Edit the `.env` file and add your actual Google AI API key:
   ```bash
   # Edit the .env file
   GOOGLE_API_KEY=your-actual-api-key-here
   ```
   - Get your API key from: https://ai.google.dev/
   - **Important**: Never commit your actual API key to version control!

## 🎯 Usage

### Step 1: Start the WebSocket Server
```bash
python3 main.py
```
You should see:
```
✅ Server running on ws://localhost:9083
🖥️  Ready for screen sharing connections!
📱 Open index.html in your browser to start
```

### Step 2: Start the Web Server
In a new terminal:
```bash
python3 -m http.server 8000
```

### Step 3: Open the Application
1. Navigate to `http://localhost:8000/index.html` in your browser
2. Allow screen sharing permissions when prompted  
3. Allow microphone access when prompted
4. **Start screen sharing**: The AI will automatically detect which GEMS portal page you're viewing
5. Click the microphone button to start voice interaction
6. Ask questions - the AI will provide context-aware responses based on the detected page!

### 🎯 Automatic Context Detection

The system automatically analyzes your screen content to detect which GEMS portal page you're viewing:

**✅ Automatic Detection Examples:**
- **Dependants page detected** → AI focuses on dependant management assistance
- **Claims page detected** → AI emphasizes claim processes and status explanations  
- **Benefits page detected** → AI explains coverage details and benefit information
- **Profile page detected** → AI helps with profile updates and account management

**🔍 How It Works:**
1. **Real-time Analysis**: AI analyzes screen captures to identify page elements
2. **Context Matching**: Matches visual elements to GEMS portal page definitions
3. **Dynamic Updates**: Context updates automatically when you navigate to different pages
4. **Fallback Handling**: Uses general GEMS context if specific page cannot be detected

**💬 Context-Aware Examples:**
- "What can I do on this page?" → AI explains current page functionality
- "How do I complete this form?" → AI provides page-specific guidance
- "What are these buttons for?" → AI identifies and explains page elements

## 🏗️ Project Structure

```
gemini20-screen/
├── .env                  # Environment variables (API keys, config)
├── .env.example         # Environment variables template
├── .gitignore           # Git ignore file
├── README.md            # This file
├── main.py              # WebSocket server with dynamic context injection
├── index.html           # Web interface with context selection
├── pcm-processor.js     # Audio worklet for real-time audio processing
├── gems_context.json    # GEMS portal context definitions
└── requirements.txt     # Python dependencies
```

## 🔧 Configuration

### Environment Variables
Edit the `.env` file to configure the application:
```bash
# Required: Your Google AI API key
GOOGLE_API_KEY=your-actual-api-key-here

# Optional: Server configuration
MODEL=gemini-2.0-flash-exp
WEBSOCKET_HOST=localhost
WEBSOCKET_PORT=9083
```

### Screen Capture Settings
Modify in `index.html`:
```javascript
video: {
    width: { max: 640 },    # Screen capture width
    height: { max: 480 },   # Screen capture height
}
```

## 🎮 How It Works

1. **Screen Capture**: Browser captures screen content using `getDisplayMedia()`
2. **Context Selection**: User selects current GEMS portal page for context-aware assistance
3. **Dynamic Context Injection**: Server loads relevant context from `gems_context.json` based on selected page
4. **Image Processing**: Screen frames are converted to base64 JPEG images every 3 seconds
5. **Audio Capture**: Microphone input is processed to PCM format at 16kHz
6. **WebSocket Communication**: Audio, image data, and context updates sent to Python server
7. **Contextual AI Processing**: Server forwards data to Gemini 2.0 Flash with page-specific system instructions
8. **AI Response**: Gemini analyzes screen content with GEMS portal context and provides relevant audio responses
9. **Audio Playback**: AI responses played back through Web Audio API

## 🎯 Automatic Context Detection System

This application features an **intelligent automatic context detection system** that analyzes screen content to provide contextual AI assistance:

### Visual Context Analysis
- **Screen Content Analysis**: AI analyzes screen captures in real-time to identify current page
- **Element Recognition**: Identifies page titles, navigation, forms, and UI components
- **Pattern Matching**: Matches visual elements to GEMS portal page definitions
- **Confidence-Based Detection**: Uses multiple visual cues for accurate page identification

### Context Configuration (`gems_context.json`)
- **Comprehensive GEMS Portal Mapping**: Detailed definitions for all 50+ portal pages
- **Visual Indicators**: Page elements and patterns for automatic detection
- **Page-Specific Instructions**: Custom AI instructions dynamically applied
- **Hierarchical Context**: Organized by functional areas (auth, dashboard, profile, etc.)

### Automatic Detection Features
- **Zero User Input**: No manual selection required - completely automatic
- **Real-time Detection**: Context updates as you navigate between pages  
- **Intelligent Fallback**: Uses general GEMS context if specific page cannot be identified
- **Performance Optimized**: Context detection only on first few screen captures

### Detection Accuracy
- **High Precision**: Identifies specific pages through multiple visual cues
- **Robust Handling**: Works with different screen sizes and zoom levels
- **Adaptive Learning**: Improves detection through visual pattern recognition

## 🐛 Troubleshooting

### Common Issues

**Screen sharing not working:**
- Ensure you're accessing via `http://localhost:8000` (not file://)
- Check browser permissions for screen capture
- Try refreshing and allowing permissions again

**WebSocket connection fails:**
- Verify the Python server is running on port 9083
- Check firewall settings
- Ensure no other applications are using port 9083

**SSL Certificate errors (macOS):**
- The code includes SSL bypass for development
- For production, install proper certificates

**Audio not working:**
- Allow microphone permissions in browser
- Check browser console for audio-related errors
- Ensure `pcm-processor.js` is accessible

### Debug Mode
Enable detailed logging by checking browser console and server terminal output.

## 🔒 Security Notes

- **API Key Security**: 
  - API keys are stored in `.env` file (excluded from git)
  - Never commit your actual API key to version control
  - The `.env` file is already added to `.gitignore`
  
- **Environment Variables**:
  - Use environment variables for all sensitive configuration
  - The current `.env` contains a sample key - replace with your actual key
  
- **Development vs Production**:
  - SSL bypass is for development only
  - Production deployment requires proper HTTPS certificates
  - This demo is designed for localhost development

- **WebRTC Requirements**: 
  - Screen sharing requires HTTPS or localhost
  - Microphone access requires user permission

## 🌐 Browser Compatibility

| Browser | Screen Sharing | Web Audio | WebSocket |
|---------|---------------|-----------|-----------|
| Chrome  | ✅            | ✅        | ✅        |
| Firefox | ✅            | ✅        | ✅        |
| Safari  | ✅            | ✅        | ✅        |
| Edge    | ✅            | ✅        | ✅        |

## 📚 API References

- [Gemini API Documentation](https://ai.google.dev/docs)
- [WebRTC Screen Capture](https://developer.mozilla.org/en-US/docs/Web/API/Screen_Capture_API)
- [Web Audio API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)

## 🎬 YouTube Tutorial

This project accompanies a YouTube tutorial demonstrating the implementation process. Check the channel for the complete walkthrough!

## 📄 License

This project is for educational and demonstration purposes. Please follow Google's AI API terms of service and usage guidelines.

## 🤝 Contributing

This is a demo project! Feel free to:
- Report issues
- Suggest improvements
- Fork and experiment
- Share your modifications

---

**Happy Screen Sharing with AI! 🚀✨**