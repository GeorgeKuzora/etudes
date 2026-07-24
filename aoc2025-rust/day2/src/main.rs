use std::fs;

struct Range {
    start: u64,
    end: u64,
}

fn main() {
    let invalid_qnt: u64 = fs::read_to_string("input.txt")
        .unwrap()
        .trim()
        .split(",")
        .map(split_range)
        .flat_map(|r| r.start..=r.end)
        .filter(|n| exactly_twice(n))
        .sum();

    println!("Quantity of invalid ID: {invalid_qnt}")
}

fn split_range(range: &str) -> Range {
    let parts: Vec<&str> = range.split('-').collect();
    if parts.len() == 2 {
        let start = parts[0].parse::<u64>().unwrap();
        let end = parts[1].parse::<u64>().unwrap();
        Range{start, end}
    } else {
        panic!("invalid format")
    }
}

fn exactly_twice(n: &u64) -> bool {
    let s = n.to_string();
    let len = s.len();

    if len == 0 || len % 2 != 0 {
        return false;
    }

    let mid = len / 2;
    s[..mid] == s[mid..]
}
