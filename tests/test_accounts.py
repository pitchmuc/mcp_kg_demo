"""Tests for account MCP tools."""

import pytest

from kg_mcp_server.tools.accounts import get_account, list_accounts, search_accounts


@pytest.mark.asyncio
async def test_list_accounts_no_filter_returns_all() -> None:
    result = await list_accounts()
    assert "Found 8 account(s)" in result
    assert "AtlasForge Manufacturing" in result


@pytest.mark.asyncio
async def test_list_accounts_filters_by_tier() -> None:
    result = await list_accounts(tier="Strategic")
    assert "AtlasForge Manufacturing" in result
    assert "Dunwich Retail Holdings" not in result


@pytest.mark.asyncio
async def test_list_accounts_filters_by_min_health_score() -> None:
    result = await list_accounts(min_health_score=90)
    assert "Cindra Logic Systems" in result
    assert "Halcyon EdTech Collective" not in result


@pytest.mark.asyncio
async def test_search_accounts_matches_industry() -> None:
    result = await search_accounts("Healthcare")
    assert "Everline Health Networks" in result


@pytest.mark.asyncio
async def test_search_accounts_empty_keyword() -> None:
    result = await search_accounts("   ")
    assert "non-empty keyword" in result


@pytest.mark.asyncio
async def test_get_account_by_local_id_includes_contacts() -> None:
    result = await get_account("acct-atlasforge")
    assert "AtlasForge Manufacturing" in result
    assert "Adriana Koll" in result
    assert "Ben Osei" in result


@pytest.mark.asyncio
async def test_get_account_by_name_substring() -> None:
    result = await get_account("Fjordwave")
    assert "FjordWave Logistics" in result


@pytest.mark.asyncio
async def test_get_account_not_found() -> None:
    result = await get_account("does-not-exist")
    assert "No account found" in result


@pytest.mark.asyncio
async def test_get_account_without_contacts() -> None:
    result = await get_account("acct-granvalley", include_contacts=False)
    assert "Contacts:" not in result
