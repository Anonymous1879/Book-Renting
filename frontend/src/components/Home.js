import React from 'react';
import {
    Container,
    Typography,
    Paper,
    Grid,
    Box,
    Card,
    CardContent,
    CardMedia,
    Button
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import LibraryBooksIcon from '@mui/icons-material/LibraryBooks';
import MonetizationOnIcon from '@mui/icons-material/MonetizationOn';
import PeopleIcon from '@mui/icons-material/People';

const Home = () => {
    const navigate = useNavigate();

    const features = [
        {
            icon: <LibraryBooksIcon sx={{ fontSize: 40 }} />,
            title: 'Extensive Book Collection',
            description: 'Access a wide variety of books from different genres shared by our community members.'
        },
        {
            icon: <MonetizationOnIcon sx={{ fontSize: 40 }} />,
            title: 'Affordable Rentals',
            description: 'Rent books at competitive prices set by book owners. Save money while enjoying great reads.'
        },
        {
            icon: <PeopleIcon sx={{ fontSize: 40 }} />,
            title: 'Community Driven',
            description: 'Join a community of book lovers. Share your collection and discover new reads from others.'
        }
    ];

    return (
        <Container>
            {/* Hero Section */}
            <Box sx={{ py: 8, textAlign: 'center' }}>
                <Typography variant="h2" component="h1" gutterBottom>
                    Welcome to Book Rental System
                </Typography>
                <Typography variant="h5" color="text.secondary" paragraph>
                    Share your books with others and discover new reads from our community.
                    Rent books at affordable prices or make money by lending your collection.
                </Typography>
                <Box sx={{ mt: 4 }}>
                    <Button
                        variant="contained"
                        size="large"
                        onClick={() => navigate('/books')}
                        sx={{ mr: 2 }}
                    >
                        Browse Books
                    </Button>
                    <Button
                        variant="outlined"
                        size="large"
                        onClick={() => navigate('/my-books')}
                    >
                        Share Your Books
                    </Button>
                </Box>
            </Box>

            {/* Features Section */}
            <Box sx={{ py: 8 }}>
                <Typography variant="h4" component="h2" gutterBottom textAlign="center">
                    How It Works
                </Typography>
                <Grid container spacing={4} sx={{ mt: 2 }}>
                    {features.map((feature, index) => (
                        <Grid item xs={12} md={4} key={index}>
                            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', p: 2 }}>
                                <Box sx={{ color: 'primary.main', my: 2 }}>
                                    {feature.icon}
                                </Box>
                                <CardContent>
                                    <Typography variant="h6" component="h3" gutterBottom textAlign="center">
                                        {feature.title}
                                    </Typography>
                                    <Typography variant="body1" color="text.secondary" textAlign="center">
                                        {feature.description}
                                    </Typography>
                                </CardContent>
                            </Card>
                        </Grid>
                    ))}
                </Grid>
            </Box>

            {/* Steps Section */}
            <Box sx={{ py: 8 }}>
                <Typography variant="h4" component="h2" gutterBottom textAlign="center">
                    Getting Started
                </Typography>
                <Paper sx={{ p: 4, mt: 4 }}>
                    <Grid container spacing={4}>
                        <Grid item xs={12} md={6}>
                            <Typography variant="h6" gutterBottom>
                                For Renters:
                            </Typography>
                            <ol>
                                <li>
                                    <Typography paragraph>
                                        Browse our collection of available books
                                    </Typography>
                                </li>
                                <li>
                                    <Typography paragraph>
                                        Select a book and check its rental price
                                    </Typography>
                                </li>
                                <li>
                                    <Typography paragraph>
                                        Request to rent for your desired duration
                                    </Typography>
                                </li>
                                <li>
                                    <Typography>
                                        Coordinate with the owner for pickup/delivery
                                    </Typography>
                                </li>
                            </ol>
                        </Grid>
                        <Grid item xs={12} md={6}>
                            <Typography variant="h6" gutterBottom>
                                For Book Owners:
                            </Typography>
                            <ol>
                                <li>
                                    <Typography paragraph>
                                        List your books with descriptions and photos
                                    </Typography>
                                </li>
                                <li>
                                    <Typography paragraph>
                                        Set your rental price and conditions
                                    </Typography>
                                </li>
                                <li>
                                    <Typography paragraph>
                                        Review and approve rental requests
                                    </Typography>
                                </li>
                                <li>
                                    <Typography>
                                        Manage your rentals and returns
                                    </Typography>
                                </li>
                            </ol>
                        </Grid>
                    </Grid>
                </Paper>
            </Box>
        </Container>
    );
};

export default Home; 