use std::error::Error;
use::std::fs::File;
use::std::io::{ErrorKind, self, Read};

fn main() -> Result<(), Box<dyn Error>> {
    let greetings = File::open("hello.txt");

    let f = match greetings {
        Ok(file) => file,
        Err(error) => match error.kind() {
            ErrorKind::NotFound => match File::create("hello.txt") {
                Ok(fc) => fc,
                Err(e) => panic!("cannot create a file {e:?}"),
            },
        _ => panic!("Problem opening the file: {error:?}"),
        },
    };
    Ok(())
}

fn read_username_from_file(filename: &str) -> Result<String, io::Error> {
    let username_file_result = File::open(filename);

    let mut username_file = match username_file_result {
        Ok(file) => file,
        Err(e) => return Err(e),
    };

    let mut username = String::new();

    match username_file.read_to_string(&mut username) {
        Ok(_) => Ok(username),
        Err(e) => Err(e),
    }
}

fn open_and_read_username_from_file_fucntional(filename: &str) -> Result<String, io::Error> {
    File::open(filename).and_then(read_from_file)
}

fn read_from_file(mut file: File) -> Result<String, io::Error> {
    let mut contents = String::new();
    file.read_to_string(&mut contents)?;
    Ok(contents)
}
