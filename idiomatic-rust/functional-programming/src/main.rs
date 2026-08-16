use functional_programming::LinkedList;

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
    let adder = |left: fn() -> i32, right: fn() -> i32| left() + right();
    adder(left_value, right_value);
    let consumable = String::from("cookies");
    let consumer = move || consumable;
    consumer();

    let dinosaurs = LinkedList::new("Tyrannosaurus Rex");
    let last_item = dinosaurs.iter().last().expect("couldn't get last item");
    println!("last_item='{}'", last_item);

    let mut dinosaurs = LinkedList::new("Tyrannosaurus Rex");
    dinosaurs.append("Triceratops");
    dinosaurs.append("Velociraptor");
    dinosaurs.append("Stegosaurus");
    dinosaurs.append("Spinosaurus");

    dinosaurs.iter().for_each(|data| println!("data={}", data));

    for data in &dinosaurs {
        println!("with for loop: data={}", data);
    }

    let arr = [1, 2, 3, 4];
    let vec: Vec<String> = arr.iter().map(|n| n.to_string()).collect();
    println!("{:?}", vec);

    // let linked_list: LinkedList<i32> = vec.iter().flat_map(|v| v.parse::<i32>()).collect();

    let arr = ["duck", "1", "2", "goose", "3", "4"];
    let (successes, failures): (Vec<_>, Vec<_>) = arr
        .iter()
        .map(|v| v.parse::<i32>())
        .partition(Result::is_ok);

    println!("successses={:?}", successes);
    println!("failures={:?}", failures);
    let successes: Vec<_> = successes.into_iter().flatten().collect();
    let failures: Vec<_> = failures.into_iter().map(|e| e.unwrap_err()).collect();

    println!("successes={:?}", successes);
    println!("failures={:?}", failures);
}
