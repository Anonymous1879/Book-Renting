import React, { useState, useEffect } from 'react';
import {
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    Button,
    Typography,
    TextField,
} from '@mui/material';
import { getMyBooks, createBook } from '../services/api';

const MyBooks = () => {
    const [books, setBooks] = useState([]);
    const [newBook, setNewBook] = useState({
        title: '',
        author: '',
        isbn: '',
        price_per_day: '',
    });

    useEffect(() => {
        loadBooks();
    }, []);

    const loadBooks = async () => {
        try {
            const response = await getMyBooks();
            setBooks(response.data);
        } catch (error) {
            console.error('Error loading books:', error);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setNewBook((prev) => ({ ...prev, [name]: value }));
    };

    const handleAddBook = async () => {
        try {
            await createBook(newBook);
            setNewBook({ title: '', author: '', isbn: '', price_per_day: '' });
            loadBooks();
        } catch (error) {
            console.error('Error adding book:', error);
        }
    };

    return (
        <div>
            <Typography variant="h4" gutterBottom>
                My Books
            </Typography>

            <div>
                <TextField
                    label="Title"
                    name="title"
                    value={newBook.title}
                    onChange={handleInputChange}
                    margin="normal"
                />
                <TextField
                    label="Author"
                    name="author"
                    value={newBook.author}
                    onChange={handleInputChange}
                    margin="normal"
                />
                <TextField
                    label="ISBN"
                    name="isbn"
                    value={newBook.isbn}
                    onChange={handleInputChange}
                    margin="normal"
                />
                <TextField
                    label="Price Per Day"
                    name="price_per_day"
                    type="number"
                    value={newBook.price_per_day}
                    onChange={handleInputChange}
                    margin="normal"
                />
                <Button variant="contained" color="primary" onClick={handleAddBook}>
                    Add Book
                </Button>
            </div>

            <TableContainer component={Paper}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>Title</TableCell>
                            <TableCell>Author</TableCell>
                            <TableCell>ISBN</TableCell>
                            <TableCell>Price Per Day</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {books.map((book) => (
                            <TableRow key={book.book_id}>
                                <TableCell>{book.title}</TableCell>
                                <TableCell>{book.author}</TableCell>
                                <TableCell>{book.isbn}</TableCell>
                                <TableCell>${book.price_per_day}</TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
        </div>
    );
};

export default MyBooks;
