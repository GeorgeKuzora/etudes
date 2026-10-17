use std::{marker::PhantomData, ops::Deref, vec::IntoIter};

#[derive(Debug)]
struct Buffer<T, const LENGTH: usize> {
    buf: [T; LENGTH],
}

impl<T, const LENGTH: usize> From<[T; LENGTH]> for Buffer<T, LENGTH> {
    fn from(value: [T; LENGTH]) -> Self {
        Buffer { buf: value }
    }
}

struct WrapperVec<T>(Vec<T>);

impl<T> Deref for WrapperVec<T> {
    type Target = Vec<T>;
    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl<T> WrapperVec<T> {
    fn into_iter(self) -> IntoIter<T> {
        self.0.into_iter()
    }
}

trait ReversedExt<T> {
    fn reversed(&self) -> Vec<T>;
}

impl<T> ReversedExt<T> for Vec<T>
where
    T: Clone,
{
    fn reversed(&self) -> Vec<T> {
        self.iter().rev().cloned().collect()
    }
}

trait DoubleEndedIteratorExt: DoubleEndedIterator {
    fn to_reversed<'a, T>(self) -> Vec<T>
    where
        T: 'a + Clone,
        Self: Sized + Iterator<Item = &'a T>;
}

impl<I: DoubleEndedIterator> DoubleEndedIteratorExt for I {
    fn to_reversed<'a, T>(self) -> Vec<T>
    where
        T: 'a + Clone,
        Self: Sized + Iterator<Item = &'a T>,
    {
        self.rev().cloned().collect()
    }
}

trait Blanket {}

impl<T> Blanket for T {}

impl<T: Default + Copy, const LENGTH: usize> From<Vec<T>> for Buffer<T, LENGTH> {
    fn from(value: Vec<T>) -> Self {
        assert_eq!(LENGTH, value.len());
        let mut ret = Buffer {
            buf: [T::default(); LENGTH],
        };
        ret.buf.copy_from_slice(&value);
        ret
    }
}

struct LightBulb<State: BulbState> {
    phantom: PhantomData<State>,
}

struct On;
struct Off;

trait BulbState {}

impl BulbState for On {}
impl BulbState for Off {}

#[derive(Debug)]
struct Student {
    name: String,
    id: u32,
}

impl Student {
    fn new(name: String, id: u32) -> Self {
        Self { name, id }
    }
    fn name(&self) -> &str {
        self.name.as_ref()
    }
    fn id(&self) -> u32 {
        self.id
    }
}

impl<'a> Student {
    fn to_ref(&'a self) -> StudentRef<'a> {
        StudentRef::new(self)
    }
}

#[derive(Debug)]
pub struct StudentList {
    students: Vec<Student>,
}

impl StudentList {
    fn new(students: &[(&str, u32)]) -> Self {
        Self {
            students: students
                .iter()
                .map(|(name, id)| Student::new((*name).into(), *id))
                .collect(),
        }
    }
}

impl<'a> StudentList {
    pub fn find_by_id(&'a self, id: u32) -> Option<StudentRef<'a>> {
        self.find(|s| s.id() == id)
    }
    pub fn find_by_name(&'a self, name: &str) -> Option<StudentRef<'a>> {
        self.find(|s| s.name() == name)
    }
    fn find<F: Fn(&&Student) -> bool>(&'a self, pred: F) -> Option<StudentRef<'a>> {
        self.students.iter().find(pred).map(Student::to_ref)
    }
}

#[derive(Debug)]
pub struct StudentRef<'a> {
    student: &'a Student,
}

impl<'a> StudentRef<'a> {
    fn new(student: &'a Student) -> Self {
        StudentRef { student }
    }
}

impl<'a> PartialEq for StudentRef<'a> {
    fn eq(&self, other: &Self) -> bool {
        self.student.id() == other.student.id()
    }
}

fn test() {
    let student = Student {
        name: "Walter".into(),
        id: 582,
    };
    let student_ref = StudentRef { student: &student };
    dbg!(&student);
    dbg!(student_ref);

    let student_list = StudentList::new(&[("Lyle", 621), ("Anna", 286)]);
    dbg!(&student_list);
    dbg!(student_list.find_by_id(621));
    dbg!(student_list.find_by_name("Anna"));

    let student_ref_621 = student_list.find_student_by_id(621).unwrap();
    let student_ref_286 = student_list.find_student_by_id(286).unwrap();
    dbg!(student_ref_286 == student_ref_621);
    dbg!(student_ref_286 != student_ref_621);
}
