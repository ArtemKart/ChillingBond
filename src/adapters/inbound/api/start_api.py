if __name__ == "__main__":
    import os
    import uvicorn

    host = os.getenv("API_HOST", "127.0.0.1")
    port = int(os.getenv("API_PORT", "8000"))

    uvicorn.run(
        "src.adapters.inbound.api.main:app",
        host=host,
        port=port,
        reload=True,
        log_config=None,
        access_log=True,
        use_colors=True,
    )
