# imports
import os
from typing import Optional
from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]
from fastapi import FastAPI, HTTPException  # pyright: ignore[reportMissingImports]
from pydantic import BaseModel  # pyright: ignore[reportMissingImports]
from snaptrade_client import SnapTrade  # pyright: ignore[reportMissingImports]

# initializations
load_dotenv()
app = FastAPI()

# env variables
snaptrade = SnapTrade(
    client_id=os.getenv("SNAPTRADE_CLIENT"),
    consumer_key=os.getenv("SNAPTRADE_CONSUMER"),
)
user_id = os.getenv("SNAPTRADE_USERID")
user_secret = os.getenv("SNAPTRADE_SECRET")


# account routes
@app.get("/accounts/connection-link")
def get_connection_link():
    response = snaptrade.authentication.login_snap_trade_user(
        query_params={"userId": user_id, "userSecret": user_secret},
        body={"connectionType": "trade"},
    )
    return response.body


@app.get("/accounts/list-accounts")
def list_accounts():
    response = snaptrade.account_information.list_user_accounts(
        user_id=user_id, user_secret=user_secret
    )
    return response.body


@app.get("/accounts/account-details")
def account_details(account_id: str):
    response = snaptrade.account_information.get_user_account_details(
        account_id=account_id,
        user_id=user_id,
        user_secret=user_secret,
    )
    return response.body


# stock info routes
@app.get("/stocks/live-quotes")
def live_quotes(account_id: str, symbols: str):
    symbols = symbols.upper().replace(" ", "")

    response = snaptrade.trading.get_user_account_quotes(
        account_id=account_id,
        user_id=user_id,
        user_secret=user_secret,
        symbols=symbols,
        use_ticker=True,
    )
    return response.body


@app.post("/stocks/pre-trade-impact")
def pre_trade_impact(
    account_id: str,
    action: str,
    symbol: str,
    order_type: str,
    time_in_force: str,
    units: float,
    price: Optional[float] = None,
    stop: Optional[float] = None,
):
    search = snaptrade.reference_data.get_symbols(body={"substring": symbol.upper()})
    symbol_id = search.body[0]["id"]

    order_data = {
        "account_id": account_id,
        "action": action.upper(),
        "universal_symbol_id": symbol_id,
        "order_type": order_type,
        "time_in_force": time_in_force,
        "units": units,
    }
    if price:
        order_data["price"] = price
    if stop:
        order_data["stop"] = stop

    response = snaptrade.trading.get_order_impact(
        user_id=user_id, user_secret=user_secret, body=order_data
    )
    return response.body


# stock order routes
@app.post("/stocks/place-order")
def place_order(
    account_id: str,
    action: str,
    symbol: str,
    order_type: str,
    time_in_force: str,
    units: float,
    price: Optional[float] = None,
    stop: Optional[float] = None,
):
    search = snaptrade.reference_data.get_symbols(body={"substring": symbol.upper()})
    symbol_id = search.body[0]["id"]

    order_data = {
        "account_id": account_id,
        "action": action.upper(),
        "universal_symbol_id": symbol_id,
        "order_type": order_type,
        "time_in_force": time_in_force,
        "units": units,
    }
    if price:
        order_data["price"] = price
    if stop:
        order_data["stop"] = stop

    response = snaptrade.trading.place_force_order(
        user_id=user_id, user_secret=user_secret, body=order_data
    )
    return response.body
