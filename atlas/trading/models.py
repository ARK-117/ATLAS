from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Mapping
from uuid import uuid4


class AssetClass(StrEnum):
    EQUITY = "equity"
    ETF = "etf"
    OPTION = "option"
    FUTURE = "future"
    CRYPTO = "crypto"


class OrderSide(StrEnum):
    BUY = "buy"
    SELL = "sell"


class OrderType(StrEnum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class RiskDecision(StrEnum):
    APPROVED = "approved"
    BLOCKED = "blocked"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class Position:
    symbol: str
    quantity: float
    market_price: float
    sector: str = "unknown"
    asset_class: AssetClass = AssetClass.EQUITY

    @property
    def market_value(self) -> float:
        return self.quantity * self.market_price


@dataclass(frozen=True)
class PortfolioState:
    account_id: str
    equity: float
    cash: float
    positions: Mapping[str, Position] = field(default_factory=dict)
    realized_loss_today: float = 0.0
    realized_loss_this_week: float = 0.0
    peak_equity: float | None = None
    kill_switch_active: bool = False

    @property
    def gross_exposure(self) -> float:
        return sum(abs(position.market_value) for position in self.positions.values())

    @property
    def drawdown_percent(self) -> float:
        if not self.peak_equity or self.peak_equity <= 0:
            return 0.0
        return max(0.0, (self.peak_equity - self.equity) / self.peak_equity)

    def position_for(self, symbol: str) -> Position | None:
        return self.positions.get(symbol.upper())

    def sector_exposure(self, sector: str) -> float:
        return sum(
            abs(position.market_value)
            for position in self.positions.values()
            if position.sector.lower() == sector.lower()
        )


@dataclass(frozen=True)
class MarketSnapshot:
    symbol: str
    price: float
    timestamp: datetime
    sector: str
    asset_class: AssetClass = AssetClass.EQUITY
    bid_ask_spread_percent: float = 0.0
    average_daily_dollar_volume: float = 0.0
    volatility_percent: float = 0.0
    is_halted: bool = False
    has_upcoming_earnings: bool = False
    has_major_unverified_news: bool = False
    source: str = "unknown"

    def age_seconds(self, now: datetime | None = None) -> float:
        reference = now or utc_now()
        return (reference - self.timestamp).total_seconds()


@dataclass(frozen=True)
class OrderIntent:
    symbol: str
    side: OrderSide
    quantity: float
    order_type: OrderType = OrderType.MARKET
    limit_price: float | None = None
    stop_price: float | None = None
    strategy_id: str = "manual"
    created_by: str = "user"
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=utc_now)

    def notional(self, market: MarketSnapshot) -> float:
        price = self.limit_price if self.limit_price is not None else market.price
        return abs(self.quantity * price)


@dataclass(frozen=True)
class Approval:
    order_intent_id: str
    approved_by: str
    approved_at: datetime
    expires_at: datetime
    production_acknowledged: bool = False

    def is_valid_for(self, order_intent_id: str, now: datetime | None = None) -> bool:
        reference = now or utc_now()
        return self.order_intent_id == order_intent_id and reference <= self.expires_at


@dataclass(frozen=True)
class RiskPolicy:
    live_trading_enabled: bool = False
    require_human_approval: bool = True
    allowed_asset_classes: tuple[AssetClass, ...] = (AssetClass.EQUITY, AssetClass.ETF)
    allow_margin: bool = False
    allow_short_selling: bool = False
    max_order_notional: float = 1_000.0
    max_single_asset_exposure_percent: float = 0.05
    max_sector_exposure_percent: float = 0.20
    max_gross_exposure_percent: float = 1.00
    max_daily_loss_percent: float = 0.01
    max_weekly_loss_percent: float = 0.02
    max_drawdown_percent: float = 0.08
    max_market_data_age_seconds: int = 30
    min_average_daily_dollar_volume: float = 1_000_000.0
    max_adv_participation_percent: float = 0.01
    max_bid_ask_spread_percent: float = 0.005
    max_volatility_percent: float = 0.08
    block_upcoming_earnings: bool = True
    block_unverified_major_news: bool = True


@dataclass(frozen=True)
class RiskCheckResult:
    decision: RiskDecision
    reasons: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    order_notional: float = 0.0
    post_trade_gross_exposure: float = 0.0
    post_trade_symbol_exposure: float = 0.0
    post_trade_sector_exposure: float = 0.0

    @property
    def approved(self) -> bool:
        return self.decision == RiskDecision.APPROVED

