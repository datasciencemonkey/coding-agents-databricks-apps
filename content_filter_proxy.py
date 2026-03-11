#!/usr/bin/env python
"""Lightweight HTTP proxy that sanitizes requests and responses between OpenCode and Databricks.

Request-side fixes:
  - Strips empty/whitespace-only text content blocks (OpenCode #5028)
  - Strips orphaned tool_result blocks with no matching tool_use
  - Removes empty messages after filtering

Response-side fixes:
  - Remaps 'databricks-tool-call' back to real tool names
  - Fixes finish_reason when tool calls are present

Runs on localhost (never exposed externally). Zero external dependencies
beyond stdlib + requests (already installed via databricks-sdk).

See: https://github.com/sst/opencode/issues/5028
     https://github.com/BerriAI/litellm/pull/20384
"""
import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

import requests

UPSTREAM_BASE = os.environ.get("PROXY_UPSTREAM_BASE", "")
LISTEN_HOST = os.environ.get("PROXY_HOST", "127.0.0.1")
LISTEN_PORT = int(os.environ.get("PROXY_PORT", "4000"))


# ---------------------------------------------------------------------------
# Request-side sanitization
# ---------------------------------------------------------------------------

def sanitize_messages(messages):
    """Strip empty text blocks and orphaned tool_result/tool messages."""
    if not isinstance(messages, list):
        return messages

    # First pass: collect tool_use/tool_call IDs per assistant message index
    # so we can validate tool_results in the following user/tool message.
    assistant_tool_ids = {}  # msg_index -> set of tool IDs
    for i, msg in enumerate(messages):
        role = msg.get("role", "")
        if role != "assistant":
            continue
        ids = set()
        # Anthropic format: content blocks with type=tool_use
        content = msg.get("content")
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    tid = block.get("id")
                    if tid:
                        ids.add(tid)
        # OpenAI format: tool_calls array
        for tc in msg.get("tool_calls", []):
            tid = tc.get("id")
            if tid:
                ids.add(tid)
        assistant_tool_ids[i] = ids

    # Second pass: clean messages
    cleaned = []
    for i, msg in enumerate(messages):
        role = msg.get("role", "")
        content = msg.get("content")

        # Find the most recent preceding assistant message's tool IDs
        prev_tool_ids = set()
        for j in range(i - 1, -1, -1):
            if messages[j].get("role") == "assistant":
                prev_tool_ids = assistant_tool_ids.get(j, set())
                break

        # --- Handle list content (Anthropic format) ---
        if isinstance(content, list):
            filtered = []
            for block in content:
                if not isinstance(block, dict):
                    filtered.append(block)
                    continue

                # Strip empty/whitespace-only text blocks
                if block.get("type") == "text" and block.get("text", "").strip() == "":
                    continue

                # Strip orphaned tool_result blocks
                if block.get("type") == "tool_result":
                    tool_use_id = block.get("tool_use_id")
                    if tool_use_id and tool_use_id not in prev_tool_ids:
                        continue

                filtered.append(block)

            if not filtered:
                # Don't drop assistant messages (would break alternation)
                if role == "assistant":
                    msg = {**msg, "content": filtered}
                else:
                    continue
            else:
                msg = {**msg, "content": filtered}

        # --- Handle OpenAI tool messages ---
        elif role == "tool":
            tool_call_id = msg.get("tool_call_id")
            if tool_call_id and tool_call_id not in prev_tool_ids:
                continue  # Orphaned tool response

        # --- Handle empty string content ---
        elif isinstance(content, str) and content.strip() == "":
            if role != "assistant":
                continue

        cleaned.append(msg)

    return cleaned


# ---------------------------------------------------------------------------
# Response-side fixes
# ---------------------------------------------------------------------------

def remap_tool_call(tool_call):
    """If tool name is 'databricks-tool-call', extract real name from arguments."""
    func = tool_call.get("function", {})
    if func.get("name") != "databricks-tool-call":
        return tool_call

    args_str = func.get("arguments", "")
    try:
        args = json.loads(args_str)
        if isinstance(args, dict) and "name" in args:
            real_name = args.pop("name")
            tool_call = {**tool_call, "function": {
                **func,
                "name": real_name,
                "arguments": json.dumps(args),
            }}
    except (json.JSONDecodeError, TypeError):
        pass  # Can't parse — leave as-is

    return tool_call


def fix_response_data(data):
    """Fix tool names and finish_reason in a parsed response object."""
    if not isinstance(data, dict):
        return data

    for choice in data.get("choices", []):
        # Non-streaming: choice.message
        message = choice.get("message", {})
        tool_calls = message.get("tool_calls", [])
        if tool_calls:
            message["tool_calls"] = [remap_tool_call(tc) for tc in tool_calls]
            # Fix finish_reason: should be "tool_calls" if tools are invoked
            if choice.get("finish_reason") == "stop" and tool_calls:
                choice["finish_reason"] = "tool_calls"

        # Streaming: choice.delta
        delta = choice.get("delta", {})
        delta_tool_calls = delta.get("tool_calls", [])
        if delta_tool_calls:
            delta["tool_calls"] = [remap_tool_call(tc) for tc in delta_tool_calls]

        # Fix finish_reason for streaming chunks
        if choice.get("finish_reason") == "stop" and delta_tool_calls:
            choice["finish_reason"] = "tool_calls"

    return data


# ---------------------------------------------------------------------------
# SSE stream processing
# ---------------------------------------------------------------------------

class SSEProcessor:
    """Buffers and fixes SSE events, handling tool name remapping across chunks."""

    def __init__(self):
        # Per tool-call-index state for streaming name resolution
        # {index: {"args_buffer": str, "resolved_name": str|None, "buffered_lines": []}}
        self._tool_state = {}
        self._pending_flush = []

    def process_line(self, line):
        """Process one SSE line. Returns list of lines to send (may be empty if buffering)."""
        # Non-data lines pass through immediately
        if not line.startswith("data: "):
            return [line]

        payload = line[6:]  # Strip "data: " prefix

        # [DONE] signal passes through
        if payload.strip() == "[DONE]":
            # Flush any remaining buffered events
            result = list(self._pending_flush)
            self._pending_flush.clear()
            result.append(line)
            return result

        # Parse event JSON
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            return [line]  # Can't parse — pass through

        # Check for tool calls that need remapping
        needs_buffering = False
        for choice in data.get("choices", []):
            delta = choice.get("delta", {})
            for tc in delta.get("tool_calls", []):
                idx = tc.get("index", 0)
                func = tc.get("function", {})

                # First chunk with tool name
                if "name" in func:
                    if func["name"] == "databricks-tool-call":
                        self._tool_state[idx] = {
                            "args_buffer": func.get("arguments", ""),
                            "resolved_name": None,
                            "buffered_lines": [],
                        }
                        needs_buffering = True
                    else:
                        # Normal tool name — no remapping needed
                        self._tool_state.pop(idx, None)

                # Argument chunks for a pending tool call
                elif idx in self._tool_state and self._tool_state[idx]["resolved_name"] is None:
                    state = self._tool_state[idx]
                    state["args_buffer"] += func.get("arguments", "")
                    needs_buffering = True

                    # Try to extract the real name from accumulated arguments
                    try:
                        args = json.loads(state["args_buffer"])
                        if isinstance(args, dict) and "name" in args:
                            state["resolved_name"] = args.pop("name")
                            # Rewrite all buffered events with the real name
                            flushed = self._flush_tool_buffer(idx, state["resolved_name"], args)
                            return flushed + [self._rewrite_event_line(line, data)]
                    except json.JSONDecodeError:
                        pass  # Arguments still incomplete — keep buffering

                # Subsequent chunks after name is resolved
                elif idx in self._tool_state and self._tool_state[idx]["resolved_name"]:
                    # Name already resolved — strip "name" from args if present
                    pass  # Just pass through, name was fixed in first event

            # Fix finish_reason
            if choice.get("finish_reason") == "stop":
                # Check if any tool calls were made in this response
                if self._tool_state:
                    choice["finish_reason"] = "tool_calls"

        if needs_buffering:
            # Buffer this event until we can resolve the tool name
            for idx, state in self._tool_state.items():
                if state["resolved_name"] is None:
                    state["buffered_lines"].append(line)
                    return []  # Don't send yet

        # No buffering needed — fix and forward
        fixed = fix_response_data(data)
        return [f"data: {json.dumps(fixed)}"]

    def _flush_tool_buffer(self, idx, real_name, cleaned_args):
        """Rewrite buffered events with the resolved tool name."""
        state = self._tool_state[idx]
        result = []
        for buffered_line in state["buffered_lines"]:
            payload = buffered_line[6:]  # Strip "data: "
            try:
                bdata = json.loads(payload)
                for choice in bdata.get("choices", []):
                    delta = choice.get("delta", {})
                    for tc in delta.get("tool_calls", []):
                        if tc.get("index", 0) == idx:
                            func = tc.get("function", {})
                            if "name" in func and func["name"] == "databricks-tool-call":
                                func["name"] = real_name
                            if "arguments" in func:
                                # Clear arguments in buffered events (we'll send clean args)
                                func["arguments"] = ""
                result.append(f"data: {json.dumps(bdata)}")
            except json.JSONDecodeError:
                result.append(buffered_line)

        state["buffered_lines"].clear()

        # Send the cleaned arguments as a separate event
        args_event = {
            "choices": [{
                "delta": {
                    "tool_calls": [{
                        "index": idx,
                        "function": {"arguments": json.dumps(cleaned_args)}
                    }]
                },
                "finish_reason": None
            }]
        }
        result.append(f"data: {json.dumps(args_event)}")
        return result

    def _rewrite_event_line(self, line, data):
        """Rewrite an event line with fixed data."""
        fixed = fix_response_data(data)
        return f"data: {json.dumps(fixed)}"

    def flush_remaining(self):
        """Flush any remaining buffered events (graceful fallback)."""
        result = []
        for idx, state in self._tool_state.items():
            for buffered_line in state["buffered_lines"]:
                result.append(buffered_line)
            state["buffered_lines"].clear()
        result.extend(self._pending_flush)
        self._pending_flush.clear()
        return result


# ---------------------------------------------------------------------------
# HTTP Server
# ---------------------------------------------------------------------------

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle concurrent requests (e.g., health checks during streaming)."""
    daemon_threads = True


class ProxyHandler(BaseHTTPRequestHandler):
    """Proxy that sanitizes requests and fixes responses."""

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        # --- Sanitize request ---
        try:
            data = json.loads(body)
            if "messages" in data:
                data["messages"] = sanitize_messages(data["messages"])
            body = json.dumps(data).encode()
        except (json.JSONDecodeError, KeyError):
            pass  # Forward as-is if not valid JSON

        # Build upstream URL
        upstream_url = UPSTREAM_BASE + self.path

        # Forward headers
        headers = {}
        for key in self.headers:
            if key.lower() not in ("host", "content-length", "transfer-encoding"):
                headers[key] = self.headers[key]
        headers["Content-Length"] = str(len(body))

        # Detect streaming
        is_stream = False
        try:
            is_stream = json.loads(body).get("stream", False)
        except Exception:
            pass

        try:
            resp = requests.post(
                upstream_url,
                data=body,
                headers=headers,
                stream=is_stream,
                timeout=300,
            )

            # --- Non-streaming response ---
            if not is_stream:
                # Fix response
                try:
                    resp_data = resp.json()
                    resp_data = fix_response_data(resp_data)
                    resp_body = json.dumps(resp_data).encode()
                except (json.JSONDecodeError, ValueError):
                    resp_body = resp.content

                self.send_response(resp.status_code)
                for key, value in resp.headers.items():
                    if key.lower() not in ("transfer-encoding", "content-encoding", "content-length"):
                        self.send_header(key, value)
                self.send_header("Content-Length", str(len(resp_body)))
                self.end_headers()
                self.wfile.write(resp_body)
                return

            # --- Streaming response ---
            self.send_response(resp.status_code)
            for key, value in resp.headers.items():
                if key.lower() not in ("transfer-encoding", "content-encoding", "content-length"):
                    self.send_header(key, value)
            self.send_header("Transfer-Encoding", "chunked")
            self.end_headers()

            processor = SSEProcessor()

            for raw_line in resp.iter_lines(decode_unicode=True):
                if raw_line is None:
                    continue

                line = raw_line.strip() if isinstance(raw_line, str) else raw_line.decode().strip()

                if not line:
                    # Blank line = event boundary, send it
                    self._send_chunk(b"\r\n")
                    continue

                # Process through SSE fixer
                output_lines = processor.process_line(line)
                for out_line in output_lines:
                    self._send_chunk((out_line + "\r\n").encode())

            # Flush any remaining buffered events
            for remaining in processor.flush_remaining():
                self._send_chunk((remaining + "\r\n").encode())

            # Send final zero-length chunk to end chunked transfer
            self._send_chunk(b"")

        except requests.exceptions.ConnectionError as e:
            self.send_error(502, f"Upstream connection failed: {e}")
        except requests.exceptions.Timeout:
            self.send_error(504, "Upstream timeout")

    def _send_chunk(self, data):
        """Send a chunk in HTTP chunked transfer encoding."""
        if data:
            chunk = f"{len(data):x}\r\n".encode() + data + b"\r\n"
        else:
            chunk = b"0\r\n\r\n"  # Final chunk
        try:
            self.wfile.write(chunk)
            self.wfile.flush()
        except BrokenPipeError:
            pass

    def do_GET(self):
        """Health check endpoint."""
        if self.path == "/health":
            body = json.dumps({"status": "ok", "upstream": UPSTREAM_BASE}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_error(404)

    def log_message(self, format, *args):
        """Suppress per-request logging to keep container logs clean."""
        pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if not UPSTREAM_BASE:
        print("Error: PROXY_UPSTREAM_BASE environment variable is required", file=sys.stderr)
        sys.exit(1)

    server = ThreadedHTTPServer((LISTEN_HOST, LISTEN_PORT), ProxyHandler)
    print(f"Content-filter proxy listening on {LISTEN_HOST}:{LISTEN_PORT}")
    print(f"Forwarding to: {UPSTREAM_BASE}")
    print(f"Fixes: empty text blocks, orphaned tool_results, tool name remapping, finish_reason")
    sys.stdout.flush()
    server.serve_forever()
