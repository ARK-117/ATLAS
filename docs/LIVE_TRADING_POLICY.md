# ATLAS Live Trading Capability Policy

ATLAS is being designed as a live-capable research and trading system. Therefore, live trading features are not permanently disabled. Instead, they are controlled by strict production permissions, risk limits, broker approvals, and human confirmation.

ATLAS supports the following trading capabilities as separate permissioned modules:

- Live stock and ETF orders.
- Margin trading.
- Leverage.
- Short selling.
- Options trading.
- Futures trading.
- Crypto trading.
- Complex order types.
- Broker execution through approved APIs.

However, these features must not be available in the default development mode.

Default mode remains:

- Research.
- Analysis.
- Watchlists.
- Backtesting.
- Paper trading.
- Risk simulation.
- Portfolio monitoring.
- Report generation.

Live trading features become available only when ATLAS is running in Live Production Mode.

## Live Production Mode

Live Production Mode is the only mode where ATLAS may create real broker order intents.

To enable Live Production Mode, the system must have:

- A real broker API connection.
- Separate paper and live API keys.
- Secure secrets management.
- User authentication.
- Role-based permissions.
- Audit logging.
- Risk engine.
- Approval workflow.
- Emergency kill switch.
- Data freshness checks.
- Broker status checks.
- Order validation.
- Position sizing rules.
- Daily loss limits.
- Portfolio exposure limits.
- Human approval for sensitive actions.

The LLM must never directly place orders.
The LLM may only generate analysis, explanations, and proposed order intents.

The execution gateway is the only service allowed to send orders to the broker.

## Permission Levels

ATLAS should use trading permission levels.

| Level | Name | Capability |
| --- | --- | --- |
| L0 | Research Mode | Research, summaries, reports, watchlists |
| L1 | Backtest Mode | Historical testing only |
| L2 | Paper Trading Mode | Simulated orders only |
| L3 | Live Cash Equities | Real stock and ETF orders |
| L4 | Live Margin and Short Selling | Margin, leverage, short selling |
| L5 | Live Options | Options strategies |
| L6 | Live Futures | Futures contracts |
| L7 | Live Crypto | Crypto spot or derivatives, depending on broker support |
| L8 | Complex Orders | Bracket orders, OCO, trailing stops, multi-leg orders |
| L9 | Autonomous Trading | AI can submit live orders under strict limits |
| L10 | Cash Movement | Withdrawals, deposits, bank changes |

Recommended rule:

- L0-L2 are safe development modes.
- L3 can be enabled after the live broker system, risk engine, and approval system are complete.
- L4-L8 require separate broker approval and separate risk models.
- L9 should not be enabled until ATLAS has a long verified record in paper and supervised live trading.
- L10 should not be controlled by the AI.

## Live Orders

Live orders are allowed only when:

- Live Production Mode is active.
- Broker credentials are loaded from a secure secret manager.
- Market data is fresh.
- Broker API status is healthy.
- User has permission.
- Risk engine approves.
- Compliance checks pass.
- The order is within portfolio limits.
- The order is not duplicated.
- Human approval is recorded unless autonomous mode is explicitly enabled.

Every live order must include:

- Symbol.
- Asset type.
- Side.
- Quantity.
- Order type.
- Time in force.
- Estimated notional value.
- Estimated fees.
- Expected maximum loss.
- Stop-loss or invalidation condition.
- Reason for trade.
- Data sources used.
- Risk approval result.
- User approval record.
- Audit event ID.

## Margin and Leverage

Margin and leverage are supported only as separate high-risk modules.

Before margin or leverage is enabled, ATLAS must check:

- Broker margin approval.
- Account equity.
- Buying power.
- Maintenance margin.
- House margin requirements.
- Concentration risk.
- Volatility risk.
- Liquidation risk.
- Interest cost.
- Maximum leverage limit.
- Daily loss limit.
- Emergency liquidation rules.

ATLAS must never use maximum available buying power automatically.

Leverage must be capped by configuration.

Example rule:

- Default leverage: 1x.
- Conservative maximum: 1.2x to 1.5x.
- Aggressive maximum: requires manual approval.
- Emergency deleveraging: triggered if drawdown, volatility, or margin usage exceeds limits.

## Short Selling

Short selling is supported only when the broker account is approved for it.

Before a short order is allowed, ATLAS must check:

- Borrow availability.
- Borrow cost.
- Short interest.
- Days to cover.
- Short squeeze risk.
- News risk.
- Volatility risk.
- Hard-to-borrow status.
- Recall risk.
- Maximum loss scenario.
- Stop-loss level.
- Position size limit.
- Margin requirement.
- Human approval.

ATLAS must clearly label short selling as high risk because losses can exceed the original trade size if the asset price rises sharply.

Naked short selling, market manipulation, coordinated short attacks, fake news, rumor-based shorting, or abusive trading behavior must be blocked.

## Options Trading

Options are supported only through a separate options module.

Before options trading is enabled, ATLAS must check:

- Broker options approval level.
- Strategy type.
- Expiration date.
- Strike price.
- Premium.
- Implied volatility.
- Greeks.
- Liquidity.
- Bid-ask spread.
- Assignment risk.
- Exercise risk.
- Maximum loss.
- Maximum profit.
- Break-even price.
- Margin requirement.
- Event risk.
- Earnings risk.
- Human approval.

Options strategies must be separated by risk level:

- Level 1: Covered calls and cash-secured puts.
- Level 2: Long calls and long puts.
- Level 3: Defined-risk spreads.
- Level 4: Multi-leg strategies.
- Level 5: Naked options.

ATLAS should block naked options by default.

Zero-day-to-expiration options should be blocked by default unless a special high-risk permission is enabled.

## Futures Trading

Futures are supported only through a futures module.

Before futures trading is enabled, ATLAS must check:

- Broker futures approval.
- Contract specification.
- Tick size.
- Tick value.
- Expiration date.
- Rollover schedule.
- Initial margin.
- Maintenance margin.
- Overnight margin.
- Intraday margin.
- Liquidity.
- Spread.
- Volatility.
- Maximum loss scenario.
- Stop-loss rule.
- Event calendar.
- Human approval.

Futures must not be traded by a generic stock strategy.

Each futures market needs its own risk rules.

## Crypto Trading

Crypto is supported only through a crypto module.

Before crypto trading is enabled, ATLAS must check:

- Jurisdiction rules.
- Broker or exchange approval.
- Custody risk.
- Exchange risk.
- Stablecoin risk.
- Liquidity.
- Spread.
- Volatility.
- 24/7 monitoring.
- Cybersecurity risk.
- Wallet permissions.
- Withdrawal restrictions.
- Human approval.

ATLAS may trade crypto only through approved APIs.

ATLAS must not move crypto to external wallets without separate human-controlled security approval.

## Complex Orders

Complex orders are supported only when the broker supports them and the risk engine understands them.

Supported complex orders may include:

- Stop-loss orders.
- Take-profit orders.
- Bracket orders.
- OCO orders.
- Trailing stops.
- Conditional orders.
- Multi-leg options orders.

Before a complex order is submitted, ATLAS must validate:

- Trigger logic.
- Execution order.
- Maximum loss.
- Partial-fill behavior.
- Cancellation behavior.
- Broker compatibility.
- Market hours behavior.
- Gap risk.
- Slippage risk.
- Duplicate order risk.

Complex orders must be simulated before live use.

## Cash Movement Rule

ATLAS must not control withdrawals, deposits, bank account changes, or cash transfers.

ATLAS may:

- Read account balance.
- Read buying power.
- Read cash available.
- Warn about low cash.
- Warn about margin usage.
- Create a funding reminder.

ATLAS must not:

- Withdraw funds.
- Deposit funds.
- Change bank details.
- Transfer cash.
- Move crypto to external wallets.
- Change account ownership details.

Cash movement should remain manually controlled by the account owner through the broker's official interface.

## Human Approval Rule

For live trading, ATLAS must require human approval for:

- First live order of the day.
- Any order above size limit.
- Any margin trade.
- Any leveraged trade.
- Any short sale.
- Any options trade.
- Any futures trade.
- Any crypto trade.
- Any complex order.
- Any trade during high volatility.
- Any trade near earnings.
- Any trade after a major news event.
- Any trade that increases drawdown risk.
- Any change to risk settings.

Autonomous trading may only be enabled after long-term supervised performance, strict risk caps, and explicit production approval.

## Final Live Trading Rule

ATLAS is allowed to trade live only inside a controlled production environment.

ATLAS must never behave like a gambling bot, hype bot, or blind auto-trader.

The final rule is:

> ATLAS may execute live trades only when permission, data quality, risk controls, compliance checks, broker status, audit logging, and human approval all pass.

