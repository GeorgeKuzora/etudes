use std::fmt::Display;

use crate::summary::{SocialPost, Summary};

struct Point<T: PartialOrd> {
    x: T,
    y: T,
}

impl<T: PartialOrd> Point<T> {
    fn x(&self) -> &T {
        &self.x
    }
}

struct ImportantExcerpt<'a> {
    part: &'a str
}

impl<'a> ImportantExcerpt<'a> {
    fn level(&self) -> i32 {
        3
    }

    fn announce_and_return_part(&self, announcement: &str) -> &str {
        println!("Attention please: {announcement}");
        self.part
    }
}

const s: &'static str = "I have a static lifetime.";

fn main() {
    let s: &'static str = "I have a static lifetime.";
    let number_list = vec![1, 2, 3, 4, 5];

    let l = largest(&number_list);

    println!("The largest number is {l}");

    let integer = Point{x: 1, y: 2};
    let float = Point{x: 1.5, y: 2.5};
    let post = SocialPost {
        username: String::from("horse_ebooks"),
        content: String::from(
            "of course, as you probably already know, people",
        ),
        reply: false,
        repost: false,
    };

    println!("summary: {}", post.summarize());

    let result;
    let string1 = String::from("abcd");

    {
        let string2 = "xyz";
        result = longest(string1.as_str(), string2);
    }

    println!("{result}");

    let novel = String::from("Call me Ishmael. Some years ago...");
    let first_sentence = novel.split('.').next().unwrap();
    let i = ImportantExcerpt {
        part: first_sentence,
    };
}

fn longest<'a>(s1: &'a str, s2: &'a str) -> &'a str {
    if s1.len() >= s2.len() {s1} else {s2}
}

fn largest<T: PartialOrd>(v: &[T]) -> &T {
    let mut largest = &v[0];

    for number in v {
        if number > largest {
            largest = number;
        }
    }
    return largest
}
mod summary {
    pub trait Summary {
        fn summarize(&self) -> String {
            format!("(Read more... from author {})", self.summarize_author())
        }
        fn summarize_author(&self) -> String;
    }

    pub struct NewsArticle {
        pub headline: String,
        pub location: String,
        pub author: String,
        pub content: String,
    }

    impl Summary for NewsArticle {
        fn summarize(&self) -> String {
            format!("{}, by {} ({})", self.headline, self.author, self.location)
        }

        fn summarize_author(&self) -> String {
            format!("@{}", self.author)
        }
    }

    pub struct SocialPost {
        pub username: String,
        pub content: String,
        pub reply: bool,
        pub repost: bool,
    }

    impl Summary for SocialPost {
        fn summarize(&self) -> String {
            format!("{}: {}", self.username, self.content)
        }

        fn summarize_author(&self) -> String {
            format!("@{}", self.username)
        }
    }

}

pub fn notify(item: &(impl Summary + Display)) {
    println!("Breaking news: {}", item.summarize())
}
