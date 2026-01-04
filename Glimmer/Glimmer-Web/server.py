"""
GLIMMER Web API Server

Provides REST API endpoints for the Vue frontend to interact with GLIMMER Agent.
"""

import json
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any, Optional
import traceback

# Add parent directory to path
sys.path.insert(0, ".")

from core import GlimmerAgent, AgentConfig
from core.model.client import ModelConfig
from core.desktop.screenshot import get_screenshot


class GlimmerAPIHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler for GLIMMER API."""
    
    agent: Optional[GlimmerAgent] = None
    current_goal: str = ""
    
    def _set_headers(self, status_code: int = 200, content_type: str = "application/json"):
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def _send_json(self, data: dict[str, Any], status_code: int = 200):
        self._set_headers(status_code)
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
    
    def _read_body(self) -> dict[str, Any]:
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        body = self.rfile.read(content_length)
        return json.loads(body.decode("utf-8"))
    
    def do_OPTIONS(self):
        self._set_headers()
    
    def do_GET(self):
        if self.path == "/api/health":
            self._send_json({"status": "ok", "agent_ready": GlimmerAPIHandler.agent is not None})
        
        elif self.path == "/api/screenshot":
            try:
                screenshot = get_screenshot()
                self._send_json({
                    "success": True,
                    "screenshot": screenshot.base64_data,
                    "width": screenshot.width,
                    "height": screenshot.height,
                })
            except Exception as e:
                self._send_json({"success": False, "error": str(e)}, 500)
        
        else:
            self._send_json({"error": "Not found"}, 404)
    
    def do_POST(self):
        if self.path == "/api/execute":
            self._handle_execute()
        elif self.path == "/api/reset":
            self._handle_reset()
        elif self.path == "/api/config":
            self._handle_config()
        else:
            self._send_json({"error": "Not found"}, 404)
    
    def _handle_execute(self):
        """Execute a step with the agent."""
        try:
            data = self._read_body()
            goal = data.get("goal", "")
            
            if not goal and not GlimmerAPIHandler.current_goal:
                self._send_json({"success": False, "error": "No goal provided"}, 400)
                return
            
            if goal:
                GlimmerAPIHandler.current_goal = goal
            
            if GlimmerAPIHandler.agent is None:
                model_config = ModelConfig(
                    base_url=data.get("model_url", "http://localhost:8000/v1"),
                    model_name=data.get("model_name", "glm-4v"),
                )
                agent_config = AgentConfig(verbose=False)
                GlimmerAPIHandler.agent = GlimmerAgent(model_config, agent_config)
            
            result = GlimmerAPIHandler.agent.step(GlimmerAPIHandler.current_goal)
            
            # Get screenshot after action
            try:
                screenshot = get_screenshot()
                screenshot_data = screenshot.base64_data
            except:
                screenshot_data = None
            
            # Build response in GLIMMER format (Agent.md)
            response = {
                "ui_thought": result.thought,
                "ui_focus_box": None,  # TODO: Parse from result.params
                "status": "DONE" if result.finished else "WORKING",
                "operation": {
                    "action": result.action_type.lower(),
                    "params": result.params,
                } if not result.finished else None,
                "screenshot": screenshot_data,
                "confidence": result.confidence,
                "message": result.message,
            }
            
            # Extract focus box from params if available
            if "box_2d" in result.params:
                box = result.params["box_2d"]
                if len(box) == 4:
                    response["ui_focus_box"] = [box[1], box[0], box[3], box[2]]  # Convert to [y1,x1,y2,x2]
            
            self._send_json(response)
            
        except Exception as e:
            traceback.print_exc()
            self._send_json({
                "ui_thought": f"Error: {str(e)}",
                "ui_focus_box": None,
                "status": "FAIL",
                "error_message": str(e),
                "operation": None,
            }, 500)
    
    def _handle_reset(self):
        """Reset the agent state."""
        if GlimmerAPIHandler.agent:
            GlimmerAPIHandler.agent.reset()
        GlimmerAPIHandler.current_goal = ""
        self._send_json({"success": True})
    
    def _handle_config(self):
        """Update agent configuration."""
        try:
            data = self._read_body()
            model_config = ModelConfig(
                base_url=data.get("model_url", "http://localhost:8000/v1"),
                model_name=data.get("model_name", "glm-4v"),
                api_key=data.get("api_key", "EMPTY"),
            )
            agent_config = AgentConfig(
                lang=data.get("lang", "en"),
                verbose=False,
            )
            GlimmerAPIHandler.agent = GlimmerAgent(model_config, agent_config)
            self._send_json({"success": True})
        except Exception as e:
            self._send_json({"success": False, "error": str(e)}, 500)


def run_server(host: str = "localhost", port: int = 5000):
    """Run the API server."""
    server_address = (host, port)
    httpd = HTTPServer(server_address, GlimmerAPIHandler)
    print(f"🚀 GLIMMER API Server running at http://{host}:{port}")
    print(f"📡 Endpoints:")
    print(f"   GET  /api/health      - Check server status")
    print(f"   GET  /api/screenshot  - Get current screenshot")
    print(f"   POST /api/execute     - Execute agent step")
    print(f"   POST /api/reset       - Reset agent state")
    print(f"   POST /api/config      - Update configuration")
    httpd.serve_forever()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="GLIMMER Web API Server")
    parser.add_argument("--host", default="localhost", help="Host to bind")
    parser.add_argument("--port", type=int, default=5000, help="Port to bind")
    args = parser.parse_args()
    run_server(args.host, args.port)
