#[derive(Debug)]
struct Rectangle {
    width: u32,
    height: u32,
}

impl Rectangle {
    fn area(&self) -> u32 {
        self.width * self.height
    }

    fn width(&self) -> bool {
        self.width > 0
    }

    fn increase(&mut self, width: u32, height: u32) {
        self.width += width;
        self.height += height;
    }

    fn can_hold(&self, other: &Rectangle) -> bool {
        self.width > other.width && self.height > other.height
    }

    fn square(size: u32) -> Self {
        Self {
            width: size,
            height: size,
        }
    }
}

fn main() {
    let mut rec = Rectangle {
        width: 30,
        height: 50,
    };

    rec.increase(10, 20);
    let area1 = rec.area();
    println!("area is: {area1}");
    println!("is width: {}", rec.width());
    dbg!(&rec);
    let square = Rectangle::square(10);
}
