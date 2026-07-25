use std::{fs};

fn main() {
    let invalid_qnt: u64 = fs::read_to_string("input.txt")
        .unwrap()
        .trim()
        .split(",")
        .flat_map(split_range)
        .filter(exactly_twice)
        .sum();

    println!("Quantity of invalid ID with exactly twice: {invalid_qnt}");

    let invalid_qnt: u64 = fs::read_to_string("input.txt")
        .unwrap()
        .trim()
        .split(",")
        .flat_map(split_range)
        .filter(at_least_twice)
        .sum();

    println!("Quantity of invalid ID with at least twice: {invalid_qnt}")
}

fn split_range(range: &str) -> std::ops::RangeInclusive<u64> {
    let parts: Vec<&str> = range.split('-').collect();
    if parts.len() == 2 {
        let start = parts[0].parse::<u64>().unwrap();
        let end = parts[1].parse::<u64>().unwrap();
        start..=end
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

fn at_least_twice(n: &u64) -> bool {
    let s = n.to_string();
    let len = s.len();

    if len < 2 {
        return false;
    }

    for window_len in 1..=(len / 2) {
        if len % window_len != 0 {
            continue;
        }

        let first_segment = &s[..window_len];

        let all_equal = (window_len..len)
            .step_by(window_len)
            .all(|start| &s[start..start + window_len] == first_segment);

        if all_equal {
            return true;
        }
    }

    false
}
