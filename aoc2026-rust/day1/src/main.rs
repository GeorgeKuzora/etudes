use std::fs;

enum Rotation {
    Right(i32),
    Left(i32),
}

impl Rotation {
    fn from_string(value: &str) -> Self {
        let direction = value.chars().next().unwrap();
        let number: i32 = value.get(1..).unwrap().parse().unwrap();

        match direction {
            'L' => Self::Left(number),
            'R' => Self::Right(number),
            _ => panic!("Unrecognized direction"),
        }
    }
}

struct Dial {
    clicks: u32,
    current: i32,
    qnt: i32
}

impl Dial {
    fn calc_times_on_zero(mut self, elem: Rotation) -> Self {
        let current = match elem {
            Rotation::Right(val) => {
                (self.current + val) % self.qnt
            },
            Rotation::Left(val) => {
                (self.current - val + self.qnt) % self.qnt
            },
        };

        self.current = current;
        if self.current == 0 { self.clicks += 1 };
        self
    }

    fn calc_times_across_zero(mut self, elem: Rotation) -> Self {
        let current = match elem {
            Rotation::Right(val) => {
                (self.current + val) % self.qnt
            },
            Rotation::Left(val) => {
                let current = (self.current - val + self.qnt) % self.qnt;
                if current < 0 {
                    current + self.qnt
                } else {
                    current
                }
            },
        };

        let times_across_zero = match elem {
            Rotation::Right(val) => {
                (self.current + val) / self.qnt
            },
            Rotation::Left(val) => {
                let relative_to_zero = self.current - val;
                if relative_to_zero > 0 {
                    0
                } else if relative_to_zero == 0 {
                    1
                } else {
                    if self.current == 0 {
                        relative_to_zero * -1 / self.qnt
                    } else {
                        (relative_to_zero * -1 + self.qnt) / self.qnt
                    }
                }
            },
        };
        self.clicks += u32::try_from(times_across_zero).unwrap();

        self.current = current;
        self
    }
}

fn main() {
    let times_on_zero = fs::read_to_string("input.txt")
        .unwrap()
        .split_whitespace()
        .map(Rotation::from_string)
        .fold(Dial { clicks: 0, current: 50 , qnt: 100 }, |dial, rotate| dial.calc_times_on_zero(rotate))
        .clicks;

    println!("times dial pointed on zero: {times_on_zero}");

    let times_across_zero = fs::read_to_string("input.txt")
        .unwrap()
        .split_whitespace()
        .map(Rotation::from_string)
        .fold(Dial { clicks: 0, current: 50 , qnt: 100 }, |dial, rotate| dial.calc_times_across_zero(rotate))
        .clicks;

    println!("times dial pointed across zero: {times_across_zero}");
}
