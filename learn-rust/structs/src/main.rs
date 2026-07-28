#[derive(Debug)]
struct User {
    active: bool,
    username: String,
    email: String,
    sing_in_count: u64,
}

struct Color(i32, i32, i32);

struct AlwaysEqual;


fn main() {
    let mut user = User {
        active: true,
        username: String::from("user"),
        email: String::from("user@email.com"),
        sing_in_count: 0,
    };

    let user2 = User {
        username: String::from("user1"),
        email: String::from("email"),
        ..user
    };

    println!("{:?}", user);

    let black = Color(0, 0, 0);

    let subject = AlwaysEqual;
}
