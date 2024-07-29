-- disable visanet payment provider
UPDATE payment_provider
   SET visanet_access_key = NULL,
       visanet_secret_key = NULL,
       visanet_profile_id = NULL;