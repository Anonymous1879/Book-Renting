import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import {
    AppBar,
    Toolbar,
    Typography,
    Container,
    Button,
    Box,
    Avatar,
    Menu,
    MenuItem,
    IconButton
} from '@mui/material';
import BookList from './components/BookList';
import MyRentals from './components/MyRentals';
import Login from './components/Login';
import Register from './components/Register';
import Home from './components/Home';
import MyBooks from './components/MyBooks';
import { getCurrentUser, logout } from './services/auth';
import MenuBookIcon from '@mui/icons-material/MenuBook';

const ProtectedRoute = ({ children }) => {
    const user = getCurrentUser();
    if (!user) {
        return <Navigate to="/login" />;
    }
    return children;
};

function App() {
    const [user, setUser] = useState(getCurrentUser());
    const [anchorEl, setAnchorEl] = useState(null);

    const handleLogout = async () => {
        await logout();
        setUser(null);
        setAnchorEl(null);
    };

    const handleMenuClick = (event) => {
        setAnchorEl(event.currentTarget);
    };

    const handleMenuClose = () => {
        setAnchorEl(null);
    };

    return (
        <Router>
            <div>
                <AppBar position="static">
                    <Toolbar>
                        <IconButton
                            component={Link}
                            to="/"
                            color="inherit"
                            edge="start"
                            sx={{ mr: 2 }}
                        >
                            <MenuBookIcon />
                        </IconButton>
                        <Typography variant="h6" component={Link} to="/" sx={{ 
                            flexGrow: 1, 
                            textDecoration: 'none', 
                            color: 'inherit' 
                        }}>
                            Book Rental System
                        </Typography>
                        
                        {user ? (
                            <>
                                <Button color="inherit" component={Link} to="/books">
                                    Browse Books
                                </Button>
                                <Button color="inherit" component={Link} to="/my-books">
                                    My Books
                                </Button>
                                <Button color="inherit" component={Link} to="/my-rentals">
                                    My Rentals
                                </Button>
                                <Box sx={{ ml: 2 }}>
                                    <Avatar
                                        onClick={handleMenuClick}
                                        sx={{ cursor: 'pointer' }}
                                    >
                                        {user.username[0].toUpperCase()}
                                    </Avatar>
                                    <Menu
                                        anchorEl={anchorEl}
                                        open={Boolean(anchorEl)}
                                        onClose={handleMenuClose}
                                    >
                                        <MenuItem component={Link} to="/profile">
                                            Profile
                                        </MenuItem>
                                        <MenuItem onClick={handleLogout}>
                                            Logout
                                        </MenuItem>
                                    </Menu>
                                </Box>
                            </>
                        ) : (
                            <>
                                <Button color="inherit" component={Link} to="/login">
                                    Login
                                </Button>
                                <Button color="inherit" component={Link} to="/register">
                                    Register
                                </Button>
                            </>
                        )}
                    </Toolbar>
                </AppBar>

                <Container sx={{ mt: 4 }}>
                    <Routes>
                        <Route path="/" element={<Home />} />
                        <Route path="/login" element={<Login />} />
                        <Route path="/register" element={<Register />} />
                        <Route
                            path="/books"
                            element={
                                <ProtectedRoute>
                                    <BookList />
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/my-books"
                            element={
                                <ProtectedRoute>
                                    <MyBooks />
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/my-rentals"
                            element={
                                <ProtectedRoute>
                                    <MyRentals />
                                </ProtectedRoute>
                            }
                        />
                    </Routes>
                </Container>
            </div>
        </Router>
    );
}

export default App;
