use std::{error::Error, fs};

use crate::config::Config;

pub fn run(config: Config) -> Result<(), Box<dyn Error>> {
    let contents = fs::read_to_string(config.file_path)?;

    if config.ignore_case {
        print_result(search_case_insensitive(&config.query, &contents));
    } else {
        print_result(search(&config.query, &contents));
    };

    Ok(())
}

pub fn print_result<'a, I>(res: I)
where I: Iterator<Item = &'a str>
{
    for line in res {
        println!("{line}");
    }
}

pub fn search<'a>(query: &str, contents: &'a str) -> impl Iterator<Item = &'a str> {
    contents.lines().filter(move |line| {line.contains(query)})
}

pub fn search_case_insensitive<'a>(query: &str, contents: &'a str) -> impl Iterator<Item = &'a str> {
    contents.lines().filter(|line| {line.to_lowercase().contains(&query.to_lowercase())})
}


pub mod config {
    use std::env;

    pub struct Config {
        pub file_path: String,
        pub query: String,
        pub ignore_case: bool
    }

    impl Config {
        pub fn build(mut args: impl Iterator<Item = String>) -> Result<Config, &'static str> {
            args.next();

            let Some(query) = args.next() else {
                return Err("query is not provided");
            };
            let Some(file_path) = args.next() else {
                return Err("file path is not provided");
            };
            let ignore_case = env::var("IGNORE_CASE").is_ok_and(|value| ["true", "True", "1"].contains(&&value[..]));
            Ok(Config { file_path, query, ignore_case })
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn case_sensitive() {
        let query = "duct";
        let contents = "\
Rust:
safe, fast, productive.
Duct type.
Pick three.";
        assert_eq!(search(query, contents).collect::<Vec<&str>>(), vec!["safe, fast, productive."])
    }

    #[test]
    fn case_insensitive() {
        let query = "Duct";
        let contents = "\
Rust:
safe, fast, PRODUCTIVE.
Pick three.";
        assert_eq!(search_case_insensitive(query, contents).collect::<Vec<&str>>(), vec!["safe, fast, PRODUCTIVE."])
    }
}
