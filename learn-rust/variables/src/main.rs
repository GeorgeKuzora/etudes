const MY_CONSTANT: u32 = 3 * 60 *60;

const MY_STRING: &str = "hello";

fn main() {
    let mut x = 5;
    println!("var x = {x}");
    x = 6;
    println!("var x = {x}");
    println!("const = {MY_CONSTANT}");
    {
        let x = MY_CONSTANT;
        println!("var x = {x}");
    };
    println!("var x = {x}");
    let guess = "42".parse::<u32>().expect("Not a number!");
    println!("var guess = {guess}");

    let tup: (i32, f64, &str) = (4, 4.0, MY_STRING);

    let (x, y, z) = tup;

    let mut a: [i32; 5] = [0; 5];

    a[0] = 1
}
