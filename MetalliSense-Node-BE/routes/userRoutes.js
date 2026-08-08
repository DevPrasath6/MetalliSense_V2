const express = require('express');
const authController = require('../controllers/firebaseAuthController');
const { protect, restrictTo } = require('../middleware/firebaseAuthMiddleware');
const userMetadataService = require('../services/userMetadataService');

const router = express.Router();

// ===== AUTHENTICATION ROUTES =====
// Public routes
router.post('/signup', authController.signup);
router.post('/password-reset', authController.sendPasswordResetEmail);
router.get('/health', authController.authHealthCheck);

// Protected routes
router.get('/me', protect, authController.getCurrentUser);
router.patch('/profile', protect, authController.updateProfile);
router.delete('/account', protect, authController.deleteAccount);
router.post('/verify-email', protect, authController.sendEmailVerification);

// Admin routes
router.post('/set-role', protect, restrictTo('admin'), authController.setUserRole);
router.get('/users', protect, restrictTo('admin'), authController.listUsers);

// ===== USER METADATA ROUTES (MongoDB) =====
// App-specific user data stored in MongoDB (self or admin only)
router.get('/metadata/:firebaseUserId', protect, userMetadataService.getUserMetadata);
router.patch('/metadata', protect, userMetadataService.updateUserMetadata);
router.get('/stats', protect, userMetadataService.getUserStats);

module.exports = router;
