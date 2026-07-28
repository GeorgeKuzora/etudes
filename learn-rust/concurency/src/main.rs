use std::{sync::{Arc, Mutex}, thread::{self, sleep}, time::Duration};
use std::sync::mpsc;

fn main() {
    let handle = thread::spawn(|| {
        for i in 1..10 {
            println!("hi number {i} from the spawned thread!");
            sleep(Duration::from_millis(1));
        }
    });

    for i in 1..5 {
        println!("hi number {i} from the main thread!");
        thread::sleep(Duration::from_millis(1));
    }

    handle.join().unwrap();

    let v = vec![1, 2, 3];

    let handle = thread::spawn(move || {
        println!("here is the vector {v:?}");
    });

    handle.join().unwrap();

    let (tx, rx) = mpsc::channel();

    let tx0 = tx.clone();
    thread::spawn(move || {
        let val = String::from("hi");
        tx0.send(val).unwrap();
    });

    let received = rx.recv().unwrap();
    println!("Got: {received}");

    let tx1 = tx.clone();
    thread::spawn(move || {
        let vals = vec![
            String::from("hi"),
            String::from("from"),
            String::from("the"),
            String::from("thread"),
        ];

        for val in vals {
            tx1.send(val).unwrap();
            thread::sleep(Duration::from_millis(1));
        };
    });

    thread::spawn(move || {
        let vals = vec![
            String::from("more"),
            String::from("messages"),
            String::from("for"),
            String::from("you"),
        ];

        for val in vals {
            tx.send(val).unwrap();
            thread::sleep(Duration::from_millis(1));
        }
    });

    for received in rx {
        println!("Got: {received}");
    }

    let m = Mutex::new(5);


    {
        let num = m.lock().unwrap();
        println!("Mutex before thread: {num}");
    }
    {
        let mut num = m.lock().unwrap();
        *num = 6;
        println!("Mutex changed before thread: {num}");
    }

    let arc_m = Arc::new(m);
    let thread_m = arc_m.clone();
    let handle = thread::spawn(move || {
        let mut num = thread_m.lock().unwrap();
        *num = 7;
        println!("Mutex inside thread: {num}");
    });

    {
        thread::sleep(Duration::from_millis(5));
        let mut num = arc_m.lock().unwrap();
        *num = 8;
        println!("Mutex changed after thread: {num}");
    }

    handle.join().unwrap();

    let num = arc_m.lock().unwrap();
    println!("Mutex final state: {num}");


    let counter = Arc::new(Mutex::new(0));
    let mut handles = vec![];

    for _ in 0..10 {
        let counter = Arc::clone(&counter);
        let handle = thread::spawn(move || {
            let mut num = counter.lock().unwrap();
            *num += 1;
        });
        handles.push(handle);
    };

    for h in handles {
        h.join().unwrap();
    };

    println!("Result: {}", *counter.lock().unwrap());

    let handle = thread::spawn(|| {
        1+1
    });
    let v: i32 = handle.join().unwrap();
    println!("{v}")
}
