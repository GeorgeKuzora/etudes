use std::{sync::{Arc, Condvar, Mutex}, thread};
use lazy_static::lazy_static;
use once_cell::sync::Lazy;

fn main() {
    let outer = Arc::new(
        (Mutex::new(0), Condvar::new())
    );
    let inner = outer.clone();

    thread::spawn(move || {
        let (mutex, cond_var) = &*inner;
        let mut guard = mutex.lock().unwrap();
        *guard += 1;
        println!("inner_guard={guard}");
        cond_var.notify_one();
    });

    let (mutex, cond_var) = &*outer;

    let mut guard = mutex.lock().unwrap();
    println!("outer before wait guard={guard}");
    while *guard == 0 {
        guard = cond_var.wait(guard).unwrap();
    }

    println!("outer after wait guard={guard}");

    let arc = POPULAR_BABY_NAMES_2021.with(|arc| arc.clone());
    let mut inner = arc.lock().expect("cannot lock the mutex");
    *inner = Some(vec![
        String::from("Olivia"),
        String::from("Liam"),
        String::from("Emma"),
        String::from("Noah"),
    ]);

    println!("popular baby names of 2020: {:?}", *POPULAR_BABY_NAMES_2020);
    println!("popular baby names of 2022: {:?}", *POPULAR_BABY_NAMES_2022);
}

thread_local! {
    static POPULAR_BABY_NAMES_2021: Arc<Mutex<Option<Vec<String>>>> = Arc::new(Mutex::new(None));
}

lazy_static! {
    static ref POPULAR_BABY_NAMES_2020: Vec<String> = {
        vec![
            String::from("Olivia"),
            String::from("Liam"),
            String::from("Emma"),
            String::from("Noah"),
        ]
    };
}

static POPULAR_BABY_NAMES_2022: Lazy<Vec<String>> = Lazy::new(|| {
    vec![
        String::from("Olivia"),
        String::from("Liam"),
        String::from("Emma"),
        String::from("Noah"),
    ]
});
