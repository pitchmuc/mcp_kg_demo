"""Tests for contact MCP tools."""

import pytest

from kg_mcp_server.tools.contacts import get_contact, list_contacts_for_account, search_contacts


@pytest.mark.asyncio
async def test_list_contacts_for_account_by_id() -> None:
    result = await list_contacts_for_account("acct-cindralogic")
    assert "Found 4 contact(s)" in result
    assert "Elif Yavuz" in result


@pytest.mark.asyncio
async def test_list_contacts_for_account_by_name_and_role() -> None:
    result = await list_contacts_for_account("Cindra Logic", role="Champion")
    assert "Farid Abbas" in result
    assert "Elif Yavuz" not in result


@pytest.mark.asyncio
async def test_search_contacts_by_job_title() -> None:
    result = await search_contacts("Chief")
    assert "Adriana Koll" in result
    assert "Elif Yavuz" in result


@pytest.mark.asyncio
async def test_get_contact_by_id() -> None:
    result = await get_contact("contact-adriana-koll")
    assert "Adriana Koll" in result
    assert "AtlasForge Manufacturing" in result


@pytest.mark.asyncio
async def test_get_contact_by_name_substring() -> None:
    result = await get_contact("O'Connor")
    assert "Liam O'Connor" in result


@pytest.mark.asyncio
async def test_get_contact_not_found() -> None:
    result = await get_contact("nobody-here")
    assert "No contact found" in result
