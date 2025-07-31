#!/usr/bin/env python3
"""
Gemini 2.0 Screen Sharing Demo

Real-time screen sharing with Gemini 2.0 Flash model for AI-powered screen analysis.
Supports audio input, screen capture, and live AI responses.

Dependencies:
    - google-genai==0.3.0
    - websockets
    - urllib3

Author: YouTube Demo Project
"""

import asyncio
import json
import os
import websockets
import base64
import ssl
import urllib3
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Disable SSL warnings and verification
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration from environment variables
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
MODEL = os.getenv('MODEL', "gemini-2.0-flash-exp")
WEBSOCKET_HOST = os.getenv('WEBSOCKET_HOST', "localhost")
WEBSOCKET_PORT = int(os.getenv('WEBSOCKET_PORT', 9083))

# Validate required environment variables
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables. Please check your .env file.")

# Set API key for Google client
os.environ['GOOGLE_API_KEY'] = GOOGLE_API_KEY

# SSL workaround for macOS certificate issues
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['SSL_VERIFY'] = 'false'
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''

# Aggressive SSL bypass
import ssl
old_create_default_context = ssl.create_default_context
def create_unverified_context(*args, **kwargs):
    context = old_create_default_context(*args, **kwargs)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return context
ssl.create_default_context = create_unverified_context
ssl._create_default_https_context = ssl._create_unverified_context

# Import genai after SSL patches
from google import genai

client = genai.Client(
  http_options={
    'api_version': 'v1alpha',
  }
)

def load_gems_context():
    """Load the GEMS context configuration from JSON file."""
    context_file = Path(__file__).parent / "gems_context.json"
    try:
        with open(context_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: Context file {context_file} not found. Using default context.")
        return None
    except json.JSONDecodeError as e:
        print(f"Warning: Invalid JSON in context file: {e}. Using default context.")
        return None

def find_page_context(gems_context, current_screen):
    """Find the appropriate page context based on the current screen URL."""
    if not gems_context or not current_screen:
        return None
    
    # Remove leading slash for comparison
    screen_path = current_screen.lstrip('/')
    
    # Search through all pages in the context
    for category, pages in gems_context.get("pages", {}).items():
        for page_key, page_data in pages.items():
            page_url = page_data.get("url", "").lstrip('/')
            
            # Direct match
            if page_url == screen_path:
                return page_data
            
            # Parameter-based match (e.g., /profile/:memberGUID matches /profile/123)
            if ':' in page_url:
                url_parts = page_url.split('/')
                screen_parts = screen_path.split('/')
                
                if len(url_parts) == len(screen_parts):
                    match = True
                    for url_part, screen_part in zip(url_parts, screen_parts):
                        if not url_part.startswith(':') and url_part != screen_part:
                            match = False
                            break
                    if match:
                        return page_data
    
    return None

def build_system_instruction(gems_context, current_screen):
    """Build a dynamic system instruction based on the current screen context."""
    
    # Default instruction
    default_instruction = """You are a helpful AI assistant for screen sharing sessions. Your role is to:
1) Analyze and describe the content being shared on screen
2) Answer questions about the shared content
3) Provide relevant information and context about what's being shown
4) Assist with technical issues related to screen sharing
5) Maintain a professional and helpful tone. Focus on being concise and clear in your responses."""
    
    if not gems_context:
        return default_instruction
    
    # Get application info
    app_info = gems_context.get("application", {})
    app_name = app_info.get("name", "Application")
    app_description = app_info.get("description", "")
    
    # Find specific page context
    page_context = find_page_context(gems_context, current_screen)
    
    if page_context:
        # Build context-specific instruction
        page_title = page_context.get("title", "Page")
        page_description = page_context.get("description", "")
        actions = page_context.get("actions", [])
        components = page_context.get("components", [])
        
        instruction = f"""You are an AI assistant helping with the {app_name} member portal screen sharing session.

CURRENT SCREEN CONTEXT:
- Page: {page_title}
- URL: {current_screen}
- Description: {page_description}

APPLICATION CONTEXT:
{app_description}

SCREEN-SPECIFIC GUIDANCE:
1) Focus on helping users understand and navigate the {page_title} page
2) Explain the available actions: {', '.join(actions) if actions else 'various page functions'}
3) Help identify and interact with page components: {', '.join(components) if components else 'page elements'}
4) Provide context-aware assistance for medical scheme member portal tasks
5) Answer questions about the specific page functionality and workflow

GENERAL ASSISTANCE:
- Analyze what's visible on the screen
- Guide users through page-specific tasks
- Explain GEMS member portal features and benefits
- Help with navigation and form completion
- Maintain a helpful, professional tone focused on member services

Pay special attention to member information, medical benefits, claims, and healthcare-related content."""
        
        return instruction
    else:
        # General application context when specific page not found
        instruction = f"""You are an AI assistant helping with the {app_name} screen sharing session.

APPLICATION CONTEXT:
{app_description}

CURRENT SCREEN: {current_screen}
Note: This appears to be a page that's not in our specific context database. Provide general assistance.

YOUR ROLE:
1) Analyze the GEMS member portal screen content being shared
2) Help users navigate and understand medical scheme features
3) Assist with member benefits, claims, profile management, and healthcare services
4) Explain portal functionality and guide users through tasks
5) Focus on healthcare and medical scheme member services
6) Maintain a professional, helpful tone appropriate for medical services

Pay special attention to:
- Member profile and account information
- Medical benefits and coverage details
- Claims and authorizations
- Healthcare provider information
- Dependant management
- Digital services and cards"""
        
        return instruction

# Load context at startup
GEMS_CONTEXT = load_gems_context()

def create_context_detection_prompt(gems_context):
    """Create a prompt for automatic context detection from screen images."""
    if not gems_context:
        return "Analyze this screen image and identify what type of application or page is being shown."
    
    # Build a detection prompt with all available contexts
    app_name = gems_context.get("application", {}).get("name", "GEMS Member Portal")
    
    # Get all page contexts for detection
    detection_options = []
    for category, pages in gems_context.get("pages", {}).items():
        for page_key, page_data in pages.items():
            url = page_data.get("url", "")
            title = page_data.get("title", "")
            description = page_data.get("description", "")
            if url and title:
                detection_options.append(f"- {url}: {title} - {description}")
    
    prompt = f"""You are analyzing a screen image from the {app_name}. 

TASK: Identify which specific page/screen is currently being displayed.

AVAILABLE PAGES TO DETECT:
{chr(10).join(detection_options[:20])}  # Limit to first 20 for prompt size

INSTRUCTIONS:
1. Look for URL patterns, page titles, headings, navigation elements, and distinctive UI components
2. Identify specific text, buttons, forms, or layouts that indicate which page this is
3. If you can identify the specific page, respond ONLY with the URL path (e.g., "/dependants", "/claims", "/profile/123")
4. If you cannot identify a specific page but recognize it as GEMS portal, respond with "GEMS_GENERAL"
5. If this is not a GEMS portal page at all, respond with "UNKNOWN"

RESPOND WITH ONLY THE URL PATH OR STATUS CODE - NO OTHER TEXT."""

    return prompt

async def detect_screen_context(image_data, gems_context):
    """Detect the current screen context from a base64 image."""
    try:
        # Create a simple detection prompt
        detection_prompt = create_context_detection_prompt(gems_context)
        
        # Create a minimal config for context detection
        detection_config = {
            "generation_config": {
                "response_modalities": ["TEXT"],
                "max_output_tokens": 50
            },
            "system_instruction": detection_prompt
        }
        
        # Use Gemini to analyze the image and detect context
        async with client.aio.live.connect(model=MODEL, config=detection_config) as detection_session:
            # Send the image for analysis
            await detection_session.send({
                "mime_type": "image/jpeg", 
                "data": image_data
            })
            
            # Get the response
            async for response in detection_session.receive():
                if response.server_content and response.server_content.model_turn:
                    for part in response.server_content.model_turn.parts:
                        if hasattr(part, 'text') and part.text:
                            detected_url = part.text.strip()
                            print(f"🔍 Context detection result: {detected_url}")
                            
                            # Find the corresponding page context
                            if detected_url.startswith('/'):
                                page_context = find_page_context(gems_context, detected_url)
                                if page_context:
                                    return detected_url, page_context
                            
                            # Handle special responses
                            if detected_url == "GEMS_GENERAL":
                                return "GEMS_GENERAL", None
                            elif detected_url == "UNKNOWN":
                                return None, None
                            
                            return None, None
                        
                if response.server_content.turn_complete:
                    break
                    
    except Exception as e:
        print(f"Error in context detection: {e}")
        return None, None
    
    return None, None

# Track current context state
current_context_state = {
    "url": None,
    "page_context": None,
    "last_detection": None
}

async def gemini_session_handler(client_websocket):
    """Handles the interaction with Gemini API within a websocket session.

    Args:
        client_websocket: The websocket connection to the client.
    """
    try:
        print(f"New client connected: {client_websocket.remote_address}")
        config_message = await client_websocket.recv()
        print(f"Received config: {config_message}")
        config_data = json.loads(config_message)
        config = config_data.get("setup", {})
        
        # Check if automatic context detection is enabled
        auto_detect = config_data.get("auto_detect_context", False)
        
        if auto_detect:
            print("🎯 Automatic context detection enabled")
            # Start with default instruction, will be updated when screen is analyzed
            system_instruction = build_system_instruction(GEMS_CONTEXT, None)
        else:
            # Fallback to manual context if provided
            current_screen = config_data.get("current_screen", "")
            print(f"Manual context provided: {current_screen}")
            system_instruction = build_system_instruction(GEMS_CONTEXT, current_screen)
        
        config["system_instruction"] = system_instruction
        print("🚀 Starting session with initial context")     

        print("Attempting to connect to Gemini API...")
        try:
            async with client.aio.live.connect(model=MODEL, config=config) as session:
                print("Connected to Gemini API")

                async def send_to_gemini():
                    """Sends messages from the client websocket to the Gemini API."""
                    try:
                        print("Starting send_to_gemini loop...")
                        async for message in client_websocket:
                            print(f"Received message from client: {message[:100]}...")  # Log first 100 chars
                            try:
                                data = json.loads(message)
                                
                                # Handle context updates
                                if data.get("type") == "context_update":
                                    new_screen = data.get("current_screen", "")
                                    print(f"🔄 Context update received: {new_screen}")
                                    
                                    # Build new system instruction
                                    new_instruction = build_system_instruction(GEMS_CONTEXT, new_screen)
                                    
                                    # Send context update to Gemini (if supported)
                                    # Note: This may require re-establishing the session depending on API capabilities
                                    print(f"✅ Updated context for: {new_screen}")
                                    if GEMS_CONTEXT:
                                        page_context = find_page_context(GEMS_CONTEXT, new_screen)
                                        if page_context:
                                            print(f"📄 Now using context: {page_context.get('title', 'Unknown')}")
                                    continue
                                
                                # Handle regular realtime input
                                if "realtime_input" in data:
                                    for chunk in data["realtime_input"]["media_chunks"]:
                                        if chunk["mime_type"] == "audio/pcm":
                                            print("Sending audio chunk to Gemini")
                                            await session.send({"mime_type": "audio/pcm", "data": chunk["data"]})
                                        elif chunk["mime_type"] == "image/jpeg":
                                            print("📸 Processing screen image...")
                                            
                                            # Perform automatic context detection on first few images
                                            if auto_detect and (current_context_state["last_detection"] is None or 
                                                              (current_context_state["last_detection"] and 
                                                               len(current_context_state["last_detection"]) < 3)):
                                                
                                                print("🔍 Attempting context detection...")
                                                detected_url, page_context = await detect_screen_context(chunk["data"], GEMS_CONTEXT)
                                                
                                                if detected_url and detected_url != current_context_state["url"]:
                                                    # Context changed or detected for first time
                                                    current_context_state["url"] = detected_url
                                                    current_context_state["page_context"] = page_context
                                                    current_context_state["last_detection"] = detected_url
                                                    
                                                    print(f"✅ Context detected: {detected_url}")
                                                    if page_context:
                                                        print(f"📄 Page: {page_context.get('title', 'Unknown')}")
                                                    
                                                    # Send context update to client
                                                    context_update = {
                                                        "type": "context_detected",
                                                        "context": {
                                                            "url": detected_url,
                                                            "title": page_context.get("title", "GEMS Portal") if page_context else "GEMS Portal",
                                                            "description": page_context.get("description", "") if page_context else ""
                                                        }
                                                    }
                                                    await client_websocket.send(json.dumps(context_update))
                                                    
                                                    # Update system instruction for this session
                                                    # Note: This would require session restart in current API
                                                    print("🔄 Context updated for current session")
                                            
                                            print("Sending image chunk to Gemini")
                                            await session.send({"mime_type": "image/jpeg", "data": chunk["data"]})
                            except Exception as e:
                                print(f"Error processing message: {e}")
                        print("Client WebSocket closed, ending send loop")
                    except websockets.exceptions.ConnectionClosed:
                        print("Client disconnected during send")
                    except Exception as e:
                        print(f"Error in send_to_gemini: {e}")
                    finally:
                        print("send_to_gemini completed")



                async def receive_from_gemini():
                    """Receives responses from the Gemini API and forwards them to the client."""
                    try:
                        print("Starting receive_from_gemini loop...")
                        async for response in session.receive():
                            print("Received response from Gemini")
                            if response.server_content is None:
                                print(f'Unhandled server message! - {response}')
                                continue

                            model_turn = response.server_content.model_turn
                            if model_turn:
                                for part in model_turn.parts:
                                    if hasattr(part, 'text') and part.text is not None:
                                        print(f"Sending text to client: {part.text[:50]}...")
                                        await client_websocket.send(json.dumps({"text": part.text}))
                                    elif hasattr(part, 'inline_data') and part.inline_data is not None:
                                        print(f"Sending audio to client, mime_type: {part.inline_data.mime_type}")
                                        base64_audio = base64.b64encode(part.inline_data.data).decode('utf-8')
                                        await client_websocket.send(json.dumps({"audio": base64_audio}))

                            if response.server_content.turn_complete:
                                print('Turn complete')
                                
                        print("Gemini session ended")
                    except websockets.exceptions.ConnectionClosed:
                        print("Client connection closed during receive")
                    except Exception as e:
                        print(f"Error in receive_from_gemini: {e}")
                    finally:
                        print("receive_from_gemini completed")


                # Start send loop
                send_task = asyncio.create_task(send_to_gemini())
                # Launch receive loop as a background task
                receive_task = asyncio.create_task(receive_from_gemini())
                
                print("Started send and receive tasks, waiting for completion...")
                
                # Wait for tasks to complete
                try:
                    await asyncio.gather(send_task, receive_task)
                except Exception as e:
                    print(f"Task error: {e}")
                    # Cancel remaining tasks
                    send_task.cancel()
                    receive_task.cancel()
        
        except Exception as gemini_error:
            print(f"Failed to connect to Gemini API: {gemini_error}")
            # Keep WebSocket alive and send error message
            await client_websocket.send(json.dumps({"error": f"Gemini API unavailable: {str(gemini_error)}"}))
            
            # Handle basic WebSocket messages without Gemini
            try:
                async for message in client_websocket:
                    print(f"Received message (Gemini offline): {message}")
                    await client_websocket.send(json.dumps({"text": "Screen sharing server running, but Gemini API is unavailable."}))
            except websockets.exceptions.ConnectionClosed:
                print("Client disconnected")

    except Exception as e:
        print(f"Error in Gemini session: {e}")
        import traceback
        traceback.print_exc()
        try:
            await client_websocket.send(json.dumps({"error": f"Server error: {str(e)}"}))
        except:
            pass
    finally:
        print("Gemini session closed.")


async def main() -> None:
    """Start the WebSocket server."""
    print(f"Starting WebSocket server on {WEBSOCKET_HOST}:{WEBSOCKET_PORT}...")
    try:
        async with websockets.serve(gemini_session_handler, WEBSOCKET_HOST, WEBSOCKET_PORT):
            print(f"✅ Server running on ws://{WEBSOCKET_HOST}:{WEBSOCKET_PORT}")
            print("🖥️  Ready for screen sharing connections!")
            print("📱 Open index.html in your browser to start")
            await asyncio.Future()  # Keep the server running indefinitely
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())