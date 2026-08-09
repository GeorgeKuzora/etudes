fn main() {
    let bark = || println!("woof, woof");
    bark();
    let increment = |value| value + 1;
    increment(1);
    let print_and_increment = |value| {
        println!("incrementing the value {value}");
        value + 1
    };
    print_and_increment(5);

    let left_value = || 1;
    let right_value = || 2;
    let adder = |left: fn()->i32, right: fn()->i32| left() + right();
    adder(left_value, right_value);
    let consumable = String::from("cookies");
    let consumer = move || consumable;
    consumer();
}

trait Iterator {
    type Item;
    fn next(&mut self) -> Option<Self::Item>;
}
