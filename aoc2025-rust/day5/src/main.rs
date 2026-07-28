use std::fs;

fn main() {
    let input = fs::read_to_string("input.txt").expect("can't find input.txt");

    let  ranges;
    let  ids;

    match split_at_empty_line(&input) {
        Some((part1, part2)) => {
            ranges = part1;
            ids = part2
        },
        None => panic!("not enough parts in the file")
    }

    let mut ranges: Vec<Range> = ranges.lines().map(input_to_range).collect();
    ranges.sort();
    dbg!(ranges);
}

fn split_at_empty_line(text: &str) -> Option<(&str, &str)> {
    text.split_once("\n\n")
}

fn input_to_range(input: &str) -> Range {
    match input.split_once("-") {
        Some((start, end)) => {
            let start: u64 = start.parse().expect("range start should be valid u64");
            let end: u64 = end.parse().expect("range end should be valid u64");
            Range { start, end }
        },
        None => panic!("invalid range in the input"),
    }
}

type Id = u64;

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
struct Range {
    start: u64,
    end: u64,
}

impl Range {
    fn new(start: u64, end: u64) -> Self {
        Range { start, end }
    }

}
