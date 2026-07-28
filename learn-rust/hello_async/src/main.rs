use trpl::{Either, Html};

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let url = &args[1];
    let url1 = &args[2];
    trpl::block_on(async {run(url, url1).await});
}

async fn run(url: &str, url1: &str) {
    let title_future = page_title(url);
    let title_future1 = page_title(url1);

    let (url, maybe_title) = match trpl::select(title_future, title_future1).await {
        Either::Left(left) => left,
        Either::Right(right) => right,
    };

    println!("{url} returned first");

    match maybe_title {
        Some(title) => println!("Its page title was: '{title}'"),
        None => println!("It had no title."),
    };
}

async fn page_title(url: &str) -> (&str, Option<String>) {
    let response_text = trpl::get(url).await.text().await;
    let title = Html::parse(&response_text)
        .select_first("title")
        .map(|title| title.inner_html());
    (url, title)
}
