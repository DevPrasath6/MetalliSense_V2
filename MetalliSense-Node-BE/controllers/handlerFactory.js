const catchAsync = require('../utils/catchAsync');
const AppError = require('../utils/AppError');

// Strip fields clients should never be able to set directly (Mongo-managed IDs,
// version keys, or model-specific fields passed in via `restrictedFields`)
const sanitizeBody = (body, restrictedFields = []) => {
  const clean = { ...body };
  delete clean._id;
  delete clean.__v;
  restrictedFields.forEach((field) => delete clean[field]);
  return clean;
};

exports.deleteOne = (Model) =>
  catchAsync(async (req, res, next) => {
    const doc = await Model.findByIdAndDelete(req.params.id);

    if (!doc) {
      return next(new AppError('No document found with that ID', 404));
    }

    res.status(204).json({
      status: 'success',
      data: null,
    });
  });

exports.updateOne = (Model, restrictedFields = []) =>
  catchAsync(async (req, res, next) => {
    const doc = await Model.findByIdAndUpdate(
      req.params.id,
      sanitizeBody(req.body, restrictedFields),
      {
        new: true,
        runValidators: true,
      },
    );

    if (!doc) {
      return next(new AppError('No document found with that ID', 404));
    }

    res.status(200).json({
      status: 'success',
      data: {
        data: doc,
      },
    });
  });

exports.createOne = (Model, restrictedFields = []) =>
  catchAsync(async (req, res, next) => {
    const doc = await Model.create(sanitizeBody(req.body, restrictedFields));

    res.status(201).json({
      status: 'success',
      data: {
        data: doc,
      },
    });
  });

exports.getOne = (Model, popOptions) =>
  catchAsync(async (req, res, next) => {
    let query = Model.findById(req.params.id);
    if (popOptions) query = query.populate(popOptions);
    const doc = await query;

    if (!doc) {
      return next(new AppError('No document found with that ID', 404));
    }

    res.status(200).json({
      status: 'success',
      data: {
        data: doc,
      },
    });
  });

exports.getAll = (Model) =>
  catchAsync(async (req, res, next) => {
    const doc = await Model.find();

    // SEND RESPONSE
    res.status(200).json({
      status: 'success',
      results: doc.length,
      data: {
        data: doc,
      },
    });
  });
