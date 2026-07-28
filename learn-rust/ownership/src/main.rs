use std::usize;

fn main() {
    let mut s1 = String::from("hello");
    s1.push_str(", world");
    println!("{s1}");

    let x = 5;
    let y = x;

    makes_copy(x);
    let z = x;
    println!("{x}");

    let s2 = s1.clone();
    println!("{s1} and {s2}");
    take_ownership(&mut s1);
    println!("{s1} and {s2}");
    take_ownership(&mut s1);

    let mut s3 = give_ownership();
    let s3 = takes_and_gives_back(&mut s3);
    println!("{s3} and {s2}");

    // let mut s1 = String::from("hello");
    // let len = calculate_length(&s1);
    // println!("The length of '{s1}' is {len}.");
    // let m = &mut s1;
    // change(&mut s1);
    // change(m);
    // let len = calculate_length(&s1);
    // println!("The length of '{s1}' is {s1}.");
    //
    // let mut s = String::from("hello");
    //
    // let r2 = &mut s;
    // change(r2);
    // let r1 = &s;
    //
    // println!("{r1}, {r2}");
    // let ref_to_nothing = dangle();

    let words = String::from(" ");
    let fw = first_word(&words);
    println!("first word is: {fw}");

    let s = String::from("Hello world");
    let hello = &s[0..5];
    let world = &s[6..=10];

}

// fn dangle() -> &String {
//     let s = String::from("value");
//     &s
// }

fn change(s: &mut String) {
    s.push_str("string");
}

fn makes_copy(x: i32) {
    println!("{x}");
}

fn take_ownership(s: &mut String) {
    println!("{s}")
}

fn give_ownership() -> String {
    let s = String::from("value");
    s
}

fn takes_and_gives_back(s: &mut String) -> &String {
    s
}

fn calculate_length(s: &str) -> usize {
    s.len()
}

fn first_word(s: &str) -> &str {
    match s.trim().split_whitespace().next() {
        None=>s,
        Some(s)=>s,
    }
}

fn first_word_alt(s: &str) -> &str {
    let bytes = s.as_bytes();

    for (i, &item) in bytes.iter().enumerate() {
        if item == b' ' {
            return &s[..i];
        }
    }
    &s[..]
}

fn n_word(s: &str, n: usize) -> &str {
    s.trim().split_whitespace().nth(n).unwrap_or(s)
}

fn n_word_alt(s: &str, n: usize) -> &str {
    let words: Vec<&str> = s.trim().split_whitespace().collect();
    if words.len() <= n {
        s
    } else {
        words[n]
    }
}
