use crate::value::Value;

pub fn detect(val: &str) -> Option<()> {
    // ^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$ case insensitive
    let val = val.as_bytes();
    let at_pos = val.iter().position(|&b| b == b'@')?;
    if at_pos == 0 {
        return None;
    }

    // local part: a-z0-9._%+-
    for &b in &val[..at_pos] {
        if !b.is_ascii_alphanumeric()
            && b != b'.'
            && b != b'_'
            && b != b'%'
            && b != b'+'
            && b != b'-'
        {
            return None;
        }
    }

    let domain = &val[at_pos + 1..];
    if domain.is_empty() {
        return None;
    }

    // find last dot in domain
    let last_dot = domain.iter().rposition(|&b| b == b'.')?;
    if last_dot == 0 || last_dot == domain.len() - 1 {
        return None;
    }

    // domain part before last dot: a-z0-9.-
    for &b in &domain[..last_dot] {
        if !b.is_ascii_alphanumeric() && b != b'.' && b != b'-' {
            return None;
        }
    }

    // tld: a-z, at least 2 chars
    let tld = &domain[last_dot + 1..];
    if tld.len() < 2 {
        return None;
    }
    for &b in tld {
        if !b.is_ascii_alphabetic() {
            return None;
        }
    }

    Some(())
}

pub fn test(val: &Value) -> bool {
    detect(val.raw()).is_some()
}
