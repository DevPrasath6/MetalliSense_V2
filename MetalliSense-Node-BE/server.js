
const mongoose = require('mongoose');
const dotenv = require('dotenv');

process.on('uncaughtException', (err) => {
  console.log('UNCAUGHT EXCEPTION! 💥');
  console.log('Error name:', err.name);
  console.log('Error message:', err.message);
  console.log('Stack trace:');
  console.log(err.stack);

  console.log('💥 Critical error - shutting down server...');
  process.exit(1);
});

const fs = require('fs');
if (fs.existsSync('./config.env')) {
  dotenv.config({ path: './config.env' });
} else {
  dotenv.config({ path: './.env' });
}

const app = require('./app');
const opcuaService = require('./services/opcuaService');
const { initializeFirebase } = require('./config/firebase');

// Initialize Firebase Admin
try {
  initializeFirebase();
} catch (error) {
  console.error('Failed to initialize Firebase:', error.message);
  console.log('⚠️  Server will continue without Firebase authentication');
}

const localDb = process.env.DATABASE_LOCAL || 'mongodb://127.0.0.1:27017/MetalliSense';
const cloudDb = process.env.DATABASE_PASSWORD && process.env.DATABASE
  ? process.env.DATABASE.replace('<PASSWORD>', process.env.DATABASE_PASSWORD)
  : process.env.DATABASE;

// Connect to local DB first for instant startup, fallback to cloud DB
mongoose.connect(localDb, { serverSelectionTimeoutMS: 2000 })
  .then(() => console.log('DB connection successful (Local MongoDB)!'))
  .catch((err) => {
    console.warn('Local DB connection failed, connecting to Cloud MongoDB...', err.message);
    if (cloudDb) {
      mongoose.connect(cloudDb, { serverSelectionTimeoutMS: 3000 })
        .then(() => console.log('DB connection successful (Cloud MongoDB)!'))
        .catch(e => console.error('Cloud DB connection error:', e.message));
    }
  });

const port = process.env.PORT || 3000;
const server = app.listen(port, async () => {
  console.log(`App running on port ${port}...`);

  // Initialize OPC UA Server only (Client connection controlled by frontend)
  console.log('Initializing OPC UA Server...');
  const opcInitialized = await opcuaService.initializeServerOnly();
  if (opcInitialized) {
    console.log('✅ OPC UA Server ready (Client connection pending)');
  } else {
    console.log('❌ OPC UA Server failed to initialize');
  }
});

process.on('unhandledRejection', (err) => {
  console.log('UNHANDLED REJECTION! 💥 Shutting down...');
  console.log(err.name, err.message);
  server.close(() => {
    // Shutdown OPC UA Service
    opcuaService.shutdown().then(() => {
      process.exit(1);
    });
  });
});

// Graceful shutdown on SIGTERM
process.on('SIGTERM', () => {
  console.log('SIGTERM received. Shutting down gracefully...');
  server.close(() => {
    opcuaService.shutdown().then(() => {
      console.log('Process terminated');
      process.exit(0);
    });
  });
});
// Trigger restart
