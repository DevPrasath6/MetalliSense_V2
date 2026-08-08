const express = require('express');
const spectrometerController = require('../controllers/spectrometerController');
const {
  protect,
  optionalAuth,
} = require('../middleware/firebaseAuthMiddleware');

const router = express.Router();

// Read-only status check (public)
router.get('/opc-status', spectrometerController.getOPCStatus);

// Controls the real OPC-UA client connection - requires auth
router.post('/opc-connect', protect, spectrometerController.connectOPCClient);
router.post(
  '/opc-disconnect',
  protect,
  spectrometerController.disconnectOPCClient,
);

// Special routes (before generic CRUD routes) - all mutate data, require auth
router.post(
  '/create-validated',
  protect,
  spectrometerController.createReadingWithValidation,
);
router.post(
  '/generate-synthetic',
  protect,
  spectrometerController.generateSyntheticReading,
);
router.post(
  '/metal-alone',
  protect,
  spectrometerController.metalAloneGeneration,
);
router.post(
  '/metal-scrap-synthetic',
  protect,
  spectrometerController.metalScrapSyntheticReading,
);

// OPC UA routes - triggers a real spectrometer read, requires auth
router.post('/opc-reading', protect, spectrometerController.requestOPCReading);

// Standard CRUD routes
router
  .route('/')
  .get(optionalAuth, spectrometerController.getAllReadings) // Public read
  .post(protect, spectrometerController.createReading); // Requires auth

router
  .route('/:id')
  .get(optionalAuth, spectrometerController.getReading) // Public read
  .patch(protect, spectrometerController.updateReading) // Requires auth
  .delete(protect, spectrometerController.deleteReading); // Requires auth

module.exports = router;
