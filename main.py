
from fastapi import FastAPI, Request, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    generate_latest
)
import uvicorn
import time

app = FastAPI()

REQUESTS = Counter(
    "api_requests_total",
    "Total API requests",
    ["method", "status", "endpoint"]
)

LATENCY = Histogram(
    "api_request_duration_seconds",
    "API request duration",
    ["endpoint"]
)


@app.get("/")
async def home():
    return {"message": "Hello"}


@app.middleware("http")
async def record_metrics(request: Request, call_next):
    start_time = time.perf_counter()

    response = await call_next(request)

    if request.url.path != "/metrics":
        duration = time.perf_counter() - start_time

        LATENCY.labels(
            endpoint=request.url.path
        ).observe(duration)

        REQUESTS.labels(
            method=request.method,
            status=response.status_code,
            endpoint=request.url.path
        ).inc()

    return response


@app.get("/metrics")
async def get_metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


if __name__ == "__main__":
    uvicorn.run(app, port=5000, host="0.0.0.0")
