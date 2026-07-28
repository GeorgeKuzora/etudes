use std::{pin::{Pin, pin}, thread, time::Duration};

use trpl::{Either, StreamExt};

fn main() {
    trpl::block_on(
        async {
            let handle = trpl::spawn_task(async {
                for i in 1..10 {
                    println!("hi number {i} from the first task!");
                    trpl::sleep(Duration::from_millis(1)).await;
                }
            });

            for i in 1..5 {
                println!("hi number {i} from the second task!");
                trpl::sleep(Duration::from_millis(1)).await;
            }
            handle.await.unwrap();

            run().await;
        }
    );
}

async fn run() {
    let fut1 = async {
        for i in 1..10 {
            println!("hi number {i} from the first task!");
            trpl::sleep(Duration::from_millis(1)).await;
        }
    };
    let fut2 = async {
        for i in 1..5 {
            println!("hi number {i} from the second task!");
            trpl::sleep(Duration::from_millis(1)).await;
        }
    };

    trpl::join(fut1, fut2).await;

    let (tx, mut rx) = trpl::channel();

    let vals = vec![
        String::from("hi"),
        String::from("from"),
        String::from("the"),
        String::from("future"),
    ];

    let tx1 = tx.clone();
    let send_fut1 = async move {
        for val in vals {
            tx1.send(val).unwrap();
            trpl::sleep(Duration::from_millis(1)).await;
        };
    };

    let vals = vec![
        String::from("more"),
        String::from("messages"),
        String::from("for"),
        String::from("you"),
    ];

    let send_fut = async move {
        for val in vals {
            tx.send(val).unwrap();
            trpl::sleep(Duration::from_millis(1)).await;
        };
    };

    let recv_fut = async {
        loop {
            match rx.recv().await {
                Some(value) => println!("received '{value}'"),
                None => { println!("received None"); break },
            }
        }
    };

    trpl::join!(send_fut1, send_fut, recv_fut);


    let a = async {
        println!("'a' started.");
        slow("a", 30);
        trpl::yield_now().await;
        slow("a", 10);
        trpl::yield_now().await;
        slow("a", 20);
        trpl::yield_now().await;
        println!("'a' finished.");
    };

    let b = async {
        println!("'b' started.");
        slow("b", 75);
        trpl::yield_now().await;
        slow("b", 10);
        trpl::yield_now().await;
        slow("b", 15);
        trpl::yield_now().await;
        slow("b", 350);
        trpl::yield_now().await;
        println!("'b' finished.");
    };

    trpl::select(a, b).await;

    let slow = async {
        trpl::sleep(Duration::from_secs(5)).await;
        "Finally finished"
    };

    match timeout(slow, Duration::from_secs(2)).await {
        Ok(message) => println!("Succeeded with '{message}'"),
        Err(duration) => println!("Failed after {} seconds", duration.as_secs()),
    }


    let values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
    let iter = values.iter().map(|x| x * 2);
    let mut stream = trpl::stream_from_iter(iter);

    while let Some(value) = stream.next().await {
        println!("The value was: {value}");
    }


    let fut1 = pin!(async {
        for i in 1..10 {
            println!("hi number {i} from the first task!");
            trpl::sleep(Duration::from_millis(1)).await;
        }
    });
    let fut2 = pin!(async {
        for i in 1..5 {
            println!("hi number {i} from the second task!");
            trpl::sleep(Duration::from_millis(1)).await;
        }
    });
    let fut3 = pin!(async {
        for i in 1..5 {
            println!("hi number {i} from the second task!");
            trpl::sleep(Duration::from_millis(1)).await;
        }
    });

    let futures: Vec<Pin<&mut dyn Future<Output = ()>>> = vec![
        fut1,
        fut2,
        fut3,
    ];
    trpl::join_all(futures);


    let (tx, mut rx) = trpl::channel();

    thread::spawn(move || {
        for i in 1..11 {
            tx.send(i).unwrap();
            thread::sleep(Duration::from_secs(1));
        }
    });

    trpl::block_on(async {
        while let Some(message) = rx.recv().await {
            println!("{message}");
        }
    });
}

async fn timeout<F: Future>(func: F, max_time: Duration) -> Result<F::Output, Duration> {
    match trpl::select(func, trpl::sleep(max_time)).await {
        Either::Left(output) => Ok(output),
        Either::Right(_) => Err(max_time),
    }
}

fn slow(name: &str, ms: u64) {
    thread::sleep(Duration::from_millis(ms));
    println!("'{name}' ran for {ms}ms");
}
