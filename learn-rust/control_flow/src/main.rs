fn main() {
    let x = 3;

    let y = if x < 3 {
            2
        } else if x < 5 {
            5
        } else {
            10
        };
    println!("{y}");

    let mut counter = 0;
    while counter != 10 {
        counter += 1;
    };

    let mut counter = Some(0);

    while let Some(i) = counter {
        if i == 10 {
            counter = None;
        } else {
            println!("{i}");
            counter = Some (i + 1);
        }
    }

    for element in (1..4).rev() {
        println!("the value is: {element}");
    };
    for element in (1..=3).rev() {
        println!("the value is: {element}");
    };
}
