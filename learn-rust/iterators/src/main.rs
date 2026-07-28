fn main() {
    let v1 = vec![1, 2, 3];
    let mut v1_iter = v1.iter();

    assert_eq!(v1_iter.next(), Some(&1));
    assert_eq!(v1_iter.next(), Some(&2));
    assert_eq!(v1_iter.next(), Some(&3));
    assert_eq!(v1_iter.next(), None);

    for val in v1_iter {
        println!("got: {val}")
    }

    let v1: Vec<i32> = vec![1, 2, 3];
    let sum: i32 = v1.iter().map(|x| x + 1).sum();
    println!("{sum}");
    println!("{v1:?}")

}
