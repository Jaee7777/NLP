"""
Webpage Analyzer - Extract patterns and classify webpages using regex
Reads from CSV file and outputs analyzed results to CSV
"""

import re
import json
import pandas as pd


# ============================================================================
# EXTRACTORS
# ============================================================================


def extract_emails(text):
    """Extract email addresses."""
    if not isinstance(text, str):
        return []
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    matches = re.findall(pattern, text)
    return list(dict.fromkeys(matches))


def extract_phones(text):
    """Extract phone numbers in various formats."""
    if not isinstance(text, str):
        return []
    phones = []

    patterns = [
        r"\b\d{3}-\d{3}-\d{4}\b",
        r"\(\d{3}\)\s*\d{3}-\d{4}",
        r"\b\d{3}\.\d{3}\.\d{4}\b",
        r"\b\d{3}\s\d{3}\s\d{4}\b",
        r"\b\d{10}\b",
        r"\+1[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
        r"\b1[-.\s]\d{3}[-.\s]\d{3}[-.\s]\d{4}\b",
        r"\b8[0-9]{2}-\d{3}-\d{4}\b",
        r"\(\d{3}\)\s*\d{3}[.\s]\d{4}",
        r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\s*(?:ext\.?|x)\s*\d{1,5}\b",
    ]

    for pattern in patterns:
        phones.extend(re.findall(pattern, text, re.IGNORECASE))

    return list(dict.fromkeys(phones))


def extract_dates(text):
    """Extract dates in various formats."""
    if not isinstance(text, str):
        return []
    dates = []

    patterns = [
        r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
        r"\b\d{4}-\d{2}-\d{2}\b",
        r"\b\d{1,2}-\d{1,2}-\d{2,4}\b",
        r"\b\d{1,2}\.\d{1,2}\.\d{2,4}\b",
        r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b",
        r"\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b",
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}\b",
        r"\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\b",
        r"\b\d{4}/\d{2}/\d{2}\b",
        r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b",
        r"\b\d{1,2}[-/]\d{4}\b",
        r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th),?\s+\d{4}\b",
        r"\b\d{1,2}(?:st|nd|rd|th)\s+(?:January|February|March|April|May|June|July|August|September|October|November|December),?\s+\d{4}\b",
    ]

    for pattern in patterns:
        dates.extend(re.findall(pattern, text, re.IGNORECASE))

    seen = set()
    unique_dates = []
    for date in dates:
        if date.lower() not in seen:
            seen.add(date.lower())
            unique_dates.append(date)

    return unique_dates


def extract_prices(text):
    """Extract prices and monetary amounts."""
    if not isinstance(text, str):
        return []
    prices = []

    patterns = [
        r"\$\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?",
        r"€\s*\d{1,3}(?:\.\d{3})*(?:,\d{2})?",
        r"€\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?",
        r"£\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?",
        r"¥\s*\d{1,3}(?:,\d{3})*",
        r"₹\s*\d{1,2}(?:,\d{2})*(?:,\d{3})(?:\.\d{2})?",
        r"\b(?:USD|EUR|GBP|JPY|CAD|AUD|CHF|CNY|INR)\s*\d{1,3}(?:[,.\s]\d{3})*(?:[.,]\d{2})?\b",
        r"\b\d{1,3}(?:[,.\s]\d{3})*(?:[.,]\d{2})?\s*(?:USD|EUR|GBP|JPY|CAD|AUD|CHF|CNY|INR)\b",
        r"-\$\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?",
        r"\(\$\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?\)",
        r"\b\d{1,2}\s*(?:cents?|¢)\b",
        r"\$\s*\d+(?:\.\d+)?\s*[KMBkmb]\b",
        r"\$\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s*[-–—]\s*\$?\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?",
        r"\b\d{1,3}(?:,\d{3})*(?:\.\d{2})?\s*(?:dollars?|euros?|pounds?|yen|yuan)\b",
    ]

    for pattern in patterns:
        prices.extend(re.findall(pattern, text, re.IGNORECASE))

    seen = set()
    unique_prices = []
    for price in prices:
        if price.lower() not in seen:
            seen.add(price.lower())
            unique_prices.append(price)

    return unique_prices


def extract_urls(text):
    """Extract URLs from text content."""
    if not isinstance(text, str):
        return []
    urls = []

    patterns = [
        r"https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)",
        r"\bwww\.[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)",
        r"ftp://[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)",
        r"file:///[-a-zA-Z0-9@:%._\+~#=/\\]+",
        r"https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?::\d{1,5})?(?:/[-a-zA-Z0-9@:%_\+.~#?&//=]*)?",
        r"https?://localhost(?::\d{1,5})?(?:/[-a-zA-Z0-9@:%_\+.~#?&//=]*)?",
        r"mailto:[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
        r"tel:[\+]?[\d\s\-()]{7,20}",
    ]

    for pattern in patterns:
        urls.extend(re.findall(pattern, text, re.IGNORECASE))

    seen = set()
    unique_urls = []
    for url in urls:
        if url.lower() not in seen:
            seen.add(url.lower())
            unique_urls.append(url)

    return unique_urls


def extract_social(text):
    """Extract social media handles and hashtags."""
    if not isinstance(text, str):
        return {"handles": [], "hashtags": []}

    pattern_handles = r"(?<![\w])@([a-zA-Z_][a-zA-Z0-9_.]{0,29})(?![\w])"
    handles = re.findall(pattern_handles, text)
    handles = ["@" + h for h in handles]

    pattern_hashtags = r"(?<![\w])#([a-zA-Z_][a-zA-Z0-9_]{0,138})(?![\w])"
    hashtags = re.findall(pattern_hashtags, text)
    hashtags = ["#" + h for h in hashtags]

    return {
        "handles": list(dict.fromkeys(handles)),
        "hashtags": list(dict.fromkeys(hashtags)),
    }


def extract_all_caps(text):
    """Extract all-caps words (minimum 2 letters)."""
    if not isinstance(text, str):
        return []
    pattern = r"\b([A-Z]{2,})\b"
    matches = re.findall(pattern, text)
    return list(dict.fromkeys(matches))


def count_question_marks(text):
    """Count question marks."""
    if not isinstance(text, str):
        return 0
    return len(re.findall(r"\?", text))


# ============================================================================
# CLASSIFIER
# ============================================================================


def classify_webpage(text, url=""):
    """Classify webpage using regex patterns. Returns single category label."""
    if not isinstance(text, str):
        text = ""
    if not isinstance(url, str):
        url = ""

    text_lower = text.lower()
    url_lower = url.lower()

    scores = {
        "news": 0,
        "blog": 0,
        "e-commerce": 0,
        "forum/discussion": 0,
        "educational": 0,
        "technical/documentation": 0,
        "government": 0,
    }

    # URL PATTERNS
    url_patterns = {
        "news": r"(news\.|/news/|\.news|headline|breaking|reuters|bbc|cnn|nytimes|guardian|washingtonpost|foxnews|nbcnews)",
        "blog": r"(blog\.|/blog/|\.blog|medium\.com|wordpress|blogger|blogspot|substack|tumblr|ghost\.io|wikidot\.com/blog)",
        "e-commerce": r"(shop\.|/shop/|/product/|/cart/|/checkout/|amazon|ebay|etsy|shopify|store\.|/buy/|/order/|\.store|walmart|alibaba)",
        "forum/discussion": r"(forum\.|/forum/|/thread/|/discussion/|reddit\.com|quora\.com|stackoverflow|discord|/community/|/topics/|discuss\.|boards\.|viewtopic\.php|/topic/)",
        "educational": r"(\.edu|/learn/|/course/|/tutorial/|coursera|udemy|edx|khanacademy|university|college|school|academy|/lesson/)",
        "technical/documentation": r"(/docs/|/documentation/|/api/|/reference/|github\.com|gitlab|readthedocs|swagger|/sdk/|/guide/|developer\.|devdocs)",
        "government": r"(\.gov|\.mil|government|/agency/|whitehouse|congress|senate|parliament|ministry|federal)",
    }

    for category, pattern in url_patterns.items():
        if re.search(pattern, url_lower):
            scores[category] += 5

    # CONTENT PATTERNS
    content_patterns = {
        "news": [
            (r"\b(breaking\s*news|headline|reporter|journalist)\b", 2),
            (r"\b(press\s*release|news\s*update|latest\s*news)\b", 2),
            (r"\b(according\s*to\s*sources|correspondent|exclusive)\b", 2),
            (r"\b(developing\s*story|associated\s*press|reuters|afp)\b", 2),
            (r"\b(reported|reporting|news\s*desk)\b", 1),
            (r"(breaking:|updated:|exclusive:)", 3),
            (
                r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{1,2},?\s+\d{4}\b",
                2,
            ),
        ],
        "blog": [
            (r"\b(posted\s*by|written\s*by|author:)\b", 2),
            (r"\b(about\s*the\s*author|read\s*more|continue\s*reading)\b", 2),
            (r"\b(blog\s*post|my\s*thoughts|in\s*this\s*post)\b", 3),
            (r"\b(subscribe|newsletter|personal\s*blog)\b", 2),
            (r"\b(i\s*think|i\s*believe|my\s*experience|my\s*journey)\b", 2),
            (r"\b(leave\s*a\s*comment|share\s*this\s*post|comments\s*section)\b", 2),
            (r"\b(opinion|reflections|musings)\b", 1),
        ],
        "e-commerce": [
            (r"\b(add\s*to\s*cart|buy\s*now|shop\s*now|order\s*now)\b", 3),
            (r"\b(price:|checkout|shipping|free\s*delivery)\b", 2),
            (r"\b(in\s*stock|out\s*of\s*stock|quantity|inventory)\b", 2),
            (r"\b(product\s*description|customer\s*reviews|ratings)\b", 2),
            (r"\b(discount|sale|coupon|promo\s*code)\b", 2),
            (r"\b(wishlist|compare|sku:|upc:)\b", 2),
            (r"[\$€£¥]\s*\d+[.,]?\d*", 1),
            (r"★{1,5}|☆{1,5}|(\d+(\.\d+)?\s*stars)", 2),
        ],
        "forum/discussion": [
            (r"\b(reply|replies|posted:|thread|topic)\b", 2),
            (r"\b(member\s*since|posts:|joined:|reputation)\b", 3),
            (r"\b(quote|quoted|forum\s*rules|moderator|admin)\b", 2),
            (r"\b(sticky|pinned|upvote|downvote|karma)\b", 2),
            (r"\b(solved|answered|discussion|community)\b", 1),
            (r"\b(members\s*online|active\s*users|views:)\b", 2),
            (r"(reply\s*#\d+|post\s*#\d+)", 3),
            (r"\b\d+\s*(replies|posts|comments|views)\b", 2),
            (r"\b(view\s*topic|post\s*reply|new\s*topic)\b", 3),
        ],
        "educational": [
            (r"\b(lesson|course|curriculum|syllabus|assignment)\b", 2),
            (r"\b(quiz|exam|test|grade|student|teacher)\b", 2),
            (r"\b(professor|lecture|learning\s*objectives|module)\b", 2),
            (r"\b(enroll|certificate|diploma|degree|academic)\b", 2),
            (r"\b(semester|tuition|scholarship|campus)\b", 2),
            (r"\b(learning|education|study|classroom)\b", 1),
            (r"(chapter\s*\d+|module\s*\d+|lesson\s*\d+|unit\s*\d+)", 3),
        ],
        "technical/documentation": [
            (r"\b(api|sdk|documentation|parameters|returns)\b", 2),
            (r"\b(example:|syntax|function|method|class)\b", 2),
            (r"\b(installation|requirements|dependencies)\b", 2),
            (r"\b(npm\s*install|pip\s*install|git\s*clone)\b", 3),
            (r"\b(import|code\s*example|endpoint)\b", 2),
            (r"\b(request|response|json|xml|deprecated)\b", 1),
            (r"\b(version:|changelog|release\s*notes)\b", 2),
            (r"(```|<code>|<pre>)", 2),
            (r"\b(def\s+\w+|function\s+\w+|class\s+\w+)\b", 2),
        ],
        "government": [
            (r"\b(official|federal|state|municipal|county)\b", 2),
            (r"\b(regulation|legislation|statute|law|policy)\b", 2),
            (r"\b(agency|department|bureau|commission|council)\b", 2),
            (r"\b(public\s*notice|government|citizen)\b", 2),
            (r"\b(tax|permit|license|compliance|jurisdiction)\b", 2),
            (r"\b(authority|ordinance|amendment|act\s*of)\b", 2),
            (r"(\d+\s*u\.?s\.?c\.?\s*§?\s*\d+)", 3),
            (r"\b(effective\s*date|pursuant\s*to|hereby)\b", 2),
        ],
    }

    for category, patterns in content_patterns.items():
        for pattern, weight in patterns:
            matches = re.findall(pattern, text_lower)
            scores[category] += len(matches) * weight

    # STRUCTURAL PATTERNS
    price_count = len(re.findall(r"[\$€£¥]\s*\d+[.,]?\d*", text))
    if price_count >= 3:
        scores["e-commerce"] += price_count * 2

    question_count = len(re.findall(r"\?", text))
    if question_count >= 5:
        scores["forum/discussion"] += question_count
        scores["educational"] += question_count // 2

    code_count = len(re.findall(r"```|<code>|<pre>", text_lower))
    if code_count >= 2:
        scores["technical/documentation"] += code_count * 3

    reply_count = len(
        re.findall(r"(reply\s*#?\d*|post\s*#?\d*|@\w+\s*said)", text_lower)
    )
    if reply_count >= 2:
        scores["forum/discussion"] += reply_count * 2

    max_score = max(scores.values())
    if max_score == 0:
        return "other"

    return max(scores, key=scores.get)


# ============================================================================
# MAIN ANALYZER
# ============================================================================


def analyze_row(row, page_id_col, url_col, text_col):
    """Analyze a single row from DataFrame."""
    page_id = row.get(page_id_col, "")
    url = row.get(url_col, "")
    text = row.get(text_col, "")

    social = extract_social(text)

    return {
        "page_id": page_id,
        "url": url,
        "emails": extract_emails(text),
        "phones": extract_phones(text),
        "dates": extract_dates(text),
        "prices": extract_prices(text),
        "urls": extract_urls(text),
        "social_handles": social["handles"],
        "hashtags": social["hashtags"],
        "all_caps_words": extract_all_caps(text),
        "question_count": count_question_marks(text),
        "category": classify_webpage(text, url),
    }


def analyze_csv(
    input_file, output_file, page_id_col="page_id", url_col="url", text_col="full_text"
):
    """
    Read CSV file, analyze each webpage, and save results to CSV.

    Args:
        input_file: Path to input CSV file
        output_file: Path to output CSV file
        page_id_col: Column name for page ID
        url_col: Column name for URL
        text_col: Column name for webpage text/content

    Returns:
        DataFrame with analysis results
    """
    # Read input CSV
    print(f"Reading {input_file}...")
    df_input = pd.read_csv(input_file)
    print(f"Found {len(df_input)} rows")
    print(f"Columns: {list(df_input.columns)}")

    # Analyze each row
    print("\nAnalyzing webpages...")
    results = []
    for idx, row in df_input.iterrows():
        result = analyze_row(row, page_id_col, url_col, text_col)
        results.append(result)

        if (idx + 1) % 500 == 0:
            print(f"  Processed {idx + 1}/{len(df_input)} rows...")

    print(f"  Processed {len(df_input)}/{len(df_input)} rows... Done!")

    # Create output DataFrame
    df_output = pd.DataFrame(results)

    # Convert lists to JSON strings for CSV storage
    list_columns = [
        "emails",
        "phones",
        "dates",
        "prices",
        "urls",
        "social_handles",
        "hashtags",
        "all_caps_words",
    ]

    for col in list_columns:
        df_output[col] = df_output[col].apply(json.dumps)

    # Save to CSV
    print(f"\nSaving results to {output_file}...")
    df_output.to_csv(output_file, index=False, encoding="utf-8")
    print(f"Saved {len(results)} results to {output_file}")

    # Print category summary
    print("\n" + "=" * 50)
    print("CATEGORY SUMMARY")
    print("=" * 50)
    print(df_output["category"].value_counts().to_string())
    print("=" * 50)

    return df_output


# ============================================================================
# USAGE
# ============================================================================

if __name__ == "__main__":

    # ===== CONFIGURATION =====
    INPUT_FILE = "data/dataset_with_assignments.csv"  # Your input CSV file
    OUTPUT_FILE = "data/OH_results.csv"  # Output CSV file

    # Column names matching your CSV structure
    PAGE_ID_COL = "page_id"
    URL_COL = "url"
    TEXT_COL = "full_text"  # Using 'full_text' column from your data
    # =========================

    # Run analysis
    df_results = analyze_csv(
        input_file=INPUT_FILE,
        output_file=OUTPUT_FILE,
        page_id_col=PAGE_ID_COL,
        url_col=URL_COL,
        text_col=TEXT_COL,
    )

    # Display sample results
    print("\n" + "=" * 50)
    print("SAMPLE RESULTS (First 10 rows)")
    print("=" * 50)

    for idx, row in df_results.head(10).iterrows():
        print(f"\nPage {row['page_id']}")
        print(
            f"  URL: {row['url'][:60]}..."
            if len(str(row["url"])) > 60
            else f"  URL: {row['url']}"
        )
        print(f"  Category: {row['category']}")
        print(f"  Emails: {row['emails']}")
        print(f"  Phones: {row['phones']}")
        print(f"  Question Count: {row['question_count']}")
