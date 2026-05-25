from __future__ import annotations

from collections import Counter
from datetime import date
from typing import Any

from .source_registry import SourceProvider, SourceRegistryDataError


def build_public_use_policy(
    providers: list[SourceProvider], as_of: date
) -> dict[str, Any]:
    if any(provider.reviewed_on > as_of for provider in providers):
        raise SourceRegistryDataError(
            "Source registry includes a provider review after the public-use policy cutoff."
        )
    deployment = Counter(provider.deployment_state for provider in providers)
    blocked = [
        {
            "provider_id": provider.provider_id,
            "provider_name": provider.provider_name,
            "data_class": provider.data_class,
            "restriction": provider.review_note,
            "reference_url": provider.reference_url,
        }
        for provider in providers
        if provider.deployment_state == "blocked"
    ]
    return {
        "policy_version": "2026-05-25",
        "as_of": as_of.isoformat(),
        "review_status": "pending_external_legal_review",
        "headline": "Research evidence, not investment advice.",
        "summary": (
            "TargetAudit is an auditable research tool. A filing, prospectus, "
            "holding change, token observation or analyst-target score does not "
            "tell a user to buy, sell or hold a security."
        ),
        "tracked_source_count": len(providers),
        "blocked_source_count": deployment["blocked"],
        "review_required_count": (
            deployment["review_required"] + deployment["license_required"]
        ),
        "manual_only_count": deployment["manual_only"],
        "data_layers": [
            {
                "title": "Project-authored sandbox",
                "status": "redistributable_demo",
                "description": (
                    "Synthetic fixtures exercise the product and may be distributed "
                    "with the repository; their results are not real market findings."
                ),
            },
            {
                "title": "Public regulatory monitors",
                "status": "evidence_only",
                "description": (
                    "Filings, prospectuses and reported holdings identify review "
                    "events. They do not establish trading availability, valuation "
                    "or an investment position."
                ),
            },
            {
                "title": "Authorized extensions",
                "status": "permission_required",
                "description": (
                    "User-supplied targets or prices can be analyzed privately. "
                    "Public output stays disabled until appropriate rights are documented."
                ),
            },
        ],
        "publication_rules": [
            "Do not publish real analyst rankings unless every required input source is approved for public output.",
            "Do not describe regulatory evidence as a completed listing or real-time market signal without separate confirmation.",
            "Do not automatically collect, cache or republish providers marked blocked or manual only.",
            "Keep API keys, provider downloads and contact identifiers outside the public repository.",
        ],
        "operator_responsibilities": [
            "Review applicable source terms and market regulations before enabling live collection.",
            "Provide required contact identification for SEC live requests and respect access limits.",
            "Treat this policy as a product control, not as legal, tax or investment advice.",
        ],
        "blocked_sources": blocked,
    }
