const GradeSpec = require('../models/gradeSpecModel');
const factory = require('./handlerFactory');
const catchAsync = require('../utils/catchAsync');
const AppError = require('../utils/AppError');

const datasetGrades = [
  {
    grade: 'SG-IRON',
    description: 'Spheroidal Graphite Cast Iron (Ductile Iron)',
    standard: 'ASTM A536',
    composition_ranges: {
      Fe: [82.0, 90.0],
      C: [3.0, 4.0],
      Si: [1.8, 2.8],
      Mn: [0.3, 1.0],
      P: [0.01, 0.08],
      S: [0.01, 0.03],
    },
    physical_properties: {
      tensile_strength_mpa: [450, 600],
      yield_strength_mpa: [310, 420],
      elongation_percent: [10, 18],
    },
    typical_applications: ['Automotive Crankshafts', 'Hydraulic Cylinders', 'Heavy Machinery Gearboxes'],
  },
  {
    grade: 'GREY-IRON',
    description: 'Grey Cast Iron (General Purpose)',
    standard: 'ASTM A48',
    composition_ranges: {
      Fe: [85.0, 92.0],
      C: [2.5, 3.8],
      Si: [1.0, 2.5],
      Mn: [0.4, 1.2],
      P: [0.02, 0.15],
      S: [0.02, 0.12],
    },
    physical_properties: {
      tensile_strength_mpa: [150, 350],
      yield_strength_mpa: [100, 250],
      elongation_percent: [0.5, 2.0],
    },
    typical_applications: ['Engine Blocks', 'Brake Drums', 'Machine Tool Bases', 'Pipes'],
  },
  {
    grade: 'LOW-CARBON-STEEL',
    description: 'Mild Steel (Carbon < 0.3%)',
    standard: 'AISI 1018 / ASTM A36',
    composition_ranges: {
      Fe: [98.0, 99.5],
      C: [0.05, 0.25],
      Si: [0.1, 0.5],
      Mn: [0.3, 0.9],
      P: [0.01, 0.04],
      S: [0.01, 0.05],
    },
    physical_properties: {
      tensile_strength_mpa: [400, 550],
      yield_strength_mpa: [250, 350],
      elongation_percent: [20, 30],
    },
    typical_applications: ['Structural Shapes', 'Automotive Body Panels', 'Nails & Wire'],
  },
  {
    grade: 'MEDIUM-CARBON-STEEL',
    description: 'Medium Carbon Steel (0.3 - 0.6% C)',
    standard: 'AISI 1045 / ASTM A29',
    composition_ranges: {
      Fe: [97.5, 99.0],
      C: [0.3, 0.6],
      Si: [0.15, 0.6],
      Mn: [0.5, 1.5],
      P: [0.01, 0.04],
      S: [0.01, 0.05],
    },
    physical_properties: {
      tensile_strength_mpa: [550, 750],
      yield_strength_mpa: [350, 500],
      elongation_percent: [15, 25],
    },
    typical_applications: ['Axles', 'Gears', 'Bolts', 'Forgings'],
  },
  {
    grade: 'HIGH-CARBON-STEEL',
    description: 'High Carbon Steel (0.6 - 1.4% C)',
    standard: 'AISI 1080 / ASTM A29',
    composition_ranges: {
      Fe: [97.0, 98.5],
      C: [0.6, 1.4],
      Si: [0.2, 0.8],
      Mn: [0.6, 1.8],
      P: [0.01, 0.04],
      S: [0.01, 0.05],
    },
    physical_properties: {
      tensile_strength_mpa: [650, 980],
      yield_strength_mpa: [380, 600],
      elongation_percent: [8, 15],
    },
    typical_applications: ['High-Strength Springs', 'Cutting Blades', 'Railroad Track Fasteners'],
  },
];

// Standard CRUD operations - pure read, no side effects
exports.getAllGrades = catchAsync(async (req, res, next) => {
  const doc = await GradeSpec.find();

  res.status(200).json({
    status: 'success',
    results: doc.length,
    data: {
      data: doc,
    },
  });
});

// Admin-only: reset grade specs back to the hardcoded dataset defaults,
// removing any custom entries. Previously this ran on every GET /grades call,
// which meant an unauthenticated read wiped out user-created grade specs.
exports.resetGradesToDataset = catchAsync(async (req, res, next) => {
  const datasetGradeNames = datasetGrades.map((g) => g.grade);

  await GradeSpec.deleteMany({ grade: { $nin: datasetGradeNames } });
  for (const item of datasetGrades) {
    await GradeSpec.updateOne(
      { grade: item.grade },
      { $set: item },
      { upsert: true }
    );
  }

  const MetalGradeSpec = require('../models/metalGradeModel');
  await MetalGradeSpec.deleteMany({ metal_grade: { $nin: datasetGradeNames } });
  for (const item of datasetGrades) {
    await MetalGradeSpec.updateOne(
      { metal_grade: item.grade },
      {
        $set: {
          metal_grade: item.grade,
          composition_range: new Map(Object.entries(item.composition_ranges)),
        },
      },
      { upsert: true }
    );
  }

  const doc = await GradeSpec.find();

  res.status(200).json({
    status: 'success',
    results: doc.length,
    data: {
      data: doc,
    },
  });
});

exports.getGrade = factory.getOne(GradeSpec);
exports.createGrade = factory.createOne(GradeSpec);
exports.updateGrade = factory.updateOne(GradeSpec);
exports.deleteGrade = factory.deleteOne(GradeSpec);

// Get grade by name (alternative to ID)
exports.getGradeByName = catchAsync(async (req, res, next) => {
  const { gradeName } = req.params;
  const grade = await GradeSpec.findOne({
    grade: gradeName.toUpperCase(),
  });

  if (!grade) {
    return next(new AppError(`Grade '${gradeName}' not found`, 404));
  }

  res.status(200).json({
    status: 'success',
    data: { grade },
  });
});

// Get composition ranges for a specific grade
exports.getCompositionRanges = catchAsync(async (req, res, next) => {
  const { gradeName } = req.params;
  const grade = await GradeSpec.findOne({
    grade: gradeName.toUpperCase(),
  });

  if (!grade) {
    return next(new AppError(`Grade '${gradeName}' not found`, 404));
  }

  res.status(200).json({
    status: 'success',
    data: {
      grade: grade.grade,
      composition_ranges: grade.composition_ranges,
    },
  });
});
