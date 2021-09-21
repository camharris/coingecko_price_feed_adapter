from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
import os
from pydantic import BaseModel
import requests
from typing import Any, Optional
from starlette.applications import Starlette
from starlette.responses import Response
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_403_FORBIDDEN, HTTP_200_OK

X_API_KEY_HEADER = APIKeyHeader(name="X-API-KEY", auto_error=False)
app = FastAPI()

def get_api_key(header: str = Security(X_API_KEY_HEADER)):
    """ Retrieves api key and validates it"""
    if header == os.getenv('API_KEY'):
        return header

    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
    )

class Request(BaseModel):
    id: str
    data: Any

class Response(BaseModel):
    jobRunID: str
    data: Any
    result: Optional[Any]
    statusCode: Optional[int]

@app.get('/healthcheck', response_model=Response)
def health_check():
    """
    Endpoint for manual and automated health checks
    """
    return Response(jobRunID=1, data={True})

@app.get('/ghoul_usd', response_model=Response, dependencies=[Security(get_api_key)])
def ghoul_usd():
    """
    Get price of ghoul token
    """
    url = 'https://api.coingecko.com/api/v3/coins/ghoul-token?tickers=false&market_data=true&community_data=false&developer_data=false&sparkline=false'
    r = requests.get(url)
    price = r.json()['market_data']['current_price']['usd']
    adjusted_price = price * 100000000
    return Response(jobRunID=1, data={adjusted_price}, statusCode=200, result={adjusted_price})        
