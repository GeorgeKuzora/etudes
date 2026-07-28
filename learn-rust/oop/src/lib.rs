pub trait Draw {
    fn draw(&self);
}

pub struct Screen {
    pub components: Vec<Box<dyn Draw>>,
}

impl Screen {
    pub fn run(&self) {
        for component in self.components.iter() {
            component.draw();
        }
    }
}

pub struct Button {
    height: u32,
    width: u32,
    label: String,
}

impl Draw for Button {
    fn draw(&self) {
        println!("height: {}, width: {}, label: {}", self.height, self.width, self.label);
    }
}
