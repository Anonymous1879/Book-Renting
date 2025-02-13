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
    Typography
} from '@mui/material';
import { getActiveRentals, returnBook } from '../services/api';

const MyRentals = () => {
    const [rentals, setRentals] = useState([]);

    useEffect(() => {
        loadRentals();
    }, []);

    const loadRentals = async () => {
        try {
            const response = await getActiveRentals();
            setRentals(response.data);
        } catch (error) {
            console.error('Error loading rentals:', error);
        }
    };

    const handleReturn = async (rentalId) => {
        try {
            await returnBook(rentalId);
            loadRentals();
        } catch (error) {
            console.error('Error returning book:', error);
        }
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString();
    };

    return (
        <div>
            <Typography variant="h4" gutterBottom>
                My Active Rentals
            </Typography>
            <TableContainer component={Paper}>
                <Table>
                    <TableHead>
                        <TableRow>
                            <TableCell>Book Title</TableCell>
                            <TableCell>Author</TableCell>
                            <TableCell>Rental Date</TableCell>
                            <TableCell>Return Date</TableCell>
                            <TableCell>Total Price</TableCell>
                            <TableCell>Status</TableCell>
                            <TableCell>Action</TableCell>
                        </TableRow>
                    </TableHead>
                    <TableBody>
                        {rentals.map((rental) => (
                            <TableRow key={rental.id}>
                                <TableCell>{rental.book.title}</TableCell>
                                <TableCell>{rental.book.author}</TableCell>
                                <TableCell>{formatDate(rental.rental_date)}</TableCell>
                                <TableCell>{formatDate(rental.return_date)}</TableCell>
                                <TableCell>${rental.total_price}</TableCell>
                                <TableCell>{rental.status}</TableCell>
                                <TableCell>
                                    {rental.status === 'ACTIVE' && (
                                        <Button
                                            variant="contained"
                                            color="primary"
                                            onClick={() => handleReturn(rental.id)}
                                        >
                                            Return Book
                                        </Button>
                                    )}
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </TableContainer>
        </div>
    );
};

export default MyRentals; 