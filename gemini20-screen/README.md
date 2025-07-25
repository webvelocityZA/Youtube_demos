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
   pip install google-genai==0.3.0 websockets urllib3
   ```

3. **Configure API Key**
   - Edit `main.py` and replace `GOOGLE_API_KEY` with your actual Google AI API key
   - Or set as environment variable: `export GOOGLE_API_KEY="your-api-key-here"`

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
4. Click the microphone button to start voice interaction
5. Start talking about what's on your screen!

## 🏗️ Project Structure

```
gemini20-screen/
├── README.md              # This file
├── main.py               # WebSocket server with Gemini integration
├── index.html            # Web interface for screen sharing
├── pcm-processor.js      # Audio worklet for real-time audio processing
└── requirements.txt      # Python dependencies (optional)
```

## 🔧 Configuration

### API Settings
Edit these constants in `main.py`:
```python
GOOGLE_API_KEY = 'your-api-key-here'  # Your Google AI API key
MODEL = "gemini-2.0-flash-exp"        # Gemini model to use
WEBSOCKET_HOST = "localhost"          # Server host
WEBSOCKET_PORT = 9083                 # Server port
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
2. **Image Processing**: Screen frames are converted to base64 JPEG images every 3 seconds
3. **Audio Capture**: Microphone input is processed to PCM format at 16kHz
4. **WebSocket Communication**: Audio and image data sent to Python server
5. **Gemini Processing**: Server forwards data to Gemini 2.0 Flash model
6. **AI Response**: Gemini analyzes screen content and provides audio responses
7. **Audio Playback**: AI responses played back through Web Audio API

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

- **API Key**: Never commit your actual API key to version control
- **SSL Bypass**: Current SSL bypass is for development only
- **Local Development**: This demo is designed for localhost development
- **HTTPS Required**: Production deployment requires HTTPS for WebRTC APIs

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