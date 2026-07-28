use std::{cmp::Ordering, io, num};

use rand::Rng;

fn main() {
    println!("Guess the number");

    let secret_number = get_secret_number(1, 100);

    let mut guessed = String::new();

    loop {
        println!("Please input your guess:");

        io::stdin()
            .read_line(&mut guessed)
            .expect("Failed to read the guess");

        let guess: u32 = match guessed.trim().parse() {
            Ok(num) => num,
            Err(_) => { println!("Only positive number is allowed"); guessed.clear(); continue },
        };

        println!("You guested: {guess}");

        let right = compare(&secret_number, &guess);
        if right {
            return
        }
        guessed.clear();
    }
}

fn get_secret_number(low: u32, high: u32) -> u32 {
    rand::thread_rng().gen_range(low..=high)
}

fn compare(secret: &u32, guess: &u32) -> bool {
    match guess.cmp(secret) {
        Ordering::Less => { println!("Too Low"); false },
        Ordering::Greater => { println!("Too High"); false },
        Ordering::Equal => { println!("You Guessed right"); true }
    }
}
