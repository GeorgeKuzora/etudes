use std::fs;

fn main() {
    let invalid_qnt: u64 = fs::read_to_string("input.txt")
        .unwrap()
        .trim()
        .split(",")
        .flat_map(split_range)
        .filter(exactly_twice)
        .sum();

    println!("Quantity of invalid ID: {invalid_qnt}")
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
