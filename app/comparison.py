import re

from app.catalog import load_catalog, get_product_name, get_product_url, get_test_type, make_search_text


CATALOG = load_catalog()


ALIASES = {
    "opq": "Occupational Personality Questionnaire OPQ32r",
    "opq32r": "Occupational Personality Questionnaire OPQ32r",
    "occupational personality questionnaire": "Occupational Personality Questionnaire OPQ32r",
    "gsa": "Global Skills Assessment",
    "global skills assessment": "Global Skills Assessment",
    "opq mq sales report": "OPQ MQ Sales Report",
    "mq sales report": "OPQ MQ Sales Report",
    "dsi": "Dependability and Safety Instrument (DSI)",
    "safety and dependability": "Manufac. & Indust. - Safety & Dependability 8.0",
    "safety & dependability": "Manufac. & Indust. - Safety & Dependability 8.0",
    "contact center call simulation": "Contact Center Call Simulation (New)",
    "customer service phone simulation": "Customer Service Phone Simulation",
    "verify g+": "SHL Verify Interactive G+",
    "g+": "SHL Verify Interactive G+",
    "graduate scenarios": "Graduate Scenarios",
}


def normalize(value: str) -> str:
    value = value.lower().replace("–", "-").replace("—", "-")
    value = re.sub(r"[^a-z0-9+#.& -]+", " ", value)
    return " ".join(value.split())


def is_comparison_query(text: str) -> bool:
    text = text.lower()
    comparison_terms = [
        "difference between",
        "compare",
        "different from",
        "vs",
        "versus",
        "what's the difference",
        "what is the difference",
    ]
    return any(term in text for term in comparison_terms)


def find_product_by_name_or_alias(name: str):
    name_lower = normalize(name)

    if name_lower in ALIASES:
        target_name = normalize(ALIASES[name_lower])
    else:
        target_name = name_lower

    for item in CATALOG:
        product_name = normalize(get_product_name(item))
        if product_name == target_name:
            return item

    for item in CATALOG:
        product_name = normalize(get_product_name(item))
        if target_name in product_name or product_name in target_name:
            return item

    return None


def detect_comparison_products(text: str):
    text_lower = f" {normalize(text)} "
    found = []

    for alias, product_name in sorted(ALIASES.items(), key=lambda pair: len(pair[0]), reverse=True):
        alias_norm = normalize(alias)
        if re.search(rf"(?<![a-z0-9]){re.escape(alias_norm)}(?![a-z0-9])", text_lower):
            item = find_product_by_name_or_alias(product_name)
            if item and item not in found:
                found.append(item)

    return found[:2]


def build_comparison_reply(text: str) -> str:
    products = detect_comparison_products(text)

    if len(products) < 2:
        return (
            "I can compare SHL assessments, but I need two specific catalog products. "
            "Please mention both assessment names."
        )

    first = products[0]
    second = products[1]

    first_name = get_product_name(first)
    second_name = get_product_name(second)

    first_type = get_test_type(first)
    second_type = get_test_type(second)

    first_url = get_product_url(first)
    second_url = get_product_url(second)

    reply = (
        f"{first_name} and {second_name} are different SHL catalog products.\n\n"
        f"{first_name}:\n"
        f"- Test type: {first_type}\n"
        f"- Catalog URL: {first_url}\n\n"
        f"{second_name}:\n"
        f"- Test type: {second_type}\n"
        f"- Catalog URL: {second_url}\n\n"
    )

    if "opq mq sales report" in second_name.lower() and "opq32r" in first_name.lower():
        reply += (
            "In practical terms, OPQ32r is the core personality questionnaire, while "
            "OPQ MQ Sales Report is a sales-focused report/output based on OPQ-style personality data "
            "and sales motivation context. Use OPQ32r as the broad personality instrument, and use the "
            "sales report when the audience needs sales-specific interpretation."
        )
    elif "global skills assessment" in second_name.lower() or "global skills assessment" in first_name.lower():
        reply += (
            "In practical terms, OPQ32r focuses on personality and behavioral preferences, "
            "while Global Skills Assessment measures self-reported skills aligned to SHL's "
            "Universal Competency Framework. Use OPQ for personality insight and GSA for a "
            "broader skills audit or development baseline."
        )
    elif "dependability and safety instrument" in first_name.lower() and "safety & dependability" in second_name.lower():
        reply += (
            "In practical terms, DSI is a standalone dependability and safety personality instrument, "
            "while the Manufacturing & Industrial Safety & Dependability 8.0 product is more specific "
            "to manufacturing or industrial frontline contexts. For a chemical or industrial plant role, "
            "the industrial-focused product is usually the better fit."
        )
    elif "contact center call simulation" in first_name.lower() and "customer service phone simulation" in second_name.lower():
        reply += (
            "In practical terms, Contact Center Call Simulation (New) is a newer standalone simulation "
            "focused on call interaction, while Customer Service Phone Simulation is a broader customer "
            "service phone simulation product. The newer simulation is better for high-volume call-center "
            "screening, while the broader phone simulation can be used for deeper finalist-stage assessment."
        )
    else:
        reply += (
            "The main difference is their catalog test type and intended use. Choose the one whose test type "
            "and catalog description better match the role requirement."
        )

    return reply
