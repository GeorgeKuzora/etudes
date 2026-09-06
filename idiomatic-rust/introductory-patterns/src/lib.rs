use std::{path::Path};

#[derive(Debug)]
pub enum Error {
    Io(std::io::Error),
    BadlineArgument(usize),
}

impl From<std::io::Error> for Error {
    fn from(value: std::io::Error) -> Self {
        Self::Io(value)
    }
}

fn read_nth_line(path: &Path, n: usize) -> Result<String, Error> {
    if n < 1 {
        return Err(Error::BadlineArgument(n))
    }

    use std::fs::File;
    use std::io::{BufRead, BufReader};
    let file = File::open(path)?;

    let mut reader_lines = BufReader::new(file).lines();

    reader_lines
        .nth(n-1)
        .map(|result| result.map_err(|err| err.into()))
        .unwrap_or_else(||Err(Error::BadlineArgument(n)))
}





#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_can_read_cargotoml() {
        let third_line = read_nth_line(Path::new("Cargo.toml"), 3)
            .expect("unable to read third line from Cargo.toml");
        assert_eq!("version = \"0.1.0\"", third_line);
    }

    #[test]
    fn test_not_a_file() {
        let err = read_nth_line(Path::new("not_a_file"), 1)
            .expect_err("file should not exist");
        assert!(matches!(err, Error::Io(_)));
    }

    #[test]
    fn test_bad_arg_0() {
        let err = read_nth_line(Path::new("Cargo.toml"), 0)
            .expect_err("0th line is invalid");
        assert!(matches!(err, Error::BadlineArgument(_)));

    }

    #[test]
    fn test_bad_arg_500() {
        let err = read_nth_line(Path::new("Cargo.toml"), 500)
            .expect_err("500th line is invalid");
        assert!(matches!(err, Error::BadlineArgument(_)));
    }
}
