const UserMetadata = require('../models/userModel');
const catchAsync = require('../utils/catchAsync');
const AppError = require('../utils/AppError');

// Sync or create user metadata in MongoDB after Firebase authentication
exports.syncUserMetadata = async (firebaseUser, additionalData = {}) => {
  try {
    // Find or create user metadata
    let userMetadata = await UserMetadata.findOne({
      firebaseUserId: firebaseUser.id,
    });

    if (!userMetadata) {
      // Create new metadata entry
      userMetadata = await UserMetadata.create({
        firebaseUserId: firebaseUser.id,
        email: firebaseUser.email,
        name: firebaseUser.name,
        role: additionalData.role || 'user',
        preferences: additionalData.preferences || {},
        department: additionalData.department,
        employeeId: additionalData.employeeId,
      });

      console.log(`✓ Created metadata for user: ${firebaseUser.id}`);
    } else {
      // Update last active
      userMetadata.lastActive = Date.now();
      await userMetadata.save();
    }

    return userMetadata;
  } catch (error) {
    console.error('Error syncing user metadata:', error);
    return null;
  }
};

// Get user metadata by Firebase user ID (self or admin only)
exports.getUserMetadata = catchAsync(async (req, res, next) => {
  const { firebaseUserId } = req.params;

  if (req.user.uid !== firebaseUserId && req.user.role !== 'admin') {
    return next(
      new AppError('You do not have permission to view this user\'s metadata', 403),
    );
  }

  const metadata = await UserMetadata.findOne({ firebaseUserId });

  if (!metadata) {
    return res.status(404).json({
      status: 'fail',
      message: 'User metadata not found',
    });
  }

  res.status(200).json({
    status: 'success',
    data: metadata,
  });
});

// Update user metadata
exports.updateUserMetadata = catchAsync(async (req, res, next) => {
  const firebaseUserId = req.user.uid;
  const updates = req.body;

  // Users may only update their own preferences/profile fields - role is
  // privileged and must only ever be changed via the admin-only setUserRole flow
  delete updates.firebaseUserId;
  delete updates.email;
  delete updates.role;
  delete updates._id;

  const metadata = await UserMetadata.findOneAndUpdate(
    { firebaseUserId },
    { ...updates, lastActive: Date.now() },
    { new: true, upsert: true, setDefaultsOnInsert: true },
  );

  res.status(200).json({
    status: 'success',
    data: metadata,
  });
});

// Get user stats
exports.getUserStats = catchAsync(async (req, res, next) => {
  const firebaseUserId = req.user.uid;

  const metadata = await UserMetadata.findOne({ firebaseUserId });

  if (!metadata) {
    return res.status(404).json({
      status: 'fail',
      message: 'User metadata not found',
    });
  }

  res.status(200).json({
    status: 'success',
    data: {
      role: metadata.role,
      department: metadata.department,
      lastActive: metadata.lastActive,
      preferences: metadata.preferences,
    },
  });
});
