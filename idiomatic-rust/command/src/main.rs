use std::{fs::File, io::{BufRead, BufReader, Error, Seek, Write}};

trait Command {
    fn execute(&self) -> Result<(), Error>;
}

struct ReadFile {
    receiver: File,
}

impl ReadFile {
    fn new(file: File) -> Box<Self> {
        Box::new(Self { receiver: file })
    }
}

impl Command for ReadFile {
    fn execute(&self) -> Result<(), Error> {
        println!("Reading from the start of the file");
        let mut reader = BufReader::new(&self.receiver);
        reader.seek(std::io::SeekFrom::Start(0))?;
        for (count, line) in reader.lines().enumerate() {
            println!("{:2}: {}", count + 1, line?);
        }
        Ok(())
    }
}

struct WriteFile {
    receiver: File,
    content: String,
}

impl WriteFile {
    fn new(receiver: File, content: String) -> Box<Self> {
        Box::new(Self { content, receiver })
    }
}

impl Command for WriteFile {
    fn execute(&self) -> Result<(), Error> {
        println!("Writing new content to file");
        let mut writer = self.receiver.try_clone()?;
        writer.write_all(self.content.as_bytes())?;
        writer.flush()?;
        Ok(())
    }
}

fn main() -> Result<(), Error>{
    let file = File::options()
        .read(true)
        .write(true)
        .create(true)
        .append(true)
        .open("hidden_file.txt")?;

    let commands: Vec<Box<dyn Command>> = vec![
        ReadFile::new(file.try_clone()?),
        WriteFile::new(file.try_clone()?, "file content\n".into()),
        ReadFile::new(file.try_clone()?),
    ];

    for command in commands {
        command.execute()?;
    }
    Ok(())
}
