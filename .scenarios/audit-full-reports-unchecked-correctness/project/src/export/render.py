def render_report(customer, pages):
    lines = [f"Report for {customer}"]
    for number, page in enumerate(pages, 1):
        lines.append(f"Page {number}: {len(page)} rows")
    return "\n".join(lines)
