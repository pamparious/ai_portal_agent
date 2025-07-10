# Available Scripts and Commands

This document outlines the various scripts and commands available for developing, testing, and running the Thomson Reuters AI Portal MCP Agent.

## Development

### Python Virtual Environment
To set up the Python virtual environment:
```bash
python -m venv venv
```

To activate the virtual environment:
- On Windows:
  ```bash
  .\venv\Scripts\activate
  ```
- On macOS/Linux:
  ```bash
  source venv/bin/activate
  ```

### Install Dependencies
Once the virtual environment is activated, install the required Python packages:
```bash
pip install -r requirements.txt
```

## Running the MCP Agent

### Start Edge Browser with Remote Debugging
Before running the agent, ensure Microsoft Edge is launched with remote debugging enabled on port 9222. You can do this by running the following command in your terminal:

```bash
"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9222 --user-data-dir="C:\EdgeProfile"
```
Replace `"C:\EdgeProfile"` with the actual path to your Edge user profile directory.

### Run the MCP Server
(Details to be added once the MCP server is implemented)

## Testing

### Run Unit Tests
(Details to be added once tests are implemented)

### Run Integration Tests
(Details to be added once tests are implemented)

## Linting and Formatting
(Details to be added for code quality checks)
