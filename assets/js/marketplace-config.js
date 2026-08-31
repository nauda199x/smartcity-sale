/*
 * Public browser configuration for the Vinhomes Smart City marketplace.
 * Only use a Supabase publishable key here. Never commit secret/service-role keys.
 */
window.SMARTCITY_MARKETPLACE_CONFIG = Object.freeze({
  supabaseUrl: "https://YOUR_PROJECT.supabase.co",
  supabasePublishableKey: "YOUR_PUBLISHABLE_KEY",
  storageBucket: "listing-images",
  maxImages: 12,
  maxImageBytes: 5 * 1024 * 1024,
  listingLifetimeDays: 45
});
