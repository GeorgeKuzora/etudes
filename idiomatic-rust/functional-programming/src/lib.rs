use std::cell::RefCell;
use std::marker::PhantomData;
use std::rc::Rc;

type ItemData<T> = Rc<RefCell<T>>;
type ListItemPtr<T> = Rc<RefCell<ListItem<T>>>;

pub struct ListItem<T> {
    pub data: ItemData<T>,
    next: Option<ListItemPtr<T>>,
}

impl<T> ListItem<T> {
    fn new(t: T) -> Self {
        Self {
            data: Rc::new(RefCell::new(t)),
            next: None,
        }
    }
}

pub struct LinkedList<T> {
    head: ListItemPtr<T>,
}

impl<'a, T> LinkedList<T> {
    pub fn new(t: T) -> Self {
        Self {
            head: Rc::new(RefCell::new(ListItem::new(t))),
        }
    }

    pub fn append(&mut self, t: T) {
        let mut next = self.head.clone();
        while next.as_ref().borrow().next.is_some() {
            let n = next
                .as_ref()
                .borrow()
                .next
                .as_ref()
                .unwrap()
                .clone();
            next = n;
        }
        next.as_ref().borrow_mut().next = Some(Rc::new(RefCell::new(ListItem::new(t))));
    }

    pub fn iter(&'a self) -> Iter<'a, T> {
        Iter {
            next: Some(self.head.clone()),
            data: None,
            phantom: PhantomData,
        }
    }

    pub fn iter_mut(&'a mut self) -> IterMut<'a, T> {
        IterMut {
            next: Some(self.head.clone()),
            data: None,
            phantom: PhantomData,
        }
    }

    pub fn into_iter(self) -> IntoIter<T> {
        IntoIter {
            next: Some(self.head.clone())
        }
    }
}

impl<'a, T> IntoIterator for &'a LinkedList<T> {
    type IntoIter = Iter<'a, T>;
    type Item = &'a T;

    fn into_iter(self) -> Self::IntoIter {
        self.iter()
    }
}

impl<'a, T> IntoIterator for &'a mut LinkedList<T> {
    type IntoIter = IterMut<'a, T>;
    type Item = &'a mut T;

    fn into_iter(self) -> Self::IntoIter {
        self.iter_mut()
    }
}

impl<T> IntoIterator for LinkedList<T> {
    type IntoIter = IntoIter<T>;
    type Item = T;

    fn into_iter(self) -> Self::IntoIter {
        self.into_iter()
    }
}

pub struct Iter<'a, T> {
    next: Option<ListItemPtr<T>>,
    data: Option<ItemData<T>>,
    phantom: PhantomData<&'a T>,
}

impl<'a, T> Iterator for Iter<'a, T> {
    type Item = &'a T;

    fn next(&mut self) -> Option<Self::Item> {
        match self.next.clone() {
            Some(ptr) => {
                self.next = ptr.as_ref().borrow().next.clone();
                self.data = Some(ptr.as_ref().borrow().data.clone());
                unsafe {Some(&*self.data.as_ref().unwrap().as_ptr())}
            },
            None => None,
        }
    }
}

pub struct IterMut<'a, T> {
    next: Option<ListItemPtr<T>>,
    data: Option<ItemData<T>>,
    phantom: PhantomData<&'a T>,
}

impl<'a, T> Iterator for IterMut<'a, T> {
    type Item = &'a mut T;

    fn next(&mut self) -> Option<Self::Item> {
        match self.next.clone() {
            Some(ptr) => {
                self.next = ptr.as_ref().borrow().next.clone();
                self.data = Some(ptr.as_ref().borrow().data.clone());
                unsafe {Some(&mut *self.data.as_ref().unwrap().as_ptr())}
            },
            None => None
        }
    }
}

pub struct IntoIter<T> {
    next: Option<ListItemPtr<T>>,
}

impl<T> Iterator for IntoIter<T> {
    type Item = T;

    fn next(&mut self) -> Option<Self::Item> {
        match self.next.clone() {
            Some(ptr) => {
                self.next = ptr.as_ref().borrow().next.clone();
                let list_item = Rc::try_unwrap(ptr).map(|refcel| refcel.into_inner());
                match list_item {
                    Ok(listitem) => Rc::try_unwrap(listitem.data)
                        .map(|refcell| refcell.into_inner())
                        .ok(),
                    Err(_) => None,
                }
            }
            None => None
        }
    }
}
