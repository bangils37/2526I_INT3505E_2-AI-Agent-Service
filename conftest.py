def pytest_collectstart(collector):
    """Compatibility shim: ensure collectors have `.obj` attribute so pytest-asyncio
    plugin can safely set `__pytest_asyncio_scoped_event_loop` during collection.

    This avoids an INTERNALERROR observed in some environments where the plugin
    expects `collector.obj` to exist for package collectors.
    """
    if not hasattr(collector, "obj"):
        # assign a small placeholder object that can hold attributes and is hashable
        class _CollectorPlaceholder:
            pass

        collector.obj = _CollectorPlaceholder()
