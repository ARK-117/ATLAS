from __future__ import annotations

from datetime import datetime

from .models import (
    Approval,
    AssetClass,
    MarketSnapshot,
    OrderIntent,
    OrderSide,
    OrderType,
    PortfolioState,
    RiskCheckResult,
    RiskDecision,
    RiskPolicy,
    TradingPermissionLevel,
)

COMPLEX_ORDER_TYPES = {
    OrderType.STOP,
    OrderType.STOP_LIMIT,
    OrderType.TRAILING_STOP,
    OrderType.BRACKET,
    OrderType.OCO,
    OrderType.MULTI_LEG,
}


class RiskEngine:
    """Deterministic pre-trade risk checks for live and simulated order intents."""

    def evaluate(
        self,
        intent: OrderIntent,
        portfolio: PortfolioState,
        market: MarketSnapshot,
        policy: RiskPolicy,
        approval: Approval | None = None,
        now: datetime | None = None,
    ) -> RiskCheckResult:
        reasons: list[str] = []
        warnings: list[str] = []

        if portfolio.kill_switch_active:
            reasons.append("kill switch is active")

        if not policy.live_trading_enabled:
            reasons.append("live trading is not enabled in risk policy")

        if not policy.live_production_mode:
            reasons.append("live production mode is not active")

        if policy.permission_level < TradingPermissionLevel.LIVE_CASH_EQUITIES:
            reasons.append("permission level is below live cash equities")

        if not policy.broker_connection_configured:
            reasons.append("broker connection is not configured")

        if not policy.separate_paper_and_live_keys:
            reasons.append("separate paper and live API keys are not confirmed")

        if not policy.secure_secrets_management:
            reasons.append("secure secrets management is not confirmed")

        if not policy.user_authenticated:
            reasons.append("user authentication is required")

        if not policy.role_permission_granted:
            reasons.append("role permission is required")

        if policy.require_human_approval and not policy.approval_workflow_enabled:
            reasons.append("approval workflow is not enabled")

        if not policy.emergency_kill_switch_available:
            reasons.append("emergency kill switch is not available")

        if not policy.broker_status_healthy:
            reasons.append("broker status is not healthy")

        if not policy.compliance_checks_passed:
            reasons.append("compliance checks have not passed")

        if not policy.duplicate_order_check_passed:
            reasons.append("duplicate order check failed")

        if intent.quantity <= 0:
            reasons.append("order quantity must be greater than zero")

        if market.price <= 0:
            reasons.append("market price must be greater than zero")

        if market.symbol.upper() != intent.symbol.upper():
            reasons.append("market snapshot symbol does not match order intent")

        if intent.asset_class != market.asset_class:
            reasons.append("order intent asset class does not match market snapshot")

        if intent.asset_class not in policy.allowed_asset_classes:
            reasons.append(f"asset class {intent.asset_class.value} is not allowed")

        required_permission = self._required_permission(intent.asset_class)
        if policy.permission_level < required_permission:
            reasons.append(
                f"permission level is below required {required_permission.name.lower()}"
            )

        self._check_asset_module_permissions(intent, policy, reasons)
        self._check_live_order_fields(intent, reasons)

        if market.is_halted:
            reasons.append("instrument is halted")

        if market.age_seconds(now) > policy.max_market_data_age_seconds:
            reasons.append("market data is stale")

        if market.bid_ask_spread_percent > policy.max_bid_ask_spread_percent:
            reasons.append("bid-ask spread exceeds limit")

        if market.average_daily_dollar_volume < policy.min_average_daily_dollar_volume:
            reasons.append("average daily dollar volume is below liquidity minimum")

        if market.volatility_percent > policy.max_volatility_percent:
            reasons.append("volatility exceeds limit")

        if policy.block_upcoming_earnings and market.has_upcoming_earnings:
            reasons.append("upcoming earnings restriction is active")

        if policy.block_unverified_major_news and market.has_major_unverified_news:
            reasons.append("unverified major news restriction is active")

        if policy.require_human_approval:
            if approval is None:
                reasons.append("human approval is required")
            elif not approval.is_valid_for(intent.id, now):
                reasons.append("human approval is missing, expired, or for another order")
            elif not approval.production_acknowledged:
                reasons.append("production approval acknowledgement is required")

        order_notional = intent.notional(market) if market.price > 0 else 0.0

        if order_notional > policy.max_order_notional:
            reasons.append("order notional exceeds max order limit")

        if intent.side == OrderSide.BUY and not policy.allow_margin and order_notional > portfolio.cash:
            reasons.append("order exceeds available cash and margin is disabled")

        if intent.uses_margin:
            if not policy.allow_margin:
                reasons.append("margin trading is not enabled")
            if policy.permission_level < TradingPermissionLevel.LIVE_MARGIN_AND_SHORT:
                reasons.append("permission level is below live margin and short selling")

        if intent.leverage_multiplier > 1.0:
            if not policy.allow_leverage:
                reasons.append("leverage is not enabled")
            if policy.permission_level < TradingPermissionLevel.LIVE_MARGIN_AND_SHORT:
                reasons.append("permission level is below live margin and short selling")
            if intent.leverage_multiplier > policy.max_leverage_multiplier:
                reasons.append("leverage multiplier exceeds configured limit")

        if intent.order_type in COMPLEX_ORDER_TYPES:
            if not policy.allow_complex_orders:
                reasons.append("complex order types are not enabled")
            if policy.permission_level < TradingPermissionLevel.COMPLEX_ORDERS:
                reasons.append("permission level is below complex orders")

        if intent.is_autonomous:
            if not policy.allow_autonomous_trading:
                reasons.append("autonomous trading is not enabled")
            if policy.permission_level < TradingPermissionLevel.AUTONOMOUS_TRADING:
                reasons.append("permission level is below autonomous trading")

        current_position = portfolio.position_for(intent.symbol)
        current_symbol_exposure = abs(current_position.market_value) if current_position else 0.0

        if intent.side == OrderSide.SELL:
            held_quantity = current_position.quantity if current_position else 0.0
            if intent.quantity > held_quantity:
                if not policy.allow_short_selling:
                    reasons.append("sell order would create a short position")
                if policy.permission_level < TradingPermissionLevel.LIVE_MARGIN_AND_SHORT:
                    reasons.append("permission level is below live margin and short selling")

        post_symbol_exposure = self._post_symbol_exposure(
            current_exposure=current_symbol_exposure,
            order_notional=order_notional,
            side=intent.side,
        )
        post_sector_exposure = self._post_sector_exposure(
            portfolio=portfolio,
            market=market,
            current_symbol_exposure=current_symbol_exposure,
            post_symbol_exposure=post_symbol_exposure,
        )
        post_gross_exposure = self._post_gross_exposure(
            portfolio=portfolio,
            current_symbol_exposure=current_symbol_exposure,
            post_symbol_exposure=post_symbol_exposure,
        )

        if portfolio.equity <= 0:
            reasons.append("portfolio equity must be greater than zero")
        else:
            if post_symbol_exposure / portfolio.equity > policy.max_single_asset_exposure_percent:
                reasons.append("single-asset exposure would exceed limit")

            if post_sector_exposure / portfolio.equity > policy.max_sector_exposure_percent:
                reasons.append("sector exposure would exceed limit")

            if post_gross_exposure / portfolio.equity > policy.max_gross_exposure_percent:
                reasons.append("gross exposure would exceed limit")

            if portfolio.realized_loss_today / portfolio.equity > policy.max_daily_loss_percent:
                reasons.append("daily loss limit is breached")

            if portfolio.realized_loss_this_week / portfolio.equity > policy.max_weekly_loss_percent:
                reasons.append("weekly loss limit is breached")

            if portfolio.drawdown_percent > policy.max_drawdown_percent:
                reasons.append("portfolio drawdown limit is breached")

        if market.average_daily_dollar_volume > 0:
            participation = order_notional / market.average_daily_dollar_volume
            if participation > policy.max_adv_participation_percent:
                reasons.append("order participation would exceed ADV limit")

        if order_notional > 0 and order_notional < 10:
            warnings.append("order notional is very small")

        decision = RiskDecision.BLOCKED if reasons else RiskDecision.APPROVED
        return RiskCheckResult(
            decision=decision,
            reasons=tuple(reasons),
            warnings=tuple(warnings),
            order_notional=order_notional,
            post_trade_gross_exposure=post_gross_exposure,
            post_trade_symbol_exposure=post_symbol_exposure,
            post_trade_sector_exposure=post_sector_exposure,
        )

    @staticmethod
    def _post_symbol_exposure(
        current_exposure: float,
        order_notional: float,
        side: OrderSide,
    ) -> float:
        if side == OrderSide.BUY:
            return current_exposure + order_notional
        return max(0.0, current_exposure - order_notional)

    @staticmethod
    def _post_sector_exposure(
        portfolio: PortfolioState,
        market: MarketSnapshot,
        current_symbol_exposure: float,
        post_symbol_exposure: float,
    ) -> float:
        current_sector_exposure = portfolio.sector_exposure(market.sector)
        return current_sector_exposure - current_symbol_exposure + post_symbol_exposure

    @staticmethod
    def _post_gross_exposure(
        portfolio: PortfolioState,
        current_symbol_exposure: float,
        post_symbol_exposure: float,
    ) -> float:
        return portfolio.gross_exposure - current_symbol_exposure + post_symbol_exposure

    @staticmethod
    def _required_permission(asset_class: AssetClass) -> TradingPermissionLevel:
        match asset_class:
            case AssetClass.EQUITY | AssetClass.ETF:
                return TradingPermissionLevel.LIVE_CASH_EQUITIES
            case AssetClass.OPTION:
                return TradingPermissionLevel.LIVE_OPTIONS
            case AssetClass.FUTURE:
                return TradingPermissionLevel.LIVE_FUTURES
            case AssetClass.CRYPTO:
                return TradingPermissionLevel.LIVE_CRYPTO

    @staticmethod
    def _check_asset_module_permissions(
        intent: OrderIntent,
        policy: RiskPolicy,
        reasons: list[str],
    ) -> None:
        if intent.asset_class == AssetClass.OPTION and not policy.allow_options:
            reasons.append("options trading is not enabled")

        if intent.asset_class == AssetClass.FUTURE and not policy.allow_futures:
            reasons.append("futures trading is not enabled")

        if intent.asset_class == AssetClass.CRYPTO and not policy.allow_crypto:
            reasons.append("crypto trading is not enabled")

    @staticmethod
    def _check_live_order_fields(intent: OrderIntent, reasons: list[str]) -> None:
        if intent.estimated_fees < 0:
            reasons.append("estimated fees cannot be negative")

        if intent.expected_max_loss is None or intent.expected_max_loss <= 0:
            reasons.append("expected maximum loss is required")

        if intent.stop_loss_price is None and not intent.invalidation_condition.strip():
            reasons.append("stop-loss or invalidation condition is required")

        if not intent.reason.strip():
            reasons.append("reason for trade is required")

        if not intent.data_sources_used:
            reasons.append("data sources used are required")
