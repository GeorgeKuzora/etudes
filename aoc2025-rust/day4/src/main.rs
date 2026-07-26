use std::{fs::read_to_string, str};

const ROLL_OF_PAPER: u8 = b'@';
const EMPTY_SPACE: u8 = b'.';

struct Coordinates {
    x: isize,
    y: isize,
}

impl Coordinates {
    fn mv(&self, offset: &Offset) -> Self {
        let Offset(x, y) = offset;
        let x = self.x + x;
        let y = self.y + y;
        Coordinates { x: x, y: y }
    }
}

struct Offset(isize, isize);

const OFFSETS: [Offset; 8] = [
    Offset(-1, -1), Offset(0, -1), Offset(1, -1),
    Offset(-1, 0),                 Offset(1, 0),
    Offset(-1, 1),  Offset(0, 1),  Offset(1, 1),
];

struct Grid<'a> {
    data: Vec<&'a u8>,
    width: usize,
    height: usize,
}

impl<'a> Grid<'a> {
    fn new(data: Vec<&'a u8>, width: usize, height: usize) -> Self {
        Grid { data, width, height }
    }

    fn get(&self, address: &Coordinates) -> Option<&'a u8> {
        if !self.in_bounds(address) {
            None
        } else {
            let id = self.width * address.y as usize + address.x as usize;
            Some(self.data[id])
        }

    }

    fn is_accessible(&self, address: &Coordinates) -> Option<bool> {
        if !self.in_bounds(address) {
            return None;
        }

        let adjacent_count = OFFSETS.iter().filter(|offset| {
            let new_address = address.mv(offset);
            if let Some(item) = self.get(&new_address) {
                if item == &EMPTY_SPACE { false } else { true }
            } else { false }
        }).count();

        Some(adjacent_count < 4)

    }

    fn in_bounds(&self, address: &Coordinates) -> bool {
        address.x >= 0
        && address.y >= 0
        && (address.x as usize) < self.width
        && (address.y as usize) < self.height
    }

}

fn main() {
    let input = read_to_string("input.txt").expect("file should be in path");

    let width = input.lines().next().map_or(0, str::len);
    let height = input.lines().count();

    let data: Vec<&u8> = input.lines().flat_map(str::as_bytes).collect();

    let grid = Grid::new(data, width, height);

    let coordinates = (0..height).flat_map(|y| {
        (0..width).map(move |x| Coordinates{ x: x as isize, y: y as isize })
    });

    let accessible_count = coordinates.filter(|address| {
        match grid.get(address) {
            Some(item) => {
                if item == &ROLL_OF_PAPER {
                    match grid.is_accessible(address) {
                        Some(is_accessible) => is_accessible,
                        None => false,
                    }
                } else {
                    false
                }
            },
            None => false,
        }
    }).count();

    println!("Count for accessible rolls without moving: {accessible_count}")
}
