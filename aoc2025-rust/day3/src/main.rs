use std::fs;

fn main() {
    let max_joultage: u64 = fs::read_to_string("input.txt")
        .unwrap()
        .trim()
        .lines()
        .map(|bank| variable_qnt(2, bank))
        .sum();

    println!("Max joultage from two batteries: {max_joultage}");

    let max_joultage: u64 = fs::read_to_string("input.txt")
        .unwrap()
        .trim()
        .lines()
        .map(|bank| variable_qnt(12, bank))
        .sum();

    println!("Max joultage from twelve batteries: {max_joultage}");
}

// fn exactly_two(bank: &str) -> u64 {
//     let len = bank.len();
//     if len <= 2 {
//         return bank.parse().unwrap();
//     }

//     let digits: Vec<u64> = bank.chars().filter_map(|c| Some(c.to_digit(10).unwrap() as u64)).collect();

//     let mut first_id = 0;
//     let mut second_id = 1;

//     for i in 1..len {
//         let candidate = digits[i];
//         if candidate > digits[first_id] && i < len - 1 {
//             first_id = i;
//             second_id = i + 1;
//         } else if candidate > digits[second_id] {
//             second_id = i;
//         }
//     }
//     digits[first_id] * 10 + digits[second_id]
// }

fn variable_qnt(qnt: u64, bank: &str) -> u64 {
    let qnt = qnt as usize;
    let len = bank.len();
    if len <= qnt {
        return bank.parse().unwrap();
    }

    let digits: Vec<u64> = bank.chars().filter_map(|c| Some(c.to_digit(10).unwrap() as u64)).collect();

    let mut lesser_order_elements = len - qnt;

    let mut stack = Vec::with_capacity(qnt);

    for &d in &digits {
        while stack.last() < Some(&d) && lesser_order_elements > 0 && !stack.is_empty() {
            stack.pop();
            lesser_order_elements -= 1;
        }
        stack.push(d);
    }

    while lesser_order_elements > 0 {
        stack.pop();
        lesser_order_elements -= 1;
    }

    stack.iter().fold(0, |acc, &d| acc * 10 + d)
}
