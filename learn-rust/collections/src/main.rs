use::std::collections::HashMap;


fn main() {
    let mut v = Vec::new();
    v.push(11);

    let mut v = vec![String::from("1"), String::from("2"), String::from("3"), String::from("4"), String::from("5")];

    let third = &v[2];

    let third_opt = v.get(2);

    println!("{third}");

    if let Some(x) = third_opt {
        println!("{x}");
    }

    for i in &v {
        println!("{i}")
    };

    for i in &mut v {
        i.push('2')
    };
    for i in v {
        println!("{i}")
    };

    let row = vec![
        SpreadSheetCell::Int(3),
        SpreadSheetCell::Float(3.0),
        SpreadSheetCell::Text(String::from("3"))
    ];

    let mut s = String::new();
    s.push_str("string");

    let data = "initial";
    let si = data.to_string();

    let s3 = s + &si;

    for c in s3.chars() {
        println!("{c}");
    }
    for b in s3.bytes() {
        println!("{b}");
    }


    let mut scores = HashMap::new();

    scores.insert("red".to_string(), 3);
    scores.insert("blue".to_string(), 2);

    let team_name = "green".to_string();
    let score = scores[&team_name];
    let score = scores.get(&team_name).copied().unwrap_or_default();
    scores.entry(team_name).or_insert(50);
}

enum SpreadSheetCell {
    Int(i32),
    Float(f64),
    Text(String),
}
