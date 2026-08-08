// Seeds the 15 real ASTM/AISI foundry grade specifications (utils/seedGradeData.js)
// into both grade collections the app reads from: GradeSpec (used by /api/v2/grades)
// and MetalGradeSpec (used by the spectrometer simulator's opc-reading flow).
// Safe to re-run - each grade is upserted by name, not blindly inserted.
const fs = require('fs');
const mongoose = require('mongoose');
const dotenv = require('dotenv');

if (fs.existsSync('./config.env')) {
  dotenv.config({ path: './config.env' });
} else {
  dotenv.config({ path: './.env' });
}

const GradeSpec = require('../models/gradeSpecModel');
const MetalGradeSpec = require('../models/metalGradeModel');
const GRADES = require('./seedGradeData');

const localDb = process.env.DATABASE_LOCAL || 'mongodb://127.0.0.1:27017/MetalliSense';
const cloudDb = process.env.DATABASE_PASSWORD && process.env.DATABASE
  ? process.env.DATABASE.replace('<PASSWORD>', process.env.DATABASE_PASSWORD)
  : process.env.DATABASE;

const connect = async () => {
  // SEED_TARGET=cloud forces seeding the Atlas cluster directly, bypassing
  // a local MongoDB instance that would otherwise be tried first (and
  // succeed silently, leaving the deployed app's database untouched).
  if (process.env.SEED_TARGET !== 'cloud') {
    try {
      await mongoose.connect(localDb, { serverSelectionTimeoutMS: 2000 });
      console.log('Connected to Local MongoDB');
      return;
    } catch (err) {
      console.warn('Local DB unavailable, trying Cloud MongoDB...', err.message);
    }
  }

  if (!cloudDb) {
    throw new Error('No DATABASE/DATABASE_PASSWORD configured - cannot connect to Cloud MongoDB');
  }
  await mongoose.connect(cloudDb, { serverSelectionTimeoutMS: 10000 });
  console.log('Connected to Cloud MongoDB');
};

const seed = async () => {
  let gradeSpecCount = 0;
  let metalGradeCount = 0;

  for (const g of GRADES) {
    await GradeSpec.findOneAndUpdate(
      { grade: g.grade },
      {
        grade: g.grade,
        description: g.description,
        standard: g.standard,
        composition_ranges: g.composition_ranges,
        physical_properties: g.physical_properties,
        typical_applications: g.typical_applications,
      },
      { upsert: true, new: true, runValidators: true, setDefaultsOnInsert: true },
    );
    gradeSpecCount += 1;

    await MetalGradeSpec.findOneAndUpdate(
      { metal_grade: g.grade },
      { metal_grade: g.grade, composition_range: g.composition_ranges },
      { upsert: true, new: true, runValidators: true, setDefaultsOnInsert: true },
    );
    metalGradeCount += 1;
  }

  console.log(`Seeded ${gradeSpecCount} grade specifications (GradeSpec collection)`);
  console.log(`Seeded ${metalGradeCount} metal grade specifications (MetalGradeSpec collection)`);
};

(async () => {
  try {
    await connect();
    await seed();
    console.log('Database seeding complete.');
  } catch (err) {
    console.error('Seeding failed:', err.message);
    process.exitCode = 1;
  } finally {
    await mongoose.disconnect();
  }
})();
