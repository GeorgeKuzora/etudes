use std::process::id;

fn main() {
    let mut x = Some(0);

    x = match x {
        None => None,
        Some(x) => Some(x + 1),
    };

    println!("{}", x.unwrap());

    let favorite_color: Option<&str> = None;
    let is_tuesday = false;
    let age: Result<u8, _> = "34".parse();

    if let Some(color) = favorite_color {
        println!("Using your favorite color, {color}, as the background");
    } else if is_tuesday {
        println!("Tuesday is green day!");
    } else if let Ok(age) = age {
        if age > 30 {
            println!("Using purple as the background color");
        } else {
            println!("Using orange as the background color");
        }
    } else {
        println!("Using blue as the background color");
    }

    let (tx, rx) = std::sync::mpsc::channel();

    std::thread::spawn(move || {
        for val in [1, 2, 3] {
            tx.send(val).unwrap();
        }
    });

    while let Ok(val) = rx.recv() {
        println!("{val}")
    }

    let v = vec![1, 2, 3];

    for (index, value) in v.iter().enumerate() {
        println!("{value} is at index {index}");
    }

    let point = (1, 2);
    print_coordinates(&point);

    let x = 1;

    match x {
        1 => println!("one"),
        2 => println!("two"),
        _ => println!("more than two"),
    }

    let x = Some(10);
    let y = 10;

    match x {
        Some(50) => println!("Got 50"),
        Some(n) if y == n => println!("Matched, y = {y}"),
        _ => println!("Default case, x = {x:?}"),
    }
    println!("at the end: x = {x:?}, y = {y}");

    let x = 1;

    match x {
        1 | 2 => println!("one or two"),
        3 => println!("three"),
        _ => println!("anything"),
    }

    let x = 5;

    match x {
        1..=5 => println!("one through five"),
        _ => println!("more than five")
    }

    let x = 'c';
    match x {
        'a'..='j' => println!("early letters"),
        'k'..='z' => println!("late letters"),
        _ => println!("other char"),
    };

    let p = Point { x: 1, y: 2 };

    let Point { x, y } = p;
    assert_eq!(1, x);
    assert_eq!(2, y);

    let p = Point {
        x: 0,
        y: 1,
    };

    match p {
        Point { x: 0, y: 0 } => println!("at the center"),
        Point { x: 0, y } => println!("On the y axis at {y}"),
        Point { x, y: 0 } => println!("On the x axis at {x}"),
        Point { x, y } => println!("On neither axis: ({x}, {y})"),
    };

    let msg = Message::Move(p);

    match msg {
        Message::Quit => {
            println!("The Quit variant has no data to destructure.");
        }
        Message::Move(Point { x, y }) => {
            println!("Move in the x direction {x} and in the y direction {y}");
        }
        Message::Write(text) => {
            println!("Text message: {text}");
        }
        Message::ChangeColor(Color::Rgb(r, g, b)) => {
            println!("Change color to red {r}, green {g}, and blue {b}");
        }
        Message::ChangeColor(Color::Hsv(h, s, v)) => {
            println!("Change color to hue {h}, saturation {s}, and value {v}");
        }
    }

    foo(3, 4);

    let mut setting_value = Some(5);
    let new_setting_value = None;

    match (setting_value, new_setting_value) {
        (Some(_), Some(_) | None) => println!("Can't overwrite an existing customized value"),
        _ => setting_value = new_setting_value,
    }
    println!("setting is {setting_value:?}");

    let p = Point3D {x: 1, y: 2, z: 3};

    match p {
        Point3D{x, ..} => println!("x is {x}"),
    }

    let numbers = (1, 2, 3, 4, 5, 6);

    match numbers {
        (first, .., last) => println!("Some numbers: {first}, {last}"),
    }

    let numbers = [1, 2, 3, 4, 5, 6];

    match numbers {
        [first, ref middle @ .., last] => {
            println!("First: {first}");
            println!("Middle: {middle:?}");
            println!("Last: {last}");
        }
    }

    let num = Some(4);
    match num {
        Some(x) if x % 2 == 0 => println!("The number {x} is even"),
        Some(x) => println!("The number {x} is odd"),
        None => (),
    }

    let x = 4;
    let y = true;

    match x {
        4 | 5 | 6 if y => println!("yes"),
        _ => println!("no"),
    }

    let g = Greet::Hello {id: 5};

    match g {
        Greet::Hello { id: id @ 1..=5 } => println!("Found an id in range: {id}"),
        Greet::Hello { id: 6..=12 } =>  println!("Found an id in another range"),
        Greet::Hello { id } => println!("Found some other id: {id}"),
    }
}

enum Greet {
    Hello{id: i32},
}

struct Point3D {
    x: i32,
    y: i32,
    z: i32
}

fn foo(_: i32, y: i32) {
    println!("This code only uses the y parameter: {y}");
}

enum Message {
    Quit,
    Move(Point),
    Write(String),
    ChangeColor(Color),

}

enum Color {
    Rgb(i32, i32, i32),
    Hsv(i32, i32, i32),
}

struct Point {
    x: i32,
    y: i32,
}

fn print_coordinates(&(x, y): &(i32, i32)) {
    println!("Current location: ({x}, {y})");
}
