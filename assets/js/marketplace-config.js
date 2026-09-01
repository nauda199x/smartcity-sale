/*
 * Public browser configuration for the Vinhomes Smart City marketplace.
 * Only use a Supabase publishable key here. Never commit secret/service-role keys.
 */
window.SMARTCITY_MARKETPLACE_CONFIG = Object.freeze({
  supabaseUrl: "https://owwqrgwezuwonwdzphie.supabase.co",
  supabasePublishableKey: "sb_publishable_uE3j6lzSrCmF3WmI7dECMw_ueYv7OF1",\n  // Legacy anon key retained as a public PostgREST compatibility key. It is RLS-limited.\n  supabaseAnonKey: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im93d3FyZ3dlenV3b253ZHpwaGllIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODgxNDUyMTcsImV4cCI6MjEwMzcyMTIxN30.F8OA1tRSN2fv-Alpbe3PHZDE6mvUuU4WU2wkFIBD04Q",
  storageBucket: "listing-images",
  maxImages: 12,
  maxImageBytes: 5 * 1024 * 1024,
  listingLifetimeDays: 45
});
