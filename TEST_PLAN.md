# Test Plan — Polecat

## Requirements → tests

### project-foundation
Requirement: The application serves the actual FinAlly dashboard with the required heading, starting amount, ten specified tracked tickers, a healthy API response, and a diagnostic error when the frontend export is unavailable.
Level: integration
Test file: finally/backend/app/main_test.py
Bead ID: te-x44
Phase: project-foundation
| Level | Test file | Bead ID | Scenarios | Assertions |
|---|---|---|---|---|
| integration | finally/backend/app/main_test.py | te-x44 | GET /api/health returns 200 and decoded JSON {"status":"ok"}; GET / serves the exported dashboard with heading "FinAlly" and "$10,000"; dashboard contains exactly AAPL, GOOGL, MSFT, AMZN, TSLA, NVDA, META, JPM, V, NFLX; missing index.html returns 404 with {"detail":"Frontend export not found"} rather than fallback content. | Assert status codes and decoded JSON values/types; assert heading, amount, and all ten symbols; assert missing-export response excludes stale fallback content. |



### project-foundation-support
Requirement: Support artifacts provide environment defaults, lifecycle scripts, CI, the database mount marker, and idempotent SQLite schema initialization with the exact default profile, ten tickers, and $10,000 cash.
Level: unit
Test file: finally/backend/db/schema_test.py
Bead ID: te-s2x
Phase: project-foundation-support
| Level | Test file | Bead ID | Scenarios | Assertions |
|---|---|---|---|---|
| unit | finally/backend/db/schema_test.py | te-s2x | Initialize fresh SQLite and verify users_profile, watchlist, positions, trades, portfolio_snapshots, and chat_messages with documented columns and constraints; verify one default profile with 10000.0 cash and exactly the ten specified tickers; initialize a second time. | Schema and uniqueness constraints, seed values, and ticker set are exact; repeated initialization succeeds without duplicates and preserves one profile and one row per ticker. |

### core-market-infrastructure
Requirement: GBM and Massive providers share one interface, selection follows MASSIVE_API_KEY, the cache retains latest/previous/timestamp values, and SSE emits the specified event fields.
Level: unit
Test file: finally/backend/tests/test_market_infrastructure.py
Bead ID: pending
Phase: core-market-infrastructure
| Level | Test file | Bead ID | Scenarios | Assertions |
|---|---|---|---|---|
| unit | finally/backend/tests/test_market_infrastructure.py | pending | Generate positive GBM prices and parse Massive response into the shared provider shape; select simulator when MASSIVE_API_KEY is absent and Massive when non-empty; update cache twice and serialize SSE event with ticker, price, previous price, timestamp, and direction. | Provider outputs are interchangeable and positive; cache previous equals prior latest; SSE uses event-stream content with every required field. |

### database-portfolio-engine
Requirement: Portfolio persistence and engine support fractional market orders, validation, average cost, P&L, snapshots, watchlist data, and persistence.
Level: unit
Test file: finally/backend/app/portfolio/engine_test.py
Bead ID: pending
Phase: database-portfolio-engine
| Level | Test file | Bead ID | Scenarios | Assertions |
|---|---|---|---|---|
| unit | finally/backend/app/portfolio/engine_test.py | pending | Buy and sell fractional shares and verify cash, quantity, and weighted average cost; reject insufficient-cash buys and excessive sells without mutation; calculate current value and unrealized P&L, record immediate snapshots, and reopen database. | Balances, positions, average cost, P&L, trade history, and snapshots match documented calculations; portfolio, trade, and history routes are registered and use the engine. |

### watchlist-market-ui
Requirement: Watchlist UI renders seeded symbols and prices, consumes SSE updates, accumulates sparklines, selects charts, flashes direction, manages CRUD, and shows connection status.
Level: ui
Test file: finally/test/watchlist-market-ui.spec.ts
Bead ID: pending
Phase: watchlist-market-ui
| Level | Test file | Bead ID | Scenarios | Assertions |
|---|---|---|---|---|
| ui | finally/test/watchlist-market-ui.spec.ts | pending | Render ten seeded tickers and prices, observe SSE price update, sparkline point, and green/red flash; select tickers, add PYPL, remove a ticker, reject duplicate AAPL, and observe connection status. | Browser observes real symbols, changed prices, chart selection, sparkline elements, CRUD results, and connected/reconnecting state. |

### portfolio-visualisation-trading
Requirement: Trading UI executes market orders and displays immediate cash/position changes, validation errors, positions, P&L, heatmap, and history chart data.
Level: ui
Test file: finally/test/portfolio-visualisation-trading.spec.ts
Bead ID: pending
Phase: portfolio-visualisation-trading
| Level | Test file | Bead ID | Scenarios | Assertions |
|---|---|---|---|---|
| ui | finally/test/portfolio-visualisation-trading.spec.ts | pending | Buy and sell AAPL shares, then verify immediate cash and position changes; reject insufficient-cash and excessive-sell orders without changing state; render positions, P&L, heatmap rectangles with P&L colors, and history chart data. | Successful and rejected trade values match API results; visualizations contain resulting portfolio data. |

### ai-trading-assistant
Requirement: Chat returns validated structured actions, supports deterministic mock mode, persists messages, executes valid actions, rejects invalid actions, and recovers from provider errors.
Level: integration
Test file: finally/backend/tests/test_chat.py
Bead ID: pending
Phase: ai-trading-assistant
| Level | Test file | Bead ID | Scenarios | Assertions |
|---|---|---|---|---|
| integration | finally/backend/tests/test_chat.py | pending | POST /api/chat returns message, trades, and watchlist_changes with documented types; identical LLM_MOCK requests produce equal decoded JSON; valid actions persist and use engine validation; malformed/provider failures return usable error without corrupting state, with ChatAssistant.test.tsx covering loading and inline confirmations. | Response keys/types, persistence, deterministic mock output, valid changes, and unchanged state after rejected actions are verified. |

### application-polish
Requirement: Polish provides the dark terminal palette, responsive layout, animations, loading/error/empty states, accessible labels, notifications, and stable streaming.
Level: ui
Test file: finally/test/application-polish.spec.ts
Bead ID: pending
Phase: application-polish
| Level | Test file | Bead ID | Scenarios | Assertions |
|---|---|---|---|---|
| ui | finally/test/application-polish.spec.ts | pending | Check dark palette, responsive layout, price transitions, loading indicators, and stable streaming; exercise empty, error, notification, and accessible-control states. | Computed styles match specified palette and real dashboard remains visible; state text/styles and accessible names communicate loading, errors, empty results, notifications, and outcomes. |

### testing-release
Requirement: Dockerized Playwright release testing runs with LLM_MOCK=true, healthcheck, real-content assertions, and complete end-to-end coverage.
Level: integration
Test file: finally/test/e2e.spec.ts
Bead ID: pending
Phase: testing-release
| Level | Test file | Bead ID | Scenarios | Assertions |
|---|---|---|---|---|
| integration | finally/test/e2e.spec.ts | pending | Compose builds and starts app with LLM_MOCK=true, healthchecks /api/health, and runs Playwright with declared Chromium project; fresh dashboard covers heading, ten tickers, prices, connection status, and $10,000; browser flows cover watchlist CRUD, streaming/reconnection, navigation, trading validation, portfolio visualizations, chat actions, and happy path. | Tests assert real content and changed values rather than status/placeholders; Compose preserves Playwright failure status and cleans up resources. |
