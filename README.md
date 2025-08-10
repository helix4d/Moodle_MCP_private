# Moodle MCP Server

This project provides a Moodle MCP (Model Context Protocol) server that allows interaction with a Moodle instance via a command-line interface using JSON-RPC over stdio.

The server uses the `MoodleAPI.py` library to interface with Moodle's web service API.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Install dependencies:**
    Make sure you have Python 3 installed. Then, install the required packages using pip:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Moodle credentials:**
    Create a `.env` file in the root of the project by copying the example file:
    ```bash
    cp .env.example .env
    ```
    Edit the `.env` file and set the following variables with your Moodle instance's details:
    - `MOODLE_DOMAIN`: Your Moodle site URL (e.g., `https://moodle.example.com`).
    - `MOODLE_TOKEN`: Your Moodle web service token.

## Usage

Run the server from the command line:
```bash
python mcp_server.py
```

The server will start and listen for JSON-RPC requests on standard input.

### Example

To get a list of all cohorts, send the following JSON request to the server's standard input:

```json
{
    "jsonrpc": "2.0",
    "method": "get_cohorts",
    "id": 1
}
```

The server will respond on its standard output with a JSON object containing the list of cohorts:

```json
{
    "jsonrpc": "2.0",
    "result": [
        {
            "id": 1,
            "name": "Cohort 1",
            "idnumber": "C1",
            "description": "",
            "descriptionformat": 1,
            "visible": true,
            "theme": null
        }
    ],
    "id": 1
}
```

## Available Methods

The server exposes the public methods of the `MoodleAPI` class. Refer to `MoodleAPI.py` for a full list of available methods and their parameters.
