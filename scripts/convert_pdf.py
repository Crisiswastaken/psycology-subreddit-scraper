import json
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from pathlib import Path

def json_to_pdf(json_path, output_path="output.pdf"):
    json_path = Path(json_path)
    output_path = Path(output_path)

    # --- Load JSON or JSONL ---
    with open(json_path, "r", encoding="utf-8") as f:
        first_char = f.read(1)
        f.seek(0)
        if first_char == "[":
            data = json.load(f)
        else:
            data = [json.loads(line) for line in f]

    # --- Create PDF doc ---
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72
    )
    styles = getSampleStyleSheet()
    story = []

    # Custom styles
    title_style = ParagraphStyle(
        'PostTitle', parent=styles['Heading2'], spaceAfter=6, leading=16
    )
    body_style = ParagraphStyle(
        'PostBody', parent=styles['BodyText'], spaceAfter=18, leading=14
    )
    meta_style = ParagraphStyle(
        'Meta', parent=styles['Normal'], fontSize=8, textColor="gray", spaceAfter=12
    )

    # --- Add each post ---
    for i, item in enumerate(data, start=1):
        title = item.get("title", "(No title)")
        body = item.get("body", "")
        subreddit = item.get("subreddit", "Unknown")

        story.append(Paragraph(f"Post {i}: {title}", title_style))
        story.append(Paragraph(body.replace("\n", "<br/>"), body_style))
        story.append(Paragraph(f"Subreddit: r/{subreddit}", meta_style))
        story.append(Spacer(1, 0.2 * inch))

    # --- Build PDF ---
    doc.build(story)
    print(f"✅ PDF created: {output_path.absolute()}")

if __name__ == "__main__":
    # example usage
    json_to_pdf("compiled_clean.jsonl", "compiled_posts.pdf")
