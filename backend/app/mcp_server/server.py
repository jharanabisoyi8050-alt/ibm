"""MCP Server - Custom Model Context Protocol server (JSON-RPC 2.0)
Exposes road safety tools: traffic, weather, geo, ambulance.
"""
import asyncio
import json
import logging
from typing import Any
from aiohttp import web

from app.mcp_server.tools.traffic_mcp import TrafficMCPTools
from app.mcp_server.tools.weather_mcp import WeatherMCPTools
from app.mcp_server.tools.geo_mcp import GeoMCPTools
from app.mcp_server.tools.ambulance_mcp import AmbulanceMCPTools
from app.config import settings

logger = logging.getLogger(__name__)


class MCPServer:
    """
    Custom MCP server implementing JSON-RPC 2.0 for road safety tools.
    Register in IBM Bob via .bob/mcp_config.yaml.
    """

    def __init__(self):
        self.traffic_tools = TrafficMCPTools()
        self.weather_tools = WeatherMCPTools()
        self.geo_tools = GeoMCPTools()
        self.ambulance_tools = AmbulanceMCPTools()
        self.tool_registry = self._build_registry()

    def _build_registry(self) -> dict:
        return {
            # Traffic tools
            "get_traffic_density": self.traffic_tools.get_traffic_density,
            "get_congestion_level": self.traffic_tools.get_congestion_level,
            "get_vehicle_count": self.traffic_tools.get_vehicle_count,
            # Weather tools
            "get_current_weather": self.weather_tools.get_current_weather,
            "get_weather_forecast": self.weather_tools.get_weather_forecast,
            "get_weather_risk": self.weather_tools.get_weather_risk,
            # Geo tools
            "geocode_address": self.geo_tools.geocode_address,
            "get_route": self.geo_tools.get_route,
            "calculate_distance": self.geo_tools.calculate_distance,
            "get_nearby_hospitals": self.geo_tools.get_nearby_hospitals,
            # Ambulance tools
            "get_available_ambulances": self.ambulance_tools.get_available_ambulances,
            "get_ambulance_location": self.ambulance_tools.get_ambulance_location,
            "dispatch_ambulance": self.ambulance_tools.dispatch_ambulance,
        }

    async def handle_jsonrpc(self, request: web.Request) -> web.Response:
        """Handle JSON-RPC 2.0 requests."""
        try:
            body = await request.json()
        except Exception:
            return self._error_response(None, -32700, "Parse error")

        method = body.get("method")
        params = body.get("params", {})
        req_id = body.get("id")

        if method == "tools/list":
            return self._success_response(req_id, self._list_tools())

        if method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            if tool_name not in self.tool_registry:
                return self._error_response(req_id, -32601, f"Tool not found: {tool_name}")
            try:
                result = await self.tool_registry[tool_name](**tool_args)
                return self._success_response(req_id, result)
            except Exception as e:
                logger.exception(f"Tool execution failed: {tool_name}")
                return self._error_response(req_id, -32603, str(e))

        return self._error_response(req_id, -32601, f"Method not found: {method}")

    def _list_tools(self) -> dict:
        return {
            "tools": [
                {"name": name, "description": f"Road safety tool: {name}"}
                for name in self.tool_registry
            ]
        }

    def _success_response(self, req_id: Any, result: Any) -> web.Response:
        return web.json_response({"jsonrpc": "2.0", "id": req_id, "result": result})

    def _error_response(self, req_id: Any, code: int, message: str) -> web.Response:
        return web.json_response({
            "jsonrpc": "2.0", "id": req_id,
            "error": {"code": code, "message": message},
        })


async def main():
    server = MCPServer()
    app = web.Application()
    app.router.add_post("/mcp", server.handle_jsonrpc)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, settings.MCP_SERVER_HOST, settings.MCP_SERVER_PORT)
    await site.start()
    logger.info(f"MCP Server running at http://{settings.MCP_SERVER_HOST}:{settings.MCP_SERVER_PORT}/mcp")
    await asyncio.Event().wait()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
