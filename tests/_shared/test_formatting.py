"""Testes dos helpers de formatação."""

from mcp_brasil._shared.formatting import (
    format_brl,
    format_number_br,
    format_percent,
    markdown_table,
    truncate_list,
)


class TestMarkdownTable:
    def test_basic_table(self) -> None:
        result = markdown_table(["Nome", "UF"], [["São Paulo", "SP"], ["Bahia", "BA"]])
        assert "| Nome | UF |" in result
        assert "| São Paulo | SP |" in result
        assert "| --- | --- |" in result

    def test_empty_rows(self) -> None:
        result = markdown_table(["A"], [])
        assert result == "Nenhum resultado encontrado."

    def test_single_column(self) -> None:
        result = markdown_table(["Estado"], [["SP"], ["RJ"]])
        assert "| Estado |" in result


class TestFormatBrl:
    def test_simple_value(self) -> None:
        assert format_brl(1234.56) == "R$ 1.234,56"

    def test_zero(self) -> None:
        assert format_brl(0) == "R$ 0,00"

    def test_millions(self) -> None:
        assert format_brl(1_500_000.99) == "R$ 1.500.000,99"

    def test_negative(self) -> None:
        assert format_brl(-42.5) == "R$ -42,50"


class TestFormatNumberBr:
    def test_default_decimals(self) -> None:
        assert format_number_br(1234.5) == "1.234,50"

    def test_zero_decimals(self) -> None:
        assert format_number_br(1234.5, decimals=0) == "1.234"

    def test_four_decimals(self) -> None:
        assert format_number_br(3.14159, decimals=4) == "3,1416"


class TestFormatPercent:
    def test_basic(self) -> None:
        assert format_percent(0.05) == "5,00%"

    def test_zero(self) -> None:
        assert format_percent(0) == "0,00%"

    def test_custom_decimals(self) -> None:
        assert format_percent(0.1234, decimals=1) == "12,3%"


class TestTruncateList:
    def test_short_list(self) -> None:
        items = ["a", "b", "c"]
        result = truncate_list(items, max_items=5)
        assert result == "a\nb\nc"

    def test_exact_limit(self) -> None:
        items = ["a", "b"]
        result = truncate_list(items, max_items=2)
        assert result == "a\nb"

    def test_truncated(self) -> None:
        items = [f"item {i}" for i in range(10)]
        result = truncate_list(items, max_items=3)
        assert "item 0" in result
        assert "item 2" in result
        assert "... e mais 7 resultados" in result
