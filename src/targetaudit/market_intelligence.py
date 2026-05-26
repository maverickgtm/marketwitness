from __future__ import annotations

from collections import Counter
from datetime import date
from typing import Any

from .source_registry import SourceProvider, SourceRegistryDataError


MODULES = (
    {
        "key": "pre_ipo_radar",
        "title": "Pre-IPO Radar",
        "theme": "Listings",
        "stage": "implemented_foundation",
        "priority": "now",
        "provider_ids": ("sec-edgar", "sec-company-map"),
        "coverage": "S-1, F-1, 424B4 and withdrawal review already routed through IPO Watch.",
        "cadence": "Daily discovery with human verification",
        "route": "/dashboard/ipo",
        "next_delivery": "Extend the review taxonomy to Form D and EFFECT milestones.",
        "claim_limit": "A filing starts verification; it does not confirm listing or a trade.",
    },
    {
        "key": "market_regimes",
        "title": "Market Regimes",
        "theme": "Digital Assets / Energy / Rates",
        "stage": "connector_planned",
        "priority": "next",
        "provider_ids": ("kraken-spot-public", "eia-open-data", "treasury-yield-curve"),
        "coverage": "BTC, ETH, WTI, Brent and U.S. Treasury 2Y/10Y context.",
        "cadence": "Mixed: public market endpoint plus official daily series",
        "route": "",
        "next_delivery": "Build normalized observations only after each output policy is accepted.",
        "claim_limit": "Regime context is not a buy, sell or position-sizing signal.",
    },
    {
        "key": "macro_calendar",
        "title": "Macro Calendar",
        "theme": "Catalysts",
        "stage": "connector_planned",
        "priority": "next",
        "provider_ids": ("fed-fomc-calendar", "bls-release-calendar"),
        "coverage": "FOMC meetings and scheduled CPI/employment publication windows.",
        "cadence": "Scheduled official calendar",
        "route": "",
        "next_delivery": "Attach upcoming official events to watched IPO and listing timelines.",
        "claim_limit": "An upcoming macro release does not determine an IPO outcome.",
    },
    {
        "key": "insider_activity",
        "title": "Insider Activity",
        "theme": "Declared Ownership",
        "stage": "connector_planned",
        "priority": "next",
        "provider_ids": ("sec-insider-transactions",),
        "coverage": "SEC Forms 3, 4 and 5 for listed companies under observation.",
        "cadence": "Regulatory filing evidence; dataset refresh cadence disclosed at ingestion",
        "route": "",
        "next_delivery": "Parse open-market purchases and sales separately from grants or awards.",
        "claim_limit": "A declared insider transaction is evidence, not investment advice.",
    },
    {
        "key": "ownership_watch",
        "title": "Ownership Watch",
        "theme": "Funds / Institutions",
        "stage": "foundation_available",
        "priority": "after_next",
        "provider_ids": ("sec-nport", "sec-edgar"),
        "coverage": "N-PORT evidence is active; 13D, 13G and 13F expansion is planned.",
        "cadence": "Periodic regulatory filings",
        "route": "/dashboard/etf",
        "next_delivery": "Add SEC beneficial-ownership and institutional filing classifications.",
        "claim_limit": "Reported holdings are delayed disclosures, not real-time flows.",
    },
    {
        "key": "futures_positioning",
        "title": "Futures Positioning",
        "theme": "Commodities / USD",
        "stage": "connector_planned",
        "priority": "after_next",
        "provider_ids": ("cftc-cot",),
        "coverage": "Managed Money and commercial positioning for energy, metals and financial futures.",
        "cadence": "Weekly CFTC report",
        "route": "",
        "next_delivery": "Publish net-position context alongside energy and dollar regimes.",
        "claim_limit": "Aggregated futures categories do not identify a profitable position.",
    },
)


def build_market_intelligence_snapshot(
    providers: list[SourceProvider], as_of: date
) -> dict[str, Any]:
    if any(provider.reviewed_on > as_of for provider in providers):
        raise SourceRegistryDataError(
            "Source registry includes a provider review after the Market Intelligence cutoff."
        )
    providers_by_id = {provider.provider_id: provider for provider in providers}
    modules = [_module_payload(item, providers_by_id) for item in MODULES]
    stages = Counter(item["stage"] for item in modules)
    return {
        "product": "Market Intelligence",
        "as_of": as_of.isoformat(),
        "module_count": len(modules),
        "foundation_count": stages["implemented_foundation"] + stages["foundation_available"],
        "planned_connector_count": stages["connector_planned"],
        "implementation_sequence": [
            "Market Regimes: BTC, ETH, WTI, Brent and Treasury 2Y/10Y.",
            "Macro Calendar and Insider Activity attached to watched companies.",
            "Ownership expansion and CFTC positioning after the first connectors are audited.",
        ],
        "publication_boundary": (
            "This workspace maps verifiable evidence and implementation order. "
            "It currently displays no newly collected live values and does not recommend positions."
        ),
        "modules": modules,
    }


def _module_payload(
    definition: dict[str, Any], providers_by_id: dict[str, SourceProvider]
) -> dict[str, Any]:
    sources = []
    for provider_id in definition["provider_ids"]:
        provider = providers_by_id.get(provider_id)
        if provider is None:
            raise SourceRegistryDataError(
                f"Market Intelligence requires registered source: {provider_id}."
            )
        sources.append(
            {
                "provider_id": provider.provider_id,
                "provider_name": provider.provider_name,
                "official_url": provider.official_url,
                "integration_status": provider.integration_status,
                "deployment_state": provider.deployment_state,
                "publication_policy": provider.publication_policy,
            }
        )
    return {
        **definition,
        "provider_ids": list(definition["provider_ids"]),
        "sources": sources,
    }
