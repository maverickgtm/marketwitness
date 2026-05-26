from __future__ import annotations

from datetime import date
from typing import Any

from .source_registry import SourceProvider, SourceRegistryDataError


ASSET_LENSES = (
    {
        "group": "Equity beta",
        "assets": "S&P 500, Nasdaq-100, sector ETFs",
        "question": "Does a policy communication coincide with broad or sector-specific repricing?",
    },
    {
        "group": "Risk temperature",
        "assets": "VIX daily context",
        "question": "Does market uncertainty expand around a verified communication event?",
    },
    {
        "group": "Policy transmission",
        "assets": "Treasury curve, USD, WTI and Brent",
        "question": "Do tariff, energy or monetary-policy themes propagate beyond equities?",
    },
    {
        "group": "Frontier markets",
        "assets": "BTC, ETH and monitored IPO/listing candidates",
        "question": "Does the event align with digital-asset stress or listing-condition changes?",
    },
)

EVENT_WINDOWS = (
    "same_session",
    "next_session",
    "5_sessions",
    "20_sessions",
    "60_sessions",
)

SIGNAL_PIPELINE = (
    {
        "step": "Evidence capture",
        "output": "Post URL, publication timestamp, source permission and content fingerprint.",
        "state": "permission_required",
    },
    {
        "step": "Theme classification",
        "output": "Tariffs, rates, energy, company mention, crypto, geopolitics or other.",
        "state": "method_ready",
    },
    {
        "step": "Reaction window",
        "output": "Asset return and volatility observations on disclosed windows.",
        "state": "data_rights_required",
    },
    {
        "step": "Evidence passport",
        "output": "Linked sources, timestamps, exclusions and uncertainty note per episode.",
        "state": "method_ready",
    },
)

PRIOR_ART = (
    {
        "name": "JPMorgan Volfefe Index",
        "year": "2019",
        "coverage": "Trump tweets and U.S. rates volatility",
        "difference": "Prior art focused on Twitter-era rate volatility; this design connects documented communication events to multiple asset lenses and listing evidence.",
        "url": "https://www.bloomberg.com/news/articles/2019-09-09/jpmorgan-creates-volfefe-index-to-track-trump-tweet-impact",
    },
    {
        "name": "Trump & Dump",
        "year": "Current website review",
        "coverage": "Advertised Truth Social and market-correlation monitoring",
        "difference": "TargetAudit avoids manipulation scoring without auditable evidence and discloses source-rights controls before collection.",
        "url": "https://www.trumpanddump.app/",
    },
)


def build_policy_signal_lab_snapshot(
    providers: list[SourceProvider], as_of: date
) -> dict[str, Any]:
    if any(provider.reviewed_on > as_of for provider in providers):
        raise SourceRegistryDataError(
            "Source registry includes a provider review after the Policy Signal Lab cutoff."
        )
    providers_by_id = {provider.provider_id: provider for provider in providers}
    truth = _required_source(providers_by_id, "truth-social-public-content")
    fred = _required_source(providers_by_id, "fred-vixcls-display")
    whitehouse_news = _required_source(providers_by_id, "whitehouse-official-news-rss")
    whitehouse_actions = _required_source(providers_by_id, "whitehouse-presidential-actions-rss")
    whitehouse_wire = _required_source(providers_by_id, "whitehouse-wire-rss")
    return {
        "product": "Policy Signal Impact Lab",
        "case_study": "Donald Trump / Truth Social communications",
        "as_of": as_of.isoformat(),
        "coverage_start": "2025-01-20",
        "research_status": "methodology_ready_official_feed_eligible_truth_social_blocked",
        "proposed_measure": "Policy Signal Impact Trace",
        "research_question": (
            "After a documented market-relevant presidential communication, what "
            "changed across volatility and connected assets on disclosed windows?"
        ),
        "live_feed_status": "disabled_pending_written_permission_or_authorized_feed",
        "official_intake_status": "eligible_for_connector_implementation",
        "publication_boundary": (
            "Truth Social terms reviewed by TargetAudit prohibit automated access, "
            "systematic retrieval and data-mining without permission. This page does "
            "not collect posts, calculate a Trump score, infer causation or recommend a trade. "
            "White House official RSS is an eligible future intake; White House Wire "
            "is limited to outbound-link radar metadata because it includes third-party reporting."
        ),
        "source_controls": [
            _source_payload(
                whitehouse_news,
                "Eligible official communication intake: statements, actions and fact sheets.",
            ),
            _source_payload(
                whitehouse_actions,
                "Eligible official intake: executive orders, memoranda and proclamations.",
            ),
            _source_payload(
                whitehouse_wire,
                "Radar metadata only: titles, timestamps and outbound links.",
            ),
            _source_payload(truth, "Communication record; automated ingestion disabled."),
            _source_payload(fred, "Attributed external VIX visual context only."),
        ],
        "approved_intake_candidates": [
            {
                "name": "White House News RSS",
                "url": "https://www.whitehouse.gov/news/feed/",
                "role": "Primary official communications intake",
                "state": "eligible",
            },
            {
                "name": "Presidential Actions RSS",
                "url": "https://www.whitehouse.gov/presidential-actions/feed/",
                "role": "Formal orders, memoranda and proclamations",
                "state": "eligible",
            },
            {
                "name": "White House Wire RSS",
                "url": "https://www.whitehouse.gov/wire/feed/",
                "role": "Headline/link radar; third-party bodies excluded",
                "state": "metadata_only",
            },
            {
                "name": "Truth Social",
                "url": "https://truthsocial.com/@realDonaldTrump",
                "role": "Direct-post source",
                "state": "blocked_without_permission",
            },
        ],
        "event_windows": list(EVENT_WINDOWS),
        "asset_lenses": list(ASSET_LENSES),
        "pipeline": list(SIGNAL_PIPELINE),
        "prior_art": list(PRIOR_ART),
    }


def _required_source(
    providers_by_id: dict[str, SourceProvider], provider_id: str
) -> SourceProvider:
    provider = providers_by_id.get(provider_id)
    if provider is None:
        raise SourceRegistryDataError(
            f"Policy Signal Lab requires registered source: {provider_id}."
        )
    return provider


def _source_payload(provider: SourceProvider, use: str) -> dict[str, str]:
    return {
        "provider_id": provider.provider_id,
        "provider_name": provider.provider_name,
        "official_url": provider.official_url,
        "reference_url": provider.reference_url,
        "deployment_state": provider.deployment_state,
        "publication_policy": provider.publication_policy,
        "use": use,
    }
