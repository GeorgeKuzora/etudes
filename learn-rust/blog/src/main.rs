use blog::{idiomatic::{self, ApproveResult}, oop};

fn main() {
    let mut post = oop::Post::new();

    post.add_text("I ate a salad for lunch today");
    assert_eq!("", post.content());

    post.request_review();
    assert_eq!("", post.content());

    post.add_text("I ate a salad for lunch today");
    assert_eq!("", post.content());

    post.approve();
    assert_eq!("", post.content());

    post.reject();
    assert_eq!("", post.content());

    post.add_text("!");
    assert_eq!("", post.content());

    post.request_review();
    assert_eq!("", post.content());

    post.approve();
    assert_eq!("", post.content());

    post.approve();
    assert_eq!("I ate a salad for lunch today!", post.content());

    let mut post = idiomatic::Post::new();
    post.add_text("I ate a salad for lunch today");

    let post = post.request_review();

    let approve_result = post.approve();

    match approve_result {
        ApproveResult::Published(post) => {
            println!("Опубликовано: {}", post.content());
        }
        ApproveResult::Pending(pending) => {
            println!("Всё ещё на ревью");
            let result2 = pending.approve();
            match result2 {
                ApproveResult::Published(post) => {
                    println!("Теперь опубликовано: {}", post.content());
                }
                ApproveResult::Pending(_) => {
                    println!("Всё ещё на ревью");
                }
            }
        }
    }
}
