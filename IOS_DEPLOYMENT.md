# iOS App Store Deployment Guide

This guide walks you through deploying Balance Beam Adventure to the iOS App Store using GitHub Actions.

## Prerequisites

1. **Apple Developer Account** ($99/year) - https://developer.apple.com/programs/
2. **GitHub Repository** - Push this code to GitHub
3. **Mac computer** (one-time setup for certificates)

## Step 1: Apple Developer Setup

### 1.1 Create App ID
1. Go to https://developer.apple.com/account/resources/identifiers
2. Click "+" to create new identifier
3. Select "App IDs" → "App"
4. Enter:
   - Description: `Balance Beam Adventure`
   - Bundle ID: `com.yourname.balancebeamadventure` (explicit)
5. Click "Register"

### 1.2 Create Distribution Certificate
1. On your Mac, open **Keychain Access**
2. Go to Keychain Access → Certificate Assistant → Request a Certificate from a Certificate Authority
3. Enter your email, select "Saved to disk", click Continue
4. Go to https://developer.apple.com/account/resources/certificates
5. Click "+" → Select "Apple Distribution" → Continue
6. Upload the certificate request file
7. Download the certificate and double-click to install

### 1.3 Export Certificate as .p12
1. Open Keychain Access
2. Find your "Apple Distribution" certificate
3. Right-click → Export
4. Save as .p12 file with a password
5. **Keep this password safe - you'll need it for GitHub secrets**

### 1.4 Create Provisioning Profile
1. Go to https://developer.apple.com/account/resources/profiles
2. Click "+" → Select "App Store" → Continue
3. Select your App ID → Continue
4. Select your Distribution Certificate → Continue
5. Name it: `BalanceBeamAdventure_AppStore`
6. Download the .mobileprovision file

### 1.5 Create App Store Connect API Key
1. Go to https://appstoreconnect.apple.com/access/api
2. Click "+" to create new key
3. Name: `GitHub Actions`
4. Access: `App Manager`
5. Download the .p8 file (you can only download once!)
6. Note the **Key ID** and **Issuer ID**

## Step 2: Create App in App Store Connect

1. Go to https://appstoreconnect.apple.com/apps
2. Click "+" → "New App"
3. Fill in:
   - Platform: iOS
   - Name: Balance Beam Adventure
   - Primary Language: English
   - Bundle ID: Select your App ID
   - SKU: `balancebeamadventure001`
4. Click "Create"

## Step 3: GitHub Secrets Setup

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:

| Secret Name | Value |
|-------------|-------|
| `BUILD_CERTIFICATE_BASE64` | Base64-encoded .p12 certificate (see below) |
| `P12_PASSWORD` | Password you set when exporting .p12 |
| `KEYCHAIN_PASSWORD` | Any random password (e.g., `temp123`) |
| `PROVISIONING_PROFILE_BASE64` | Base64-encoded .mobileprovision (see below) |
| `CODE_SIGN_IDENTITY` | `Apple Distribution: Your Name (TEAM_ID)` |
| `DEVELOPMENT_TEAM` | Your 10-character Team ID |
| `APP_STORE_CONNECT_API_KEY` | Contents of your .p8 file |
| `APP_STORE_CONNECT_KEY_ID` | Key ID from App Store Connect |
| `APP_STORE_CONNECT_ISSUER_ID` | Issuer ID from App Store Connect |

### How to Base64 encode files:

**On Mac/Linux:**
```bash
base64 -i your_certificate.p12 | pbcopy  # Copies to clipboard
base64 -i your_profile.mobileprovision | pbcopy
```

**On Windows (PowerShell):**
```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("your_certificate.p12")) | Set-Clipboard
[Convert]::ToBase64String([IO.File]::ReadAllBytes("your_profile.mobileprovision")) | Set-Clipboard
```

### Find your Team ID:
1. Go to https://developer.apple.com/account
2. Look for "Membership Details"
3. Your Team ID is a 10-character alphanumeric code

## Step 4: Push to GitHub

```bash
cd BalanceBeamAdventure-Kivy
git init
git add .
git commit -m "Initial commit - Balance Beam Adventure"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/balance-beam-adventure.git
git push -u origin main
```

## Step 5: Trigger Build

### Automatic build:
- Push to `main` branch triggers a build
- Creating a tag like `v1.0.0` triggers build + App Store upload

### Manual build:
1. Go to GitHub → Actions → "Build iOS App"
2. Click "Run workflow"

## Step 6: Submit for Review

After the IPA is uploaded to App Store Connect:

1. Go to https://appstoreconnect.apple.com/apps
2. Select your app
3. Go to the build and fill in:
   - Screenshots (required)
   - App description
   - Keywords
   - Support URL
   - Age rating (select 4+)
4. Click "Submit for Review"

## App Store Requirements

### Screenshots needed:
- 6.7" iPhone (1290 x 2796)
- 6.5" iPhone (1284 x 2778)
- 5.5" iPhone (1242 x 2208)
- 12.9" iPad (2048 x 2732)

### App Information:
- Description (up to 4000 chars)
- Keywords (up to 100 chars)
- Support URL
- Privacy Policy URL
- Age Rating: 4+ (no objectionable content)
- Category: Games → Kids

## Troubleshooting

### Build fails with signing error:
- Verify certificate and provisioning profile match
- Check that Bundle ID matches exactly

### Upload fails:
- Ensure App Store Connect API key has correct permissions
- Verify Issuer ID and Key ID are correct

### App rejected:
- Common reasons: missing privacy policy, inappropriate content rating
- Apple usually provides specific feedback

## Cost Summary

| Item | Cost |
|------|------|
| Apple Developer Program | $99/year |
| GitHub Actions | Free (2,000 mins/month for public repos) |
| **Total** | **$99/year** |
