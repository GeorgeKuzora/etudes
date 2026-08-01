use std::fs;
use std::cmp::Ordering;

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
    // Need for both parts
    let ranges = combine_ranges(&ranges);

    // Part 1
    let fresh_id_count = ids.lines()
        .map(|line| line.parse::<u64>().expect("id should be a valid number"))
        .map(|id| ranges.binary_search_by(
            |range| range.partial_cmp(&id).expect("unexepted fail during binary search")
        ))
        .flatten()
        .count();

    println!("available ingredient IDs are fresh: {fresh_id_count}");

    // Part 2
    let all_ranges_count: u64 = ranges.iter().map(|range| range.len()).sum();

    println!("ingredient IDs are considered to be fresh: {all_ranges_count}");
}

fn combine_ranges(ranges: &[Range]) -> Vec<Range> {
    let mut out = Vec::new();
    let len = ranges.len();

    let mut cri = 0;
    let mut nri = 1;

    while cri < len {
        let cr = ranges[cri];
        let mut comb = Range::new(cr.left, cr.right);

        while nri < len {
            let nr = ranges[nri];

            // If they don't overlap, stop looking ahead
            if comb.right < nr.left {
                break;
            }

            // They overlap. If the next range extends further right, expand our combined range.
            if comb.right <= nr.right {
                comb.right = nr.right;
            }

            cri += 1;
            nri += 1;
        }

        out.push(comb);
        cri += 1;
        nri += 1;
    }

    out
}

fn split_at_empty_line(text: &str) -> Option<(&str, &str)> {
    text.split_once("\n\n")
}

fn input_to_range(input: &str) -> Range {
    match input.split_once("-") {
        Some((start, end)) => {
            let start: u64 = start.parse().expect("range start should be valid u64");
            let end: u64 = end.parse().expect("range end should be valid u64");
            Range::new(start, end)
        },
        None => panic!("invalid range in the input"),
    }
}

type Id = u64;

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
struct Range {
    left: u64,
    right: u64,
}

impl Range {
    fn new(start: u64, end: u64) -> Self {
        Range { left: start, right: end }
    }

    fn len(&self) -> u64 {
        self.right - self.left + 1
    }
}

impl PartialEq<Id> for Range {
    fn eq(&self, other: &Id) -> bool {
        *other >= self.left && *other <= self.right
    }
}

impl PartialEq<Range> for Id {
    fn eq(&self, other: &Range) -> bool {
        self >= &other.left && self <= &other.right
    }
}

impl PartialOrd<Id> for Range {
    fn partial_cmp(&self, other: &Id) -> Option<Ordering> {
        if self.left <= *other && self.right >= *other {
            Some(Ordering::Equal)
        } else if self.left > *other {
            Some(Ordering::Greater)
        } else if self.right < *other {
            Some(Ordering::Less)
        } else {
            None
        }
    }
}

impl PartialOrd<Range> for Id {
    fn partial_cmp(&self, other: &Range) -> Option<Ordering> {
        if self >= &other.left && self <= &other.right {
            Some(Ordering::Equal)
        } else if self < &other.left {
            Some(Ordering::Greater)
        } else if self > &other.right {
            Some(Ordering::Less)
        } else {
            None
        }
    }
}
