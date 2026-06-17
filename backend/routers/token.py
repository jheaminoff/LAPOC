"""Speech token endpoint — proxies Azure Speech STS token to the frontend."""

import os
from urllib.parse import urlparse

import httpx
from fastapi import APIRouter, HTTPException

router = APIRouter()


def _extract_region(endpoint: str) -> str:
    hostname = urlparse(endpoint).hostname or ""
    return hostname.split(".")[0]


@router.get("/speech-token")
async def get_speech_token() -> dict:
    endpoint = os.getenv("AZURE_SPEECH_ENDPOINT", "")
    key = os.getenv("AZURE_SPEECH_KEY", "")

    if not endpoint or not key:
        raise HTTPException(status_code=500, detail="Speech service not configured")

    issue_url = f"{endpoint.rstrip('/')}/sts/v1.0/issueToken"
    headers = {"Ocp-Apim-Subscription-Key": key}

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(issue_url, headers=headers, timeout=10.0)
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail="Failed to fetch speech token from Azure.",
            ) from exc
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=502,
                detail="Could not reach Azure Speech service.",
            ) from exc

    region = _extract_region(endpoint)
    return {"token": resp.text, "region": region}
