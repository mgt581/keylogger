Partner phone test instructions

This is a minimal onboarding flow for a partner phone.

1. Open the onboarding link in the phone browser.
   - Example: `https://<your-ngrok-url>/onboard`

2. Enter the following values:
   - `Owner UID`: the Firebase user ID that should own this device.
   - `Device ID`: a unique string like `partner-phone-01`.
   - `Custom Token`: the token obtained from the admin backend.

3. Tap "Save onboarding info".
   - This stores the values in the browser's local storage.
   - It does not complete Firebase sign-in by itself.

4. The next step requires a mobile app or script to use the custom token.
   - The phone must sign in with Firebase using the token.
   - After sign-in, the app should create or update `devices/{deviceId}`.

5. Dashboard check:
   - Open Firebase Console → Firestore → `devices` collection.
   - Confirm `partner-phone-01` appears with `owner` equal to the entered UID.
   - Check `devices/{deviceId}/logs` for any logs from the client.

Important:
- Do not proceed without informed consent from the device owner.
- This repo only provides the backend and onboarding helper page, not a full phone app.
