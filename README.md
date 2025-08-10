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

The server exposes the public methods of the `MoodleAPI` class. Here is a list of the available methods and their parameters:

### Cohort Methods
- `get_cohorts()`
- `get_cohort(cohort_id: int)`
- `get_cohort_members(cohort_id: int)`
- `get_cohort_teachers(cohort_id: int, get_cohort_members)`
- `update_cohort(cohort_id: int)`
- `search_cohorts(name: str)`
- `create_cohort(name: str, idnumber: str, description: str)`
- `add_cohort_member(cohort_id: int, user_id: int)`
- `delete_cohort_member(cohort_id: int, user_id: int)`

### Course Methods
- `get_course_contents(course_id: int)`
- `get_course_by_id(course_id: int)`

### Enrolment and User Methods
- `get_user_courses(user_id: int)`
- `get_teacher_courses(courses: list, user_id: int, get_enrolled_users_of_course)`
- `get_enrolled_users_of_course(course_id: int)`
- `get_all_users()`
- `get_user_by_id(user_id: int)`

### Quiz Methods
- `get_tests_in_course(course_id: int)`
- `get_attempts_by_users(test_id: int, course_id: int, log=None)`
- `collect_exams_results(courses: list, log=None)`
- `extract_lectures_and_practices(course_contents: list)`
