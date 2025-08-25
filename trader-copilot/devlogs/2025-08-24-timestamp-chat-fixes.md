# v0.3.2 - Timestamp & Chat Functionality Fixes

**Date:** August 24, 2025
**Status:** Completed

## Issues Resolved

### 1. Timestamp Display Bug
- **Problem:** Live Prices section showed cached timestamp (1:23 AM CT) instead of current time (6:xx AM CT)
- **Root Cause:** `PriceTicker.tsx` was looking for `snapshot.meta?.last_updated` but actual data structure uses `snapshot.intraday.meta.run_timestamp`
- **Fix:** Updated timestamp extraction logic to use correct nested paths:
  ```typescript
  const intradayTimestamp = systemCtx.snapshot?.intraday?.meta?.run_timestamp;
  const swingTimestamp = systemCtx.snapshot?.swing?.meta?.run_timestamp;
  const timestamp = intradayTimestamp || swingTimestamp;
  ```

### 2. Chat Submit Button Disabled
- **Problem:** Submit button remained disabled even after typing message text
- **Root Cause:** Breaking API changes in `@ai-sdk/react` v2.0.22 - `useChat` hook no longer returns `input`, `handleInputChange`, `handleSubmit`, or `isLoading`
- **Fix:** Implemented manual state management for chat input:
  ```typescript
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { messages, sendMessage } = useChat({ /* config */ });
  ```

## Technical Details

### Files Modified
- `src/components/PriceTicker.tsx` - Fixed timestamp field references
- `src/components/Chat.tsx` - Rewrote input handling for AI SDK v2 compatibility

### Testing Approach
- Created comprehensive Playwright test suites to validate fixes
- Debugged multiple badge elements on page (ThesisPanel: "system", PriceTicker: "0140", Chat: "o3")
- Confirmed timezone handling (Austin CDT = UTC-5)

### Verification Results
✅ Timestamp shows correct current time in Central Time
✅ Chat submit button enables/disables based on input text
✅ Hash badge displays time-based hash (e.g., "0140")
✅ Price data loads and displays correctly

## Impact
- Users now see accurate refresh timestamps
- Chat functionality fully restored
- No breaking changes to existing features
- Improved reliability of real-time data display