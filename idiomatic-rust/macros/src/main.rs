// macro_rules! noop_macro {
//     () => {}
// }

macro_rules! print_what_it_is {
    () => {
        println!("A macro with no arguments")
    };
    ($e:expr) => {
        println!("A macro with expression")
    };
    ($s:stmt) => {
        println!("A macro with statement")
    };
    ($e:expr, $s:stmt) => {
        println!("A macro with expression followed by statement")
    };
}

macro_rules! special_println {
    ($($arg:tt)*) => {
        println!("Printed_specially: {}", format!($($arg)*))
    };
}

macro_rules! var_print {
    ($($v:ident),*) => {
        println!(
            concat!($(stringify!($v),"={:?} "),*), $($v),*
        )
    };
}

fn main() {
    print_what_it_is!();
    print_what_it_is!({});
    print_what_it_is!(;);
    print_what_it_is!({}, ;);

    special_println!("hello world {}", "goodbuy world");

    let counter = 7;
    let gauge = core::f64::consts::PI;
    let name = "Peter";
    var_print!(counter, gauge, name);
}
