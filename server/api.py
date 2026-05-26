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


# ==========================================
# ACCOUNT ROUTES (Connection & Onboarding)
# ==========================================
@app.get("/api/accounts/connection-link")
def get_connection_link():
    try:
        response = snaptrade.authentication.login_snap_trade_user(
            query_params={"userId": user_id, "userSecret": user_secret},
            body={"connectionType": "trade"},
        )
        return response.body
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to generate connection link: {str(e)}"
        )


@app.get("/api/accounts/list-accounts")
def list_accounts():
    try:
        response = snaptrade.account_information.list_user_accounts(
            user_id=user_id, user_secret=user_secret
        )
        return response.body
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to list brokerage accounts: {str(e)}"
        )


@app.get("/api/accounts/account-details")
def account_details(account_id: str):
    try:
        response = snaptrade.account_information.get_user_account_details(
            account_id=account_id,
            user_id=user_id,
            user_secret=user_secret,
        )
        return response.body
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to fetch account details: {str(e)}"
        )


@app.get("/api/accounts/list-connections")
def list_connections():
    try:
        response = snaptrade.connections.list_brokerage_authorizations(
            user_id=user_id, user_secret=user_secret
        )
        return response.body
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to list brokerage connections: {str(e)}"
        )


@app.post("/api/accounts/refresh-connection")
def refresh_connection(authorization_id: str):
    try:
        response = snaptrade.connections.refresh_brokerage_authorization(
            authorization_id=authorization_id, user_id=user_id, user_secret=user_secret
        )
        return response.body
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to refresh brokerage connection: {str(e)}"
        )


@app.delete("/api/accounts/disconnect-broker")
def disconnect_broker(authorization_id: str):
    try:
        response = snaptrade.connections.remove_brokerage_authorization(
            authorization_id=authorization_id,
            user_id=user_id,
            user_secret=user_secret,
        )
        return response.body
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to remove brokerage connection: {str(e)}"
        )


# ==========================================
# PORTFOLIO ROUTES (Balances, Positions & Performance)
# ==========================================
@app.get("/api/portfolio/balances")
def portfolio_balances(account_id: str):
    try:
        response = snaptrade.account_information.get_user_account_balance(
            account_id=account_id,
            user_id=user_id,
            user_secret=user_secret,
        )
        return response.body
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to fetch portfolio balances: {str(e)}"
        )


@app.get("/api/portfolio/positions")
def portfolio_positions(account_id: str):
    try:
        response = snaptrade.account_information.get_user_account_positions(
            account_id=account_id,
            user_id=user_id,
            user_secret=user_secret,
        )
        return response.body
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to fetch portfolio positions: {str(e)}"
        )


@app.get("/api/portfolio/drift-analysis")
def portfolio_drift_analysis(account_id: str):
    try:
        response = snaptrade.account_information.get_user_account_positions(
            account_id=account_id,
            user_id=user_id,
            user_secret=user_secret,
        )
        return response.body
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to fetch drift analysis alignment data: {str(e)}",
        )


@app.get("/api/portfolio/history")
def portfolio_history(account_id: str):
    try:
        balance_res = snaptrade.account_information.get_user_account_balance(
            account_id=account_id, user_id=user_id, user_secret=user_secret
        )

        ledger_res = snaptrade.account_information.get_account_activities(
            account_id=account_id,
            user_id=user_id,
            user_secret=user_secret,
            type="CONTRIBUTION,WITHDRAWAL",
        )
        return {
            "status": "success",
            "current_valuation": balance_res.body,
            "capital_flows": ledger_res.body,
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to reconstruct historical net worth matrix: {str(e)}",
        )


# ==========================================
# LONG-TERM PERFORMANCE ROUTES (Dividends & Taxes)
# ==========================================
@app.get("/api/portfolio/dividends")
def dividend_history(
    account_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None
):
    try:
        response = snaptrade.account_information.get_account_activities(
            account_id=account_id,
            user_id=user_id,
            user_secret=user_secret,
            start_date=start_date,
            end_date=end_date,
            type="DIVIDEND,REI",
        )
        return response.body
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to fetch historic dividend ledger: {str(e)}",
        )


@app.get("/api/portfolio/tax-ledger")
def tax_ledger_history(
    account_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None
):
    try:
        response = snaptrade.account_information.get_account_activities(
            account_id=account_id,
            user_id=user_id,
            user_secret=user_secret,
            start_date=start_date,
            end_date=end_date,
            type="CONTRIBUTION,WITHDRAWAL,FEE,TAX",
        )
        return response.body
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to fetch cash flow outlays or fee audits: {str(e)}",
        )


# ==========================================
# STOCK INFO ROUTES (Market Data & Discovery)
# ==========================================
@app.get("/api/stocks/live-quotes")
def live_quotes(account_id: str, symbols: str):
    try:
        symbols = symbols.upper().replace(" ", "")
        response = snaptrade.trading.get_user_account_quotes(
            account_id=account_id,
            user_id=user_id,
            user_secret=user_secret,
            symbols=symbols,
            use_ticker=True,
        )
        return response.body
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to fetch market data snapshot: {str(e)}"
        )


@app.get("/api/stocks/search")
def search_stock(symbol: str):
    try:
        response = snaptrade.reference_data.get_symbols(
            body={"substring": symbol.upper()}
        )
        return response.body
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Ticker lookup system failure: {str(e)}"
        )


# ==========================================
# STOCK ORDER ROUTES (Execution & Management)
# ==========================================
@app.post("/api/stocks/pre-trade-impact")
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
    try:
        search = snaptrade.reference_data.get_symbols(
            body={"substring": symbol.upper()}
        )
        if not search.body:
            raise ValueError(
                f"Could not resolve structural asset reference for ticker symbol: {symbol}"
            )
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
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Order pre-clearance tracking rejected: {str(e)}"
        )


@app.post("/api/stocks/place-order")
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
    try:
        search = snaptrade.reference_data.get_symbols(
            body={"substring": symbol.upper()}
        )
        if not search.body:
            raise ValueError(
                f"Could not resolve structural asset reference for ticker symbol: {symbol}"
            )
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
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Execution rejected by broker routing framework: {str(e)}",
        )


@app.get("/api/stocks/open-orders")
def get_open_orders(account_id: str):
    try:
        response = snaptrade.account_information.get_user_account_orders(
            account_id=account_id,
            user_id=user_id,
            user_secret=user_secret,
            state="open",
        )
        return response.body
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to extract active open orders ledger: {str(e)}",
        )


@app.post("/api/stocks/cancel-order")
def cancel_order(account_id: str, order_id: str):
    try:
        response = snaptrade.trading.cancel_user_account_order(
            account_id=account_id,
            user_id=user_id,
            user_secret=user_secret,
            body={"orderId": order_id},
        )
        return response.body
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Broker cancellation request rejected: {str(e)}"
        )
