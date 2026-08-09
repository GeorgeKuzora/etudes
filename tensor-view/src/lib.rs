pub struct TensorView<'a> {
    data: &'a Vec<f32>,
    cols: usize,
    rows: usize
}

impl<'a> TensorView<'a> {
    fn new(data: &'a Vec<f32>, cols: usize, rows: usize) -> Self {
        Self { data, cols, rows }
    }


}

#[cfg(test)]
mod tests {
    use crate::TensorView;


    #[test]
    fn tensor_test() {
        let data: Vec<f32> = vec![1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0];
        let tensor_view = TensorView::new(&data, 2, 2);
        assert_eq!(4, 4);
    }
}
