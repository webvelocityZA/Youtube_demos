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
        
        # Use simple default system instruction
        system_instruction = """You are a helpful AI assistant for screen sharing sessions. Your role is to:
1) Analyze and describe the content being shared on screen
2) Answer questions about the shared content
3) Provide relevant information and context about what's being shown
4) Assist with technical issues related to screen sharing
5) Maintain a professional and helpful tone. Focus on being concise and clear in your responses."""
        
        config["system_instruction"] = system_instruction
        print("🚀 Starting session")     

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
                                
                                # Handle regular realtime input
                                if "realtime_input" in data:
                                    for chunk in data["realtime_input"]["media_chunks"]:
                                        if chunk["mime_type"] == "audio/pcm":
                                            print("Sending audio chunk to Gemini")
                                            await session.send({"mime_type": "audio/pcm", "data": chunk["data"]})
                                        elif chunk["mime_type"] == "image/jpeg":
                                            print("📸 Processing screen image...")
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