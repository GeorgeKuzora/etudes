use std::collections::HashMap;

fn main() {
    let s = "Hello world";
    let latin_s = to_pig_latin(s);
    println!("{latin_s}")
}

fn calculate_median(v: &mut Vec<i32>) -> Option<i32> {
    v.sort_unstable();
    let mid = v.len() / 2;
    v.get(mid).copied()
}

fn calculate_mode(v: &Vec<i32>) -> i32 {
    let mut ocurencies = HashMap::new();

    for i in v.iter() {
        let e = ocurencies.entry(i).or_insert(0);
        *e += 1;
    }

    if let Some(mode) = ocurencies.values().max().copied() {
        return mode
    }
    return 0
}

fn to_pig_latin(s: &str) -> String {
    let latin: Vec<String> = s.trim().split_whitespace().map(word_to_pig_latin).collect();
    let latin = latin.join(" ");
    latin
}

fn word_to_pig_latin(w: &str) -> String {
    let Some(first) = w.chars().next() else {
        return "".to_string()
    };
    let first = first.to_ascii_lowercase();
    let suffix = if matches!(first, 'a' | 'e' | 'i' | 'o' | 'u') {
        format!("-hay")
    } else {
        format!("-{first}ay")
    };

    let w: String = w.chars().skip(1).collect();
    w + &suffix
}
