pub mod oop {
    pub struct Post {
        state: Option<Box<dyn State>>,
        content: String,
    }

    impl Post {
        pub fn new() -> Post {
            Post {
                state: Some(Box::new(Draft {})),
                content: (String::new()),
            }
        }

        pub fn add_text(&mut self, text: &str) {
            self.content = self.state.as_ref().unwrap().add_text(&self.content, text);
        }

        pub fn content(&self) -> &str {
            self.state.as_ref().unwrap().content(self)
        }

        pub fn request_review(&mut self) {
            if let Some(s) = self.state.take() {
                self.state = Some(s.request_review())
            }
        }

        pub fn approve(&mut self) {
            if let Some(s) = self.state.take() {
                self.state = Some(s.approve())
            }
        }

        pub fn reject(&mut self) {
            if let Some(s) = self.state.take() {
                self.state = Some(s.reject())
            }
        }
    }

    trait State {
        fn request_review(self: Box<Self>) -> Box<dyn State>;

        fn approve(self: Box<Self>) -> Box<dyn State>;

        fn reject(self: Box<Self>) -> Box<dyn State>;

        fn content<'a>(&self, _post: &'a Post) -> &'a str {
            ""
        }

        fn add_text(&self, post: &str, _text: &str) -> String {
            String::from(post)
        }
    }

    struct Draft {}

    impl State for Draft {
        fn request_review(self: Box<Self>) -> Box<dyn State> {
            Box::new(PendingReview {approve_count: 0, required_approves: 2})
        }

        fn approve(self: Box<Self>) -> Box<dyn State> {
            self
        }

        fn reject(self: Box<Self>) -> Box<dyn State> {
            self
        }

        fn add_text(&self, post: &str, text: &str) -> String {
            let mut post = String::from(post);
            post.push_str(text);
            post
        }
    }

    struct PendingReview {
        approve_count: u32,
        required_approves: u32,
    }

    impl State for PendingReview {
        fn request_review(self: Box<Self>) -> Box<dyn State> {
            self
        }

        fn approve(mut self: Box<Self>) -> Box<dyn State> {
            self.approve_count += 1;
            if self.approve_count >= self.required_approves{
                Box::new(Published {})
            } else {
                self
            }
        }

        fn reject(self: Box<Self>) -> Box<dyn State> {
            Box::new(Draft {})
        }
    }

    struct Published {}

    impl State for Published {
        fn request_review(self: Box<Self>) -> Box<dyn State> {
            self
        }

        fn approve(self: Box<Self>) -> Box<dyn State> {
            self
        }

        fn reject(self: Box<Self>) -> Box<dyn State> {
            self
        }

        fn content<'a>(&self, post: &'a Post) -> &'a str {
            &post.content
        }
    }
}

pub mod idiomatic {
    pub struct Post {
        content: String,
    }

    pub struct DraftPost {
        content: String,
    }

    impl Post {
        pub fn new() -> DraftPost {
            DraftPost { content: String::new() }
        }

        pub fn content(&self) -> &str {
            &self.content
        }
    }

    impl DraftPost {
        pub fn add_text(&mut self, text: &str) {
            self.content.push_str(text);
        }

        pub fn request_review(self) -> PendingReviewPost {
            PendingReviewPost {
                content: self.content,
                approve_count: 0,
                required_approves: 2,
            }
        }
    }

    pub struct PendingReviewPost {
        content: String,
        approve_count: u32,
        required_approves: u32,
    }

    impl PendingReviewPost {
        pub fn approve(mut self) -> ApproveResult {
            self.approve_count += 1;

            if self.approve_count < self.required_approves {
                ApproveResult::Pending(self)
            } else {
                ApproveResult::Published(Post { content: self.content })
            }
        }

        pub fn reject(self) -> DraftPost {
            DraftPost { content: self.content }
        }
    }

    pub enum ApproveResult {
        Published(Post),
        Pending(PendingReviewPost),
    }

    impl ApproveResult {
        pub fn is_published(&self) -> bool {
            matches!(self, ApproveResult::Published(_))
        }
    }
}
