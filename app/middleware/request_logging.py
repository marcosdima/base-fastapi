import time
import json
from fastapi import FastAPI, Request
from starlette.responses import Response
from ..utils.settings import settings


RESET = '\033[0m'
BLUE = '\033[94m'
CYAN = '\033[96m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
GRAY = '\033[90m'
WHITE = '\033[97m'

MAX_BODY_CHARS = 2000
BLOCK_WIDTH = 92


def _colorize(value: str, color: str) -> str:
    return f'{color}{value}{RESET}'


def _status_color(status_code: int) -> str:
    return GREEN if status_code < 400 else RED


def _format_method(method: str) -> str:
    method_colors = {
        'GET': GREEN,
        'POST': BLUE,
        'PUT': CYAN,
        'PATCH': CYAN,
        'DELETE': RED,
    }
    color = method_colors.get(method.upper(), GRAY)
    return _colorize(method.upper().ljust(6), color)


def _format_status(status_code: int) -> str:
    if status_code >= 500:
        color = RED
    elif status_code >= 400:
        color = YELLOW
    else:
        color = GREEN
    return _colorize(str(status_code), color)


def _format_duration(duration_ms: float) -> str:
    if duration_ms >= 1000:
        color = RED
    elif duration_ms >= 300:
        color = YELLOW
    else:
        color = GREEN
    return _colorize(f'{duration_ms:.2f}ms', color)


def _build_request_line(request: Request, status_code: int, duration_ms: float) -> str:
    method = _format_method(request.method)
    status = _format_status(status_code)
    duration = _format_duration(duration_ms)
    path = _colorize(request.url.path, CYAN)

    query = str(request.url.query)
    query_part = f'?{query}' if query else ''

    return f'{method}  {path}{query_part}  status={status}  duration={duration}'


def _truncate(text: str, max_chars: int = MAX_BODY_CHARS) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + '...<truncated>'


def _safe_decode(raw_data: bytes) -> str:
    if not raw_data:
        return '<empty>'
    try:
        return raw_data.decode('utf-8')
    except UnicodeDecodeError:
        return '<binary>'


def _safe_json_or_text(raw_data: bytes) -> str:
    decoded = _safe_decode(raw_data)
    if decoded in {'<empty>', '<binary>'}:
        return decoded

    try:
        parsed = json.loads(decoded)
        return _truncate(json.dumps(parsed, ensure_ascii=True, default=str))
    except json.JSONDecodeError:
        return _truncate(decoded)


def _safe_headers(headers: dict[str, str]) -> dict[str, str]:
    sensitive = {'authorization', 'cookie', 'set-cookie'}
    return {
        key: ('***' if key.lower() in sensitive else value)
        for key, value in headers.items()
    }


def _ascii_header(title: str, color: str) -> str:
    line = '+' + ('-' * (BLOCK_WIDTH - 2)) + '+'
    title_text = f'| {title}'
    title_line = title_text.ljust(BLOCK_WIDTH - 1) + '|'
    return '\n'.join([
        _colorize(line, color),
        _colorize(title_line, color),
        _colorize(line, color),
    ])


def _kv(label: str, value: str) -> str:
    return f'{_colorize(label + ":", WHITE)} {value}'


def _build_request_block(request: Request, raw_body: bytes) -> str:
    query = str(request.url.query) or '-'
    return '\n'.join([
        _kv('method', request.method),
        _kv('path', request.url.path),
        _kv('query', query),
        _kv('path_params', json.dumps(request.path_params, ensure_ascii=True, default=str)),
        _kv('headers', json.dumps(_safe_headers(dict(request.headers)), ensure_ascii=True, default=str)),
        _kv('body', _safe_json_or_text(raw_body)),
    ])


def _build_response_block(response: Response, raw_body: bytes, duration_ms: float) -> str:
    response_headers = {
        'content-type': response.headers.get('content-type', '-'),
        'content-length': response.headers.get('content-length', '-'),
    }
    return '\n'.join([
        _kv('status_code', str(response.status_code)),
        _kv('duration', f'{duration_ms:.2f}ms'),
        _kv('headers', json.dumps(response_headers, ensure_ascii=True, default=str)),
        _kv('body', _safe_json_or_text(raw_body)),
    ])


async def _read_response_body(response: Response) -> bytes:
    body = b''
    async for chunk in response.body_iterator:
        body += chunk
    return body


def _rebuild_response(response: Response, raw_body: bytes) -> Response:
    rebuilt = Response(
        content=raw_body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type,
    )
    rebuilt.background = response.background
    return rebuilt


def _build_full_log(
    request: Request,
    response: Response,
    request_body: bytes,
    response_body: bytes,
    duration_ms: float,
) -> str:
    color = _status_color(response.status_code)
    request_line = _build_request_line(request, response.status_code, duration_ms)
    return '\n'.join([
        _ascii_header('HTTP TRACE', color),
        request_line,
        _colorize('REQUEST', color),
        _build_request_block(request, request_body),
        _colorize('RESPONSE', color),
        _build_response_block(response, response_body, duration_ms),
        _colorize('+' + ('-' * (BLOCK_WIDTH - 2)) + '+', color),
    ])


def register_request_logging_middleware(app: FastAPI) -> None:
    @app.middleware('http')
    async def log_requests(request: Request, call_next):
        if not settings.LOG_REQUESTS:
            return await call_next(request)

        start = time.perf_counter()
        request_body = await request.body()

        response = await call_next(request)
        response_body = await _read_response_body(response)

        duration_ms = (time.perf_counter() - start) * 1000
        print(
            _build_full_log(request, response, request_body, response_body, duration_ms),
            flush=True,
        )

        return _rebuild_response(response, response_body)
