use std::ops::Range;

#[derive(Debug)]
enum TensorError {
    ShapeMismatch(&'static str),
    SliceOutOfBounds(&'static str),
}

/// A zero-copy, strided 2D view over a contiguous 1D array.
/// `row_stride` allows for non-contiguous column slicing (like PyTorch/NumPy).
#[derive(Debug)]
pub struct TensorView<'a> {
    data: &'a [f32],
    rows: usize,
    cols: usize,
    stride: usize,
}

impl<'a> TensorView<'a> {
    fn build(data: &'a [f32], rows: usize, cols: usize) -> Result<Self, TensorError> {
        let expected_len = rows * cols;
        if data.len() < expected_len {
            return Err(TensorError::ShapeMismatch("provided data is short for the tensor" ))
        }
        Ok(Self { data, rows, cols, stride: cols})
    }

    /// Creates a zero-copy sub-view.
    /// Note: Slicing columns changes the `row_stride`, making the underlying
    /// memory non-contiguous, but the view remains zero-copy.
    fn slice(&self, col_range: Range<usize>, row_range: Range<usize>) -> Result<TensorView<'a>, TensorError> {
        if col_range.end > self.cols || row_range.end > self.rows {
            return Err(TensorError::SliceOutOfBounds("Slice range is out of bounds"));
        }

        let slice_start = row_range.start * self.stride + col_range.start;
        let slice_end = row_range.end * self.stride + col_range.end;

        let sliced_data = &self.data[slice_start..slice_end];

        let rows = row_range.end -row_range.start;
        let cols = col_range.end -col_range.start;

        let output_slice = Self {
            data: sliced_data,
            rows: rows,
            cols: cols,
            stride: self.stride,
        };

        Ok(output_slice)
    }
}

#[cfg(test)]
mod tests {
    use std::ops::Range;

    use crate::TensorView;


    #[test]
    fn tensor_test() {
        let data: Vec<f32> = vec![1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0];
        let tensor_view = TensorView::build(&data, 2, 3).unwrap();
        println!("{tensor_view:?}");

        let tensor_slice = tensor_view.slice(Range{start: 1, end: 2}, Range{start: 0, end: 1});

        println!("{tensor_slice:?}");
        assert_eq!(4, 2);
    }
}
