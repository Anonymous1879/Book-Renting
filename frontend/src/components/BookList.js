import React, { useState, useEffect } from 'react';
import { 
    Grid, 
    Card, 
    CardContent, 
    CardMedia, 
    Typography, 
    Button,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField
} from '@mui/material';
import { getAvailableBooks, requestRental } from '../services/api';

const BookList = () => {
    const [books, setBooks] = useState([]);
    const [selectedBook, setSelectedBook] = useState(null);
    const [rentalDays, setRentalDays] = useState(7);
    const [open, setOpen] = useState(false);

    useEffect(() => {
        loadBooks();
    }, []);

    const loadBooks = async () => {
        try {
            const response = await getAvailableBooks();
            setBooks(response.data);
        } catch (error) {
            console.error('Error loading books:', error);
        }
    };

    const handleRentClick = (book) => {
        setSelectedBook(book);
        setOpen(true);
    };

    const handleClose = () => {
        setOpen(false);
        setSelectedBook(null);
        setRentalDays(7);
    };

    const handleRent = async () => {
        try {
            await requestRental(selectedBook.id, rentalDays);
            loadBooks();
            handleClose();
        } catch (error) {
            console.error('Error renting book:', error);
        }
    };

    return (
        <div>
            <Typography variant="h4" gutterBottom>
                Available Books
            </Typography>
            <Grid container spacing={3}>
                {books.map((book) => (
                    <Grid item xs={12} sm={6} md={4} key={book.id}>
                        <Card>
                            {book.cover_image && (
                                <CardMedia
                                    component="img"
                                    height="200"
                                    image={book.cover_image}
                                    alt={book.title}
                                />
                            )}
                            <CardContent>
                                <Typography variant="h6" component="div">
                                    {book.title}
                                </Typography>
                                <Typography variant="subtitle1" color="text.secondary">
                                    {book.author}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    Available copies: {book.available_copies}
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    Price per day: ${book.price_per_day}
                                </Typography>
                                <Button 
                                    variant="contained" 
                                    color="primary"
                                    onClick={() => handleRentClick(book)}
                                    sx={{ mt: 1 }}
                                >
                                    Rent Book
                                </Button>
                            </CardContent>
                        </Card>
                    </Grid>
                ))}
            </Grid>

            <Dialog open={open} onClose={handleClose}>
                <DialogTitle>Rent Book</DialogTitle>
                <DialogContent>
                    <Typography variant="body1" gutterBottom>
                        {selectedBook?.title}
                    </Typography>
                    <TextField
                        autoFocus
                        margin="dense"
                        label="Number of Days"
                        type="number"
                        fullWidth
                        value={rentalDays}
                        onChange={(e) => setRentalDays(Number(e.target.value))}
                        inputProps={{ min: 1 }}
                    />
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                        Total Price: ${selectedBook?.price_per_day * rentalDays}
                    </Typography>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleClose}>Cancel</Button>
                    <Button onClick={handleRent} variant="contained" color="primary">
                        Confirm Rental
                    </Button>
                </DialogActions>
            </Dialog>
        </div>
    );
};

export default BookList; 