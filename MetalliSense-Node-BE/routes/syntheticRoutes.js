const express = require('express');
const syntheticController = require('../controllers/syntheticController');
const {
  protect,
  optionalAuth,
} = require('../middleware/firebaseAuthMiddleware');

const router = express.Router();

// Read-only status check (public)
router.get('/opc-status', optionalAuth, syntheticController.getOPCStatus);

// Controls the real OPC-UA client connection / writes data - require auth
router.post('/opc-connect', protect, syntheticController.connectOPCClient);
router.post(
  '/opc-disconnect',
  protect,
  syntheticController.disconnectOPCClient,
);

// Synthetic reading generation
router.post(
  '/generate-synthetic',
  protect,
  syntheticController.generateSyntheticReading,
);

module.exports = router;
