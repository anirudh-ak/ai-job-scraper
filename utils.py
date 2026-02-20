import re


def _text(s):
    return (s or "").lower()


def text_contains_any(text, keywords):
    if not text:
        return False
    text_l = _text(text)
    for k in keywords:
        if k and k.lower() in text_l:
            return True
    return False


def job_matches(job, config):
    """Return True if the job fits the config filters.

    Filtering rules:
    1. exclude_keywords must not appear anywhere in title or description.
    2. A location keyword must appear in the combined text unless "anywhere"
       is in location_keywords (all boards here are remote-only so this is
       mostly a safety net).
    3. At least one job_keyword must match as a whole word in the title+tags
       (the primary signal). If not found there, it must appear in the
       description AND at least one role_keyword must also appear in the
       title — preventing jobs that merely mention AI in passing.
    4. At least one role_keyword must match as a whole word in the title.
       This ensures we only surface roles the user actually wants.

    Matching uses word-boundary regex to avoid substring false positives
    (e.g. "AI" won't match inside "MAIL" or "PAID").
    """
    title = job.get("title", "").lower()
    description = job.get("description", "").lower()
    tags_text = " ".join(job.get("tags") or []).lower()
    location = job.get("location", "").lower()

    # Combined for exclusion / location checks
    combined = f"{title} {job.get('company', '').lower()} {description} {tags_text} {location}"

    def _contains_word(text, kw):
        if not kw:
            return False
        pattern = r"\b" + re.escape(kw.lower()) + r"\b"
        return re.search(pattern, text) is not None

    # 1. Exclusions — check title + description only (not tags, which can be noisy)
    for ex in config.get("exclude_keywords", []) or []:
        if _contains_word(title + " " + description, ex):
            return False

    # 2. Location check
    loc_keywords = [k.lower() for k in (config.get("location_keywords") or [])]
    if "anywhere" not in loc_keywords:
        if not any(_contains_word(combined, lk) for lk in loc_keywords):
            return False

    job_keys = config.get("job_keywords") or []
    role_keys = config.get("role_keywords") or []

    # 3. Job keyword must appear in title+tags (strong signal)
    title_tags = f"{title} {tags_text}"
    has_job_kw_in_title = any(_contains_word(title_tags, jk) for jk in job_keys)

    if not has_job_kw_in_title:
        # Fallback: keyword in description is only acceptable if a role keyword
        # is also in the title (the role is clearly relevant, AI is the context)
        has_job_kw_in_desc = any(_contains_word(description, jk) for jk in job_keys)
        has_role_in_title = any(_contains_word(title, rk) for rk in role_keys)
        if not (has_job_kw_in_desc and has_role_in_title):
            return False

    # 4. Role keyword must appear in the title
    if not any(_contains_word(title, rk) for rk in role_keys):
        return False

    return True
