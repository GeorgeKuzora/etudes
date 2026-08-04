use std::fmt::Display;

fn main() {
    println!("Hello, world!");
}

fn some_or_none<T: Display>(option: &Option<T>) {
    match option {
        Some(v) => println!("some {v}"),
        None => println!("none"),
    }
}

fn what_type_of_integer_it_is(value: i32) {
    match value {
        1 => println!("this is the one"),
        2 | 3 => println!("two or three"),
        4..=10 => println!("4 through 10"),
        _ => println!("other number"),
    }
}

fn destructive_tuple(tuple: &(i32, i32, i32)) {
    match tuple {
        (first, ..) => println!("first element is {first}"),
    }
    match tuple {
        (.., last) => println!("last element is {last}"),
    }
    match tuple {
        (_, middle, _) => println!("middle element is {middle}"),
    }
    match tuple {
        (first, middle, last) => println!("{first} {middle} {last}"),
    }
}

fn match_with_guard(value: i32, choose_first: bool) {
    match value {
        v if v == 1 && choose_first => println!("First match: value = 1"),
        v if v == 1 && !choose_first => println!("Second match: value = 1"),
        v if choose_first => println!("First match: value = {v}"),
        v if !choose_first => println!("Second match: value = {v}"),
        _ => println!("Didn't match"),
    }
}

enum CatColor {
    Black,
    Red,
}

struct Cat {
    name: String,
    color: CatColor,
}

fn match_on_black_cat(cat: Cat) {
    match cat {
        Cat {
            name,
            color: CatColor::Black,
        } => println!("{name} is Black"),
        Cat{name, color: _} => println!("{name} isn't Black"),
    }
}

fn write_to_file() -> Result<(), ErrorWrapper> {
    use std::fs::File;
    use std::io::prelude::*;

    let mut file = File::create("filename")?;
    file.write_all(b"content")?;
    Ok(())
}

fn write_to_file_func() -> Result<(), ErrorWrapper> {
    use std::fs::File;
    use std::io::prelude::*;

    File::create("filename")
        .map_err(|e| ErrorWrapper::from(e))
        .and_then(|mut file| Ok( file.write_all(b"contetn")?))
}

fn try_to_write_to_file() {
    match write_to_file() {
        Ok(()) => println!("write success"),
        Err(err) => println!("write error {}", err.message),
    }
}

enum ErrorTypes {
    IoError(std::io::Error),
    FormatError(std::fmt::Error),
}

struct ErrorWrapper {
    source: ErrorTypes,
    message: String,
}

impl From<std::io::Error> for ErrorWrapper {
    fn from(value: std::io::Error) -> Self {
        Self {
            message: format!("IO error: {}", value.to_string()),
            source: ErrorTypes::IoError(value),
        }
    }
}
