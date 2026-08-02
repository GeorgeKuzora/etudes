use std::{fmt::Debug, marker::PhantomData};

#[derive(Debug)]
struct Container<T> {
    field: T
}

impl<T> Container<T> {
    fn new(value: T) -> Self {
        Self { field: value }
    }
}

#[derive(Clone)]
struct ListItem<T>
where T: Clone + Debug
{
    data: Box<T>,
    next: Option<Box<T>>,
}

enum Recurcive<T> {
    Next(Box<Recurcive<T>>),
    Box(Box<T>),
    Optional(Option<T>),
}

struct Dog<Breed> {
    name: String,
    breed: PhantomData<Breed>,
}

impl Dog<Poodle> {
    fn breed_name(&self) -> &str {
        "Poodle"
    }
}

impl Dog<Retriever> {
    fn breed_name(&self) -> &str {
        "Retriever"
    }
}

impl SelfDescribing for Dog<Poodle> {
    fn describe(&self) -> String {
        "Dog<Poodle>".into()
    }
    fn describe_type() -> String {
        "Dog<Poodle>".into()
    }
}
impl SelfDescribing for Dog<Retriever> {
    fn describe(&self) -> String {
        "Dog<Retriever>".into()
    }
    fn describe_type() -> String {
        "Dog<Retriever>".into()
    }
}

struct Poodle {}
struct Retriever {}

fn main() {
    let container = Container {field: "hello world"};
    println!("{container:?}");

    let a: Container<Option<&str>> = Container {field: None};
    println!("{a:?}");

    let b = Container::<Option<&str>>::new(None);
    println!("{b:?}");

    let poodle: Dog<Poodle> = Dog { name: String::from("Boy"), breed: PhantomData };
    let retriever: Dog<Retriever> = Dog { name: String::from("Boy"), breed: PhantomData };
    println!("p: {}, r: {}", poodle.breed_name(), retriever.breed_name());
    println!("Does it bark? p: {}, r: {}", poodle.it_barks(), retriever.it_barks());

    let t = describe_type(&poodle);
    println!("poodle type is: {t}");
    let t = describe_type(&retriever);
    println!("retriever type is: {t}");
    println!("poodle type is: {}", describe_type_selfless::<Dog<Poodle>>());
    println!("retriever type is: {}", describe_type_selfless::<Dog<Retriever>>());

    let mut v = Vec::<Box<dyn MyTrait>>::new();
    v.push(Box::new(MyStruct1{}));
    v.push(Box::new(MyStruct2{}));

    v.iter().for_each(|t| t.trait_hello());
}

trait MinimalTrait {}

trait DoesItBark {
    fn it_barks(&self) -> bool;
}

impl<T> DoesItBark for Dog<T> {
    fn it_barks(&self) -> bool {
        true
    }
}

struct Rectangle {
    width: u32,
    height: u32,
}

impl Rectangle {
    fn new(width: u32, height: u32) -> Self {
        Self {width, height}
    }
}

struct Square {
    length: u32,
}

impl Square {
    pub fn new(length: u32) -> Self {
        Self { length }
    }

    pub fn length(&self) -> u32 {
        self.length
    }
}

pub trait Rectangular {
    fn width(&self) -> u32;

    fn height(&self) -> u32;

    fn area(&self) -> u32;
}

impl Rectangular for Rectangle {
    fn width(&self) -> u32 {
        self.width
    }

    fn height(&self) -> u32 {
        self.height
    }

    fn area(&self) -> u32 {
        self.width * self.height
    }
}

impl Rectangular for Square {
    fn width(&self) -> u32 {
        self.length
    }

    fn height(&self) -> u32 {
        self.length
    }

    fn area(&self) -> u32 {
        self.length * self.length
    }
}

fn describe_type<T: SelfDescribing>(t: &T) -> String {
    t.describe()
}
fn describe_type_selfless<T: SelfDescribing>() -> String {
    T::describe_type()
}

pub trait SelfDescribing {
    fn describe(&self) -> String;

    fn describe_type() -> String;
}

trait MyTrait {
    fn trait_hello(&self);
}

struct MyStruct1 {}

impl MyStruct1 {
    fn struct_hello(&self) {
        println!("Hello, world! from MyStruct1");
    }
}

struct MyStruct2 {}

impl MyStruct2 {
    fn struct_hello(&self) {
        println!("Hello, world! from MyStruct2");
    }
}

impl MyTrait for MyStruct1 {
    fn trait_hello(&self) {
        self.struct_hello();
    }
}

impl MyTrait for MyStruct2 {
    fn trait_hello(&self) {
        self.struct_hello();
    }
}
