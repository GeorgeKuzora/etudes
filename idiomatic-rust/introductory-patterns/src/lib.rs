use std::path::Path;

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
    
}