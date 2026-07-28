#[derive(Debug)]
enum UsState {
    Alaska,
    Alabama,
}

impl UsState {
    fn existed_in(&self, year: u16) -> bool {
        match self {
            UsState::Alabama => year >= 1819,
            UsState::Alaska => year >= 1959,
        }
    }
}

fn describe_state_quater(coin: Coin) -> Option<String> {
    let Coin::Quarter(state) = coin else {
        return None;
    };

    if state.existed_in(1900) {
        Some(format!("{state:?} is old"))
    } else {
        Some(format!("{state:?} is new"))
    }
}

enum Coin {
    Penny,
    Nickel,
    Dime,
    Quarter(UsState),
}

impl Coin {
    fn value_in_cents(coin: Coin) -> u32 {
        match coin {
            Coin::Penny => 1,
            Coin::Nickel => 5,
            Coin::Dime => 10,
            Coin::Quarter(state) => {
                println!("State quarter from {state:?}");
                25
            },
        }
    }
}


enum IpAddrKind {
    V4(u8, u8, u8, u8),
    V6(String),
}

enum Message {
    Quit,
    Move { x: i32, y: i32 },
    Write(String),
    ChangeColor(i32, i32, i32),
}

impl Message {
    fn call(&self) {
        match self {
            Self::Quit => (),
            Self::Move { x, y } => (),
            Self::Write(_) => (),
            Self::ChangeColor(_, _, _) => ()
        }
    }
}

fn fn_option(opt: Option<i32>) {
    match opt {
        Some(x) => println!("{x}"),
        None => println!("None"),
    }
}

fn div(x: i32, y: i32) -> Option<i32> {
    if y == 0 {
        return None;
    }
    Some(x / y)
}

fn route(ip: &IpAddrKind) {
    let addr = match ip {
         IpAddrKind::V4(a, b, c, d) => format!("{}.{}.{}.{}", a, b, c ,d),
         IpAddrKind::V6(v) => v.to_string(),
     };
    println!("{addr}");
}

fn main() {
    let four = IpAddrKind::V4(127, 0, 0, 1);
    let six = IpAddrKind::V6(String::from("v6"));

    route(&four);
    route(&six);

    route(&four);

    let x = div(1, 0);

    let config_max = Some(3u8);

    match config_max {
        Some(max) => println!("The maximum is configured to be {max}"),
        _ => (),
    }

    if let Some(max) = config_max {
        println!("The maximum is configured to be {max}");
    }
}

