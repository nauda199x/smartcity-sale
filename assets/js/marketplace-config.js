/*
 * Public browser configuration for the Vinhomes Smart City marketplace.
 * Only use a Supabase publishable key here. Never commit secret/service-role keys.
 */
window.SMARTCITY_MARKETPLACE_CONFIG = Object.freeze({
  supabaseUrl: "https://owwqrgwezuwonwdzphie.supabase.co",
  supabasePublishableKey: "sb_publishable_uE3j6lzSrCmF3WmI7dECMw_ueYv7OF1",
  storageBucket: "listing-images",
  maxImages: 12,
  maxImageBytes: 5 * 1024 * 1024,
  listingLifetimeDays: 45
});
