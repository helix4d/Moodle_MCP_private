import sys
import json
from MoodleAPI import MoodleAPI
from logger import setup_logger

def main():
    logger = setup_logger("mcp_server", "mcp_server.log")
    logger.info("MCP server started")

    moodle_api = MoodleAPI(domain=None, token=None, logger=logger)

    while True:
        line = sys.stdin.readline()
        if not line:
            logger.info("No more input, shutting down.")
            break

        logger.debug(f"Received request: {line.strip()}")
        response = None
        try:
            request = json.loads(line)
            method_name = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")

            if not method_name:
                logger.error("Request is missing 'method' field.")
                response = {
                    "jsonrpc": "2.0",
                    "error": {"code": -32600, "message": "Invalid Request"},
                    "id": request_id,
                }
            elif not hasattr(moodle_api, method_name) or method_name.startswith("_"):
                logger.error(f"Method not found or private: {method_name}")
                response = {
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": "Method not found"},
                    "id": request_id,
                }
            else:
                logger.info(f"Calling method '{method_name}' with params: {params}")
                method = getattr(moodle_api, method_name)
                try:
                    result = method(**params)
                    response = {
                        "jsonrpc": "2.0",
                        "result": result,
                        "id": request_id,
                    }
                    logger.info(f"Method '{method_name}' executed successfully.")
                except Exception as e:
                    logger.error(f"Error executing method '{method_name}': {e}", exc_info=True)
                    response = {
                        "jsonrpc": "2.0",
                        "error": {"code": -32603, "message": f"Internal error: {e}"},
                        "id": request_id,
                    }
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON request.", exc_info=True)
            response = {
                "jsonrpc": "2.0",
                "error": {"code": -32700, "message": "Parse error"},
                "id": None,
            }
        except Exception as e:
            logger.critical(f"An unexpected error occurred: {e}", exc_info=True)
            response = {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": "Internal error"},
                "id": None, # ID may not be available
            }

        if response:
            response_str = json.dumps(response)
            logger.debug(f"Sending response: {response_str}")
            sys.stdout.write(response_str + "\\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
