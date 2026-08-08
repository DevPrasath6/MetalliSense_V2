const express = require('express');
const metalGradeController = require('../controllers/metalGradeController');
const {
  protect,
  optionalAuth,
} = require('../middleware/firebaseAuthMiddleware');

const router = express.Router();

router.get('/names', optionalAuth, metalGradeController.getGradeNames);
router.post('/by-name', optionalAuth, metalGradeController.getMetalGradeByName);
router.post('/elements', optionalAuth, metalGradeController.getGradeElements);
router.post(
  '/composition-ranges',
  optionalAuth,
  metalGradeController.getCompositionRanges,
);
router.post(
  '/check-specs',
  optionalAuth,
  metalGradeController.checkCompositionSpecs,
);

router
  .route('/')
  .get(optionalAuth, metalGradeController.getAllMetalGrades) // Public read
  .post(protect, metalGradeController.createMetalGrade); // Requires auth

router
  .route('/:id')
  .get(optionalAuth, metalGradeController.getMetalGrade) // Public read
  .patch(protect, metalGradeController.updateMetalGrade) // Requires auth
  .delete(protect, metalGradeController.deleteMetalGrade); // Requires auth

module.exports = router;
