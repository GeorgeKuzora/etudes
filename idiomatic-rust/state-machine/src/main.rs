use state_machine::Session;

fn main() {
    let session = Session::new();
    println!("{:?}", session);
    if let Ok(mut session) = session.authenticate("username", "password") {
        session.update_property("key", "value");
        println!("{:?}", session);
        let session = session.logout();
        println!("{:?}", session);
    }
}
