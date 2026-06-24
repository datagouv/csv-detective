use crate::value::Value;

pub fn detect(val: &str) -> Option<()> {
    // must start with http://, https://, ftp://, or www.
    let lower = val.to_ascii_lowercase();
    if !lower.starts_with("http://")
        && !lower.starts_with("https://")
        && !lower.starts_with("ftp://")
        && !lower.starts_with("www.")
    {
        return None;
    }

    // after protocol, must have a domain with at least one dot
    let after_protocol = if let Some(rest) = lower.strip_prefix("http://") {
        rest
    } else if let Some(rest) = lower.strip_prefix("https://") {
        rest
    } else if let Some(rest) = lower.strip_prefix("ftp://") {
        rest
    } else if let Some(rest) = lower.strip_prefix("www.") {
        rest
    } else {
        return None;
    };

    // domain part (before first /)
    let domain_end = after_protocol.find('/').unwrap_or(after_protocol.len());
    let domain = &after_protocol[..domain_end];

    if domain.is_empty() || !domain.contains('.') {
        return None;
    }

    // tld must be 2-6 alpha chars
    let last_dot = domain.rfind('.')?;
    let tld = &domain[last_dot + 1..];
    if tld.len() < 2 || tld.len() > 6 {
        return None;
    }
    if !tld.chars().all(|c| c.is_ascii_alphabetic()) {
        return None;
    }

    Some(())
}

pub fn test(val: &Value) -> bool {
    detect(val.raw()).is_some()
}
