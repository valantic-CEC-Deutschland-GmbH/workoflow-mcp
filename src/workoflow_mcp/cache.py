"""TTL cache for tool definitions."""

import hashlib
import os
import time
from typing import Any


class ToolCache:
    """Simple TTL cache for tool definitions."""

    def __init__(self, ttl_seconds: int | None = None):
        """Initialize the cache.

        Args:
            ttl_seconds: Cache TTL in seconds. Defaults to CACHE_TTL_SECONDS env var or 600.
        """
        self.ttl_seconds = ttl_seconds or int(os.getenv("CACHE_TTL_SECONDS", "600"))
        self._cache: dict[str, tuple[list[dict[str, Any]], float]] = {}

    def _make_key(self, prompt_token: str, tool_types: str | None) -> str:
        """Create a cache key from token and tool types.

        We hash the token to avoid storing sensitive data in memory.
        """
        token_hash = hashlib.sha256(prompt_token.encode()).hexdigest()[:16]
        return f"{token_hash}:{tool_types or 'all'}"

    def get(self, prompt_token: str, tool_types: str | None = None) -> list[dict[str, Any]] | None:
        """Get cached tools if available and not expired.

        Args:
            prompt_token: User's personal access token.
            tool_types: Tool type filter.

        Returns:
            Cached tools or None if not cached or expired.
        """
        key = self._make_key(prompt_token, tool_types)

        if key not in self._cache:
            return None

        tools, timestamp = self._cache[key]

        if time.time() - timestamp > self.ttl_seconds:
            # Expired, remove from cache
            del self._cache[key]
            return None

        return tools

    def set(self, prompt_token: str, tool_types: str | None, tools: list[dict[str, Any]]) -> None:
        """Cache tools for the given token and tool types.

        Args:
            prompt_token: User's personal access token.
            tool_types: Tool type filter.
            tools: Tools to cache.
        """
        key = self._make_key(prompt_token, tool_types)
        self._cache[key] = (tools, time.time())

    def invalidate(self, prompt_token: str, tool_types: str | None = None) -> None:
        """Invalidate cache for the given token.

        Args:
            prompt_token: User's personal access token.
            tool_types: Tool type filter. If None, invalidates all entries for this token.
        """
        if tool_types is not None:
            key = self._make_key(prompt_token, tool_types)
            self._cache.pop(key, None)
        else:
            # Invalidate all entries for this token
            token_hash = hashlib.sha256(prompt_token.encode()).hexdigest()[:16]
            keys_to_remove = [k for k in self._cache.keys() if k.startswith(f"{token_hash}:")]
            for key in keys_to_remove:
                del self._cache[key]

    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()


# Singleton instance
_cache: ToolCache | None = None


def get_cache() -> ToolCache:
    """Get the singleton ToolCache instance."""
    global _cache
    if _cache is None:
        _cache = ToolCache()
    return _cache
