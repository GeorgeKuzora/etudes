use std::fs;

enum Operator {
    Sum,
    Mult,
}

impl Operator {
    fn new(op: &str) -> Self {
        match op {
            "+" => Self::Sum,
            "*" => Self::Mult,
            _ => panic!("unsupported operator"),
        }
    }
}

struct Expression {
    op: Operator,
    result: u64,
}

impl Expression {
    fn new(op: Operator) -> Self {
        let init_value = match op {
            Operator::Sum => 0,
            Operator::Mult => 1,
        };

        Self { op, result: init_value }
    }

    fn collect(&mut self, n: u64) {
        match self.op {
            Operator::Sum => self.result += n,
            Operator::Mult => self.result *= n,
        }
    }
}

fn main() {
    let input = fs::read_to_string("input.txt").expect("file should be in path");

    // PART 1
    let mut expressions: Vec<Expression> = input.lines()
        .last()
        .expect("should be a line")
        .split_whitespace()
        .map(Operator::new)
        .map(move |op| Expression::new(op))
        .collect();

    let number_lines = input.lines().rev().skip(1);

    for line in number_lines {
        let numbers = line.split_whitespace();

        for (exp, num_str) in expressions.iter_mut().zip(numbers) {
            let n = num_str.parse::<u64>().expect("should be a valid u64");
            exp.collect(n);
        }
    }

    let total: u64 = expressions.iter().map(|exp| exp.result).sum();
    println!("Part1 grand total: {total}");

    // PART 2
}
