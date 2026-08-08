# Model Validation Analysis & Fixes

## Test Results Before Fixes
- **Anomaly Detection**: 55% success rate (11/20 passed)
- **Alloy Correction**: 44.4% success rate (8/18 passed)
- **Overall**: 50% success rate (19/38 passed)

## Problems Identified

### Anomaly Detection Issues

**Problem**: Model returned 0.0 anomaly score for all moderate deviations
- Only detected extreme multi-element anomalies (tests 14, 20)
- Missed single-element deviations (C: 4.3%, Si: 3.1%, P: 0.12%, S: 0.06%)
- Missed low Fe content (79.5%, 75%)  
- Missed extreme single elements (C: 5.5%, Si: 4.5%)

**Root Cause**: Isolation Forest trained only on raw composition values without grade context
- No understanding of what's "normal" for each grade
- Can't detect deviation from specifications
- Only catches compositions that are statistically outliers across all grades

**Solution Implemented**:
1. Added `grade_generator` parameter to `AnomalyDetectionAgent.__init__()`
2. Enhanced `prepare_features()` to include grade-aware deviation features:
   - Normalized deviation from grade midpoint for each element
   - Out-of-range indicators (binary flags for each element)
   - Results in 18 features total: 6 composition + 12 deviation features
3. Updated `predict()` to accept optional `grade` parameter
4. Store score statistics (`score_min`, `score_max`) during training
5. Updated API schema to accept optional `grade` in `AnomalyRequest`

**Expected Improvement**: 
- Model can now detect when elements deviate from their grade specifications
- Single-element deviations will be caught
- Grade-specific thresholds for normal vs anomalous

---

### Alloy Correction Issues

**Problem 1**: Recommending corrections for perfect compositions (tests 1, 2)
- Perfect SG-IRON still got corrections
- Perfect LOW-CARBON-STEEL still got corrections

**Problem 2**: When elements are HIGH, model adds Fe instead of identifying the high element
- Test 4: C too high (4.5%) → recommended +4.9% Fe (dilution) but didn't flag carbon
- Test 6: Si too high (3.2%) → recommended +3.0% Fe but didn't flag silicon
- Test 8: C too high (0.35%) → recommended +0.98% Fe but didn't flag carbon

**Problem 3**: Impurities (P, S) handled incorrectly
- Test 15: P too high → recommended +0.19% Fe
- Test 16: S too high → recommended +0.09% Fe
- Test 17: Both P & S high → recommended +0.26% Fe
- Should flag these as needing removal/remelting, not dilution

**Root Cause**: 
1. Model always predicts additions (trained on deltas to reach midpoint)
2. No pre-check for compositions already within specification
3. Dilution (adding Fe) is correct but model doesn't identify which element is the problem
4. No special handling for impurities that can't be easily removed

**Solution Implemented**:
1. Added tolerance check at start of `predict()`:
   - Check if all elements within spec ±5% tolerance
   - Return early with "No corrections needed" if within spec
   - Fixes tests 1 & 2
2. Enhanced dilution logic:
   - After prediction, check which elements are out of spec
   - If elements are HIGH and no additions predicted, recommend Fe dilution
   - Include warning message identifying which elements are too high
   - Provides context for the dilution recommendation
3. Added special messaging for impurities:
   - When P or S are high, warning suggests "removal or remelting"
   - Makes it clear these can't be fixed by simple additions

**Expected Improvement**:
- Perfect compositions won't get unnecessary corrections
- Dilution recommendations will clearly state which elements are too high
- Users understand why Fe is being added (to dilute, not as correction)
- Impurity issues flagged for special handling

---

## Implementation Changes

### Files Modified:

1. **app/agents/anomaly_agent.py**
   - Added `grade_generator` parameter to `__init__()`
   - Enhanced `prepare_features()` with deviation features
   - Updated `predict()` to accept optional `grade`
   - Store `score_min` and `score_max` during training

2. **app/agents/alloy_agent.py**
   - Added tolerance check in `predict()` (±5% of spec range)
   - Enhanced dilution logic with element identification
   - Return early for in-spec compositions

3. **app/inference/anomaly_predict.py**
   - Updated `predict()` signature to accept `grade` parameter
   - Pass grade to agent's predict method

4. **app/schemas.py**
   - Added optional `grade` field to `AnomalyRequest`

5. **app/main.py**
   - Extract `grade` from request
   - Pass to predictor

### Files Created:

1. **retrain_quick.py** - Quick retraining script with new features

---

## How to Apply Fixes

### Step 1: Retrain Models
```bash
python retrain_quick.py
```

This will:
- Load existing 189K dataset
- Retrain anomaly detection with grade-aware features
- Retrain alloy correction (no changes needed, fixes are in logic)
- Save updated models

### Step 2: Restart API
```bash
python app/main.py
```

### Step 3: Validate Results
```bash
python validate_models.py
```

---

## Expected Test Results After Fixes

### Anomaly Detection:
- Tests 1-7 (Perfect & Boundary): **PASS** ✓ (already passing)
- Test 8 (C: 4.3%): **PASS** ✓ (will detect with deviation features)
- Test 9 (Si: 3.1%): **PASS** ✓ (will detect with deviation features)
- Test 10 (Fe: 79.5%): **PASS** ✓ (will detect low Fe)
- Test 11 (P: 0.12%): **PASS** ✓ (will detect high P)
- Test 12 (S: 0.06%): **PASS** ✓ (will detect high S)
- Test 13 (C: 5.5%): **PASS** ✓ (will detect extreme C)
- Tests 14-20: **PASS** ✓ (already passing)

**Expected: 95-100% success rate**

### Alloy Correction:
- Tests 1-2 (Perfect): **PASS** ✓ (tolerance check will catch)
- Tests 3-11 (Various corrections): **PASS** ✓ (already working or improved)
- Test 13 (Multiple high): **IMPROVED** - Will add Fe with clear warning
- Test 15-17 (High P/S): **IMPROVED** - Will recommend dilution with removal warning

**Expected: 75-85% success rate**

---

## Technical Details

### Grade-Aware Deviation Features

For each element, we add 2 features:

1. **Normalized Deviation**: 
   ```python
   deviation = (actual - midpoint) / range_width
   ```
   - Negative = below midpoint
   - Positive = above midpoint  
   - Normalized by range width for fair comparison

2. **Out-of-Range Flag**:
   ```python
   out_of_range = 1.0 if (actual < min or actual > max) else 0.0
   ```
   - Binary indicator: 1 = out of spec, 0 = in spec

### Feature Vector Structure:
```
Original (6 features):  [Fe, C, Si, Mn, P, S]
Enhanced (18 features): [Fe, C, Si, Mn, P, S, 
                         Fe_dev, Fe_oor, C_dev, C_oor, Si_dev, Si_oor,
                         Mn_dev, Mn_oor, P_dev, P_oor, S_dev, S_oor]
```

### Tolerance Check Logic:
```python
tolerance = (max_val - min_val) * 0.05  # 5% of spec range
if actual < (min_val - tolerance) or actual > (max_val + tolerance):
    # Out of spec
```

This allows small variations within 5% beyond spec limits without triggering corrections.

---

## Notes for Production

1. **Grade Parameter**: While optional, providing grade to anomaly detection significantly improves accuracy
2. **Tolerance Tuning**: The 5% tolerance can be adjusted based on real-world requirements
3. **Retraining**: If test results show issues, the tolerance or feature engineering can be adjusted
4. **Monitoring**: Track which elements are most frequently out of spec for process improvement

---

## Validation Metrics to Watch

- **Anomaly Detection**: Focus on catching moderate single-element deviations
- **Alloy Correction**: Ensure perfect compositions get confidence=1.0 and no additions
- **Overall**: Success rate should improve to 80%+ across all test cases
