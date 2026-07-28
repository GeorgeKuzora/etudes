fn main() {
    println!("Hello, world!");

    another_function(5, 'h');

    let x = get_none();
    let y = x + 2;
}

fn another_function(x: i32, unit_label: char) {
    println!("Another function {x}{unit_label}.");
}

fn get_none() {
    ()
}
