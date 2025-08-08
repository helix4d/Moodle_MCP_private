import sys
import json
from MoodleAPI import MoodleAPI

def main():
    moodle_api = MoodleAPI(domain=None, token=None)  # Will be loaded from .env

    while True:
        line = sys.stdin.readline()
        if not line:
            break

        try:
            request = json.loads(line)
            method_name = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")

            if not method_name or not hasattr(moodle_api, method_name):
                response = {
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": "Method not found"},
                    "id": request_id,
                }
            else:
                method = getattr(moodle_api, method_name)
                try:
                    result = method(**params)
                    response = {
                        "jsonrpc": "2.0",
                        "result": result,
                        "id": request_id,
                    }
                except Exception as e:
                    response = {
                        "jsonrpc": "2.0",
                        "error": {"code": -32603, "message": str(e)},
                        "id": request_id,
                    }
        except json.JSONDecodeError:
            response = {
                "jsonrpc": "2.0",
                "error": {"code": -32700, "message": "Parse error"},
                "id": None,
            }

        
>
if __name__ == "__main__":
    main()
